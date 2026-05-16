"""Entry point for the Aurora Siger colony simulator.

Runs one Martian week (168 hours by default) and prints a summary of the
history along with the new AURORA CORE outputs:

  - Hierarchies (functional and criticality trees)
  - Simulation summary (totals, averages)
  - Decision rules applied to the final snapshot (item 1.2)
  - Wind power forecast from manual linear regression (item 1.3)
  - Energy-balance verdict over the run (item 1.4)

Usage:
    python3 main.py                       # deterministic, 168 steps
    python3 main.py --random              # non-deterministic (system entropy)
    python3 main.py --seed 7              # custom seed
    python3 main.py --horizon 48          # short run (2 sols)
    python3 main.py --log-file data/log.txt
    python3 main.py --quiet               # only the final summary
"""

import argparse

from colony.analysis import analyze_balance, summarize_history, write_log
from colony.constants import TOTAL_STEPS
from colony.decision import evaluate_rules
from colony.hierarchies import build_functional_tree, build_criticality_tree
from colony.prediction import fit_wind_power_model, predict
from colony.simulator import run_simulation


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Aurora Siger colony simulator — Fase 3 (AURORA CORE).",
    )
    parser.add_argument("--seed", type=int, default=42,
                        help="random seed for reproducibility (default: 42)")
    parser.add_argument("--random", action="store_true",
                        help="use system entropy (overrides --seed)")
    parser.add_argument("--horizon", type=int, default=TOTAL_STEPS,
                        help=f"number of hourly steps to simulate (default: {TOTAL_STEPS})")
    parser.add_argument("--log-file", type=str, default=None,
                        help="optional path to dump the per-step history as text")
    parser.add_argument("--quiet", action="store_true",
                        help="only print the final summary")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    seed = None if args.random else args.seed

    if not args.quiet:
        print("Aurora Siger — Simulação de 7 sóis marcianos\n")
        print("Árvore funcional dos subsistemas:")
        print(build_functional_tree().pretty_print())
        print()
        print("Árvore de criticidade dos subsistemas:")
        print(build_criticality_tree().pretty_print())
        print()

    climate, battery, history = run_simulation(seed=seed, horizon=args.horizon)

    summary = summarize_history(history)
    print(f"Passos simulados: {summary['total_steps']}")
    print(f"Geração total média: {summary['avg_generation_kw']:.1f} kW")
    print(f"Consumo total médio: {summary['avg_consumption_kw']:.1f} kW")
    print(f"Bateria final: {battery['current_charge_kwh']:.1f} / {battery['max_capacity_kwh']:.1f} kWh")
    print(f"Passos com tempestade: {summary['storm_hours']} de {summary['total_steps']}")
    print(f"Passos com alerta: {summary['alert_hours']}")
    print()

    # Item 1.4 — Análise de balanço energético (média da rodada)
    balance = analyze_balance(summary["avg_generation_kw"], summary["avg_consumption_kw"])
    print("Balanço médio do período:")
    print(f"  status: {balance['status']}")
    print(f"  delta médio: {balance['delta_kw']:+.1f} kW")
    print(f"  mensagem: {balance['message']}")
    print()

    # Item 1.2 — Regras de decisão sobre o último snapshot
    snapshot = {
        "energy_kw": history["total_generation_kw"][-1],
        "consumption_kw": history["total_consumption_kw"][-1],
        "storm": history["storm"][-1],
    }
    actions = evaluate_rules(snapshot)
    print("Regras de decisão (último passo):")
    print(f"  entrada: energia={snapshot['energy_kw']:.1f} kW, "
          f"consumo={snapshot['consumption_kw']:.1f} kW, "
          f"tempestade={snapshot['storm']}")
    if actions:
        for a in actions:
            print(f"  → {a}")
    else:
        print("  → (nenhum alerta — operação saudável)")
    print()

    # Item 1.3 — Previsão eólica via regressão linear manual
    try:
        a, b = fit_wind_power_model(history)
        wind_forecast = 11.0  # mesmo exemplo do enunciado
        forecast_kw = max(0.0, predict(a, b, wind_forecast))
        sign = "+" if b >= 0 else "-"
        print("Previsão eólica (regressão linear sobre o histórico):")
        print(f"  reta ajustada: y = {a:.3f}·v {sign} {abs(b):.3f}")
        print(f"  para v = {wind_forecast} m/s → previsão ≈ {forecast_kw:.1f} kW")
    except ValueError as e:
        print(f"Previsão eólica indisponível: {e}")
    print()

    if args.log_file:
        write_log(history, args.log_file)
        print(f"Histórico passo-a-passo gravado em: {args.log_file}")


if __name__ == "__main__":
    main()
