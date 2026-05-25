import logging
import random
import threading
import time

from colonia_aurora.crew.crew import CrewMember

_log = logging.getLogger(__name__)

THREAD_JOIN_TIMEOUT = 2.0


class SimulationLoop:
    """Encapsula o tick loop da simulação com injeção formal de dependências."""

    def __init__(
        self,
        storage,
        sensor_manager,
        module_manager,
        event_manager,
        energy_manager,
        crew_manager,
        logger,
        *,
        tick_rate: float,
        spawn_prob: float,
        sol_ticks: int,
        stop_flag: threading.Event,
        pause_event: threading.Event,
    ) -> None:
        self._storage        = storage
        self._sensor_manager = sensor_manager
        self._module_manager = module_manager
        self._event_manager  = event_manager
        self._energy_manager = energy_manager
        self._crew_manager   = crew_manager
        self._logger         = logger
        self._tick_rate      = tick_rate
        self._spawn_prob     = spawn_prob
        self._sol_ticks      = sol_ticks
        self._stop_flag      = stop_flag
        self._pause_event    = pause_event
        self._thread: threading.Thread | None = None

    # ── Controle público ───────────────────────────────────────────────────────

    def start(self) -> None:
        self._thread = threading.Thread(
            target=self._run, daemon=True, name="SimLoop"
        )
        self._thread.start()

    def stop(self, timeout: float = THREAD_JOIN_TIMEOUT) -> None:
        self._stop_flag.set()
        self._pause_event.set()
        if self._thread:
            self._thread.join(timeout=timeout)
            if self._thread.is_alive():
                _log.warning(
                    "SimLoop thread ainda viva após %.1fs — possível deadlock", timeout
                )

    # ── Loop interno ───────────────────────────────────────────────────────────

    def _run(self) -> None:
        try:
            self._tick_loop()
        finally:
            self._logger.close()

    def _tick_loop(self) -> None:
        tick = 0
        while not self._stop_flag.is_set():
            tick_start = time.monotonic()
            self._pause_event.wait()
            if self._stop_flag.is_set():
                break

            tick += 1
            try:
                self._tick(tick)
            except Exception:
                _log.exception("Erro não tratado no tick %d — simulação continua", tick)

            elapsed   = time.monotonic() - tick_start
            remaining = self._tick_rate - elapsed
            if remaining > 0:
                self._stop_flag.wait(remaining)

    # ── Um tick completo, delegado por responsabilidade ────────────────────────

    def _tick(self, tick: int) -> None:
        self._publish_tick(tick)
        self._sensor_manager.do_all()
        self._event_manager.check_and_roll(
            self._module_manager, self._crew_manager, self._storage
        )
        self._storage.set("modules.count", len(self._module_manager.all_modules()))
        self._module_manager.run_all()
        self._energy_manager.calculate(self._module_manager)
        self._crew_manager.do_all()
        self._module_manager.publish_snapshot(self._storage)
        self._event_manager.publish_state(self._storage)
        self._logger.log(tick, self._storage)
        self._maybe_spawn(tick)

    def _publish_tick(self, tick: int) -> None:
        self._storage.set("tick", tick)
        # (tick - 1) garante que o tick 48 ainda seja sol 0, não sol 1
        self._storage.set("sol", (tick - 1) // self._sol_ticks)

    # ── Spawn de módulo + tripulante operador ──────────────────────────────────

    def _maybe_spawn(self, tick: int) -> None:
        if random.random() >= self._spawn_prob:
            return
        level = self._storage.get("energy.level", "NOMINAL")
        if level == "CRITICAL":
            new_mod = self._module_manager.spawn_generation()
            tag = "GERAÇÃO FORÇADA"
        else:
            new_mod = self._module_manager.spawn_from_bag()
            tag = "bag"
        if new_mod:
            self._logger.log_event(f"[Spawn {tag}] {new_mod.name}")
            self._add_crew_for_spawn(tick)

    def _add_crew_for_spawn(self, tick: int) -> None:
        # Novo módulo requer um operador: crew cresce junto com a colônia.
        self._crew_manager.add(
            CrewMember(f"Tripulante_{tick}", random.choice(CrewMember.ROLES))
        )
