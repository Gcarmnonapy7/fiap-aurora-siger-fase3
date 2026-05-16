"""AURORA CORE — interactive console for the Aurora Siger colony simulator.

Menu-driven interface that runs the simulation once and then lets the user
explore the four assignment items:
  1.1  Hierarchies (functional and criticality trees)
  1.2  Decision rules over the latest snapshot
  1.3  Wind power forecast via manual linear regression
  1.4  Energy-balance verdict + per-step log file

Uses only built-ins (`input`, `print`) — no argparse or external libraries.
"""

from colony.analysis import analyze_balance, summarize_history, write_log
from colony.constants import TOTAL_STEPS
from colony.decision import evaluate_rules
from colony.hierarchies import build_functional_tree, build_criticality_tree
from colony.prediction import fit_wind_power_model, predict
from colony.simulator import run_simulation


BANNER = """
=========================================================
   AURORA CORE — Colônia Marciana Aurora Siger
   Sistema Inteligente Integrado de Energia e Decisão
=========================================================
"""


class SessionState:
    """Configurações e resultado da última simulação rodada."""

    def __init__(self):
        self.seed: int | None = 42
        self.horizon: int = TOTAL_STEPS
        self.history: dict | None = None
        self.battery: dict | None = None

    def seed_label(self) -> str:
        return "aleatório (entropia do sistema)" if self.seed is None else str(self.seed)

    def has_simulation(self) -> bool:
        return self.history is not None


# ---------- helpers de I/O ----------

def prompt_int(message: str, default: int, minimum: int = 1) -> int:
    """Lê um inteiro do usuário; ENTER mantém o default. Repete em caso de erro."""
    while True:
        raw = input(f"{message} [{default}]: ").strip()
        if raw == "":
            return default
        try:
            value = int(raw)
            if value < minimum:
                print(f"  ! valor deve ser >= {minimum}.")
                continue
            return value
        except ValueError:
            print("  ! entrada inválida — digite um número inteiro.")


def prompt_choice(message: str, valid: set[str]) -> str:
    while True:
        raw = input(message).strip()
        if raw in valid:
            return raw
        print(f"  ! opção inválida — escolha entre {sorted(valid)}.")


NO_SIM_MSG = "\n[!] Nenhuma simulação rodada ainda — escolha a opção 1 primeiro."


# ---------- comandos do menu ----------

def cmd_run_simulation(session: SessionState) -> None:
    print(f"\nRodando simulação (seed={session.seed_label()}, horizonte={session.horizon} horas)...")
    _, battery, history = run_simulation(seed=session.seed, horizon=session.horizon)
    session.battery = battery
    session.history = history
    summary = summarize_history(history)
    print(f"[OK] {summary['total_steps']} horas simuladas.")
    print(f"     Geração média: {summary['avg_generation_kw']:.1f} kW")
    print(f"     Consumo médio: {summary['avg_consumption_kw']:.1f} kW")
    print(f"     Bateria final: {battery['current_charge_kwh']:.1f}/{battery['max_capacity_kwh']:.1f} kWh")


def cmd_configure_seed(session: SessionState) -> None:
    print("\nModo de aleatoriedade:")
    print("  [1] Determinístico (escolher seed inteira)")
    print("  [2] Aleatório (entropia do sistema, varia a cada run)")
    choice = prompt_choice("Escolha [1/2]: ", {"1", "2"})
    if choice == "1":
        session.seed = prompt_int("Seed", default=42 if session.seed is None else session.seed)
    else:
        session.seed = None
    print(f"[OK] seed = {session.seed_label()}")


def cmd_configure_horizon(session: SessionState) -> None:
    print(f"\nHorizonte atual: {session.horizon} horas ({session.horizon // 24} sóis + {session.horizon % 24}h)")
    print(f"Padrão do enunciado: {TOTAL_STEPS} horas (7 sóis × 24h)")
    session.horizon = prompt_int("Novo horizonte (em horas)", default=session.horizon)
    print(f"[OK] horizonte = {session.horizon} horas")


def cmd_show_hierarchies(session: SessionState) -> None:
    del session  # não usa estado da sessão; assinatura uniforme p/ dispatch
    print("\n--- Árvore funcional ---")
    print(build_functional_tree().pretty_print())
    print("\n--- Árvore de criticidade ---")
    print(build_criticality_tree().pretty_print())


def cmd_show_summary(session: SessionState) -> None:
    history, battery = session.history, session.battery
    if history is None or battery is None:
        print(NO_SIM_MSG)
        return
    s = summarize_history(history)
    print("\n--- Resumo numérico da simulação ---")
    print(f"  horas simuladas       : {s['total_steps']}")
    print(f"  geração média (kW)    : {s['avg_generation_kw']:.2f}")
    print(f"  geração mínima (kW)   : {s['min_generation_kw']:.2f}")
    print(f"  geração máxima (kW)   : {s['max_generation_kw']:.2f}")
    print(f"  consumo médio (kW)    : {s['avg_consumption_kw']:.2f}")
    print(f"  bateria final (kWh)   : {battery['current_charge_kwh']:.1f}")
    print(f"  horas com tempestade  : {s['storm_hours']}")
    print(f"  horas com alerta      : {s['alert_hours']}")


def cmd_decision_rules(session: SessionState) -> None:
    history = session.history
    if history is None:
        print(NO_SIM_MSG)
        return
    snapshot = {
        "energy_kw": history["total_generation_kw"][-1],
        "consumption_kw": history["total_consumption_kw"][-1],
        "storm": history["storm"][-1],
    }
    actions = evaluate_rules(snapshot)
    print("\n--- Regras de decisão (item 1.2) ---")
    print(f"  entrada: energia={snapshot['energy_kw']:.1f} kW, "
          f"consumo={snapshot['consumption_kw']:.1f} kW, "
          f"tempestade={snapshot['storm']}")
    if actions:
        for a in actions:
            print(f"  -> {a}")
    else:
        print("  -> (nenhum alerta — operação saudável)")


WIND_PRESETS = [
    ("1", "Vento fraco",          5),
    ("2", "Vento típico",         8),
    ("3", "Vento forte",         11),
    ("4", "Vento de saturação",  15),
]


def cmd_wind_prediction(session: SessionState) -> None:
    history = session.history
    if history is None:
        print(NO_SIM_MSG)
        return
    print("\n--- Previsão eólica (item 1.3) ---")
    try:
        a, b = fit_wind_power_model(history)
    except ValueError as e:
        print(f"  ! previsão indisponível: {e}")
        return
    sign = "+" if b >= 0 else "-"
    print(f"Reta ajustada: y = {a:.3f}·v {sign} {abs(b):.3f}\n")

    print("Escolha o cenário de vento:")
    for key, label, value in WIND_PRESETS:
        print(f"  [{key}] {label:<20} (v = {value} m/s)")
    print("  [5] Digitar valor customizado")

    valid = {k for k, _, _ in WIND_PRESETS} | {"5"}
    choice = prompt_choice("Escolha: ", valid)
    if choice == "5":
        wind = prompt_int("Vento (m/s)", default=11, minimum=0)
    else:
        wind = next(v for k, _, v in WIND_PRESETS if k == choice)

    forecast = max(0.0, predict(a, b, wind))
    print(f"  -> v = {wind} m/s -> energia eólica prevista = {forecast:.1f} kW")


def cmd_balance_analysis(session: SessionState) -> None:
    history = session.history
    if history is None:
        print(NO_SIM_MSG)
        return
    print("\n--- Análise de balanço energético (item 1.4) ---")
    s = summarize_history(history)
    avg = analyze_balance(s["avg_generation_kw"], s["avg_consumption_kw"])
    last = analyze_balance(
        history["total_generation_kw"][-1],
        history["total_consumption_kw"][-1],
    )
    print(f"  média do período  : delta={avg['delta_kw']:+.1f} kW | {avg['status']:<8} | {avg['message']}")
    print(f"  último passo      : delta={last['delta_kw']:+.1f} kW | {last['status']:<8} | {last['message']}")


def cmd_save_log(session: SessionState) -> None:
    history = session.history
    if history is None:
        print(NO_SIM_MSG)
        return
    default_path = "data/colony_log.txt"
    raw = input(f"\nCaminho do arquivo de log [{default_path}]: ").strip()
    path = raw or default_path
    try:
        write_log(history, path)
    except OSError as e:
        print(f"  ! erro ao escrever {path}: {e}")
        return
    print(f"[OK] log gravado em {path} ({len(history['total_generation_kw'])} horas).")


# ---------- loop principal ----------

MENU = [
    ("1", "Rodar simulação", cmd_run_simulation),
    ("2", "Configurar seed (determinístico/aleatório)", cmd_configure_seed),
    ("3", "Configurar horizonte (em horas)", cmd_configure_horizon),
    ("4", "Mostrar hierarquias da colônia (item 1.1)", cmd_show_hierarchies),
    ("5", "Resumo numérico da simulação", cmd_show_summary),
    ("6", "Regras de decisão (item 1.2)", cmd_decision_rules),
    ("7", "Previsão eólica via regressão linear (item 1.3)", cmd_wind_prediction),
    ("8", "Análise de balanço energético (item 1.4)", cmd_balance_analysis),
    ("9", "Salvar log da simulação em arquivo", cmd_save_log),
    ("0", "Sair", None),
]


def print_menu(session: SessionState) -> None:
    status = "(sem simulação ainda)" if not session.has_simulation() else f"({session.horizon} horas simuladas)"
    print()
    print("=" * 57)
    print(f"  Configuração: seed={session.seed_label()} | horizonte={session.horizon}")
    print(f"  Estado: {status}")
    print("-" * 57)
    for key, label, _ in MENU:
        print(f"  [{key}] {label}")
    print("=" * 57)


def main() -> None:
    print(BANNER)
    session = SessionState()
    dispatch = {key: cmd for key, _, cmd in MENU if cmd is not None}
    valid_keys = {key for key, _, _ in MENU}

    while True:
        print_menu(session)
        choice = prompt_choice("Escolha uma opção: ", valid_keys)
        if choice == "0":
            print("\nEncerrando AURORA CORE. Até a próxima!\n")
            return
        dispatch[choice](session)


if __name__ == "__main__":
    main()
