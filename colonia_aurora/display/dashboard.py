"""
Dashboard Terminal — Colônia Aurora
====================================
Navegação: ← → ou teclas 1-6   |   P pausar/retomar   |   Q sair
"""

import os
import sys
import time
from collections import deque

from colonia_aurora.core.storage import DataStorage

# ─── ANSI ─────────────────────────────────────────────────────────────────────

ESC   = "\033"
RESET = f"{ESC}[0m"
BOLD  = f"{ESC}[1m"
DIM   = f"{ESC}[2m"


def fg(r, g, b): return f"{ESC}[38;2;{r};{g};{b}m"
def bg(r, g, b): return f"{ESC}[48;2;{r};{g};{b}m"
def goto(r, c):  return f"{ESC}[{r};{c}H"
def clr():       return f"{ESC}[2J{ESC}[H"
def hide_cur():  sys.stdout.write(f"{ESC}[?25l"); sys.stdout.flush()
def show_cur():  sys.stdout.write(f"{ESC}[?25h"); sys.stdout.flush()


AMBER  = fg(245, 158, 11);  AMBER_D = fg(120, 75, 5)
TEAL   = fg(20, 184, 166);  TEAL_D  = fg(10, 80, 70)
RED    = fg(239, 68, 68);   RED_D   = fg(100, 25, 25)
GREEN  = fg(34, 197, 94);   GREEN_D = fg(15, 80, 35)
BLUE   = fg(96, 165, 250)
PURPLE = fg(167, 139, 250)
GRAY   = fg(107, 128, 168); DIM_C   = fg(40, 55, 85)
WHITE  = fg(210, 220, 255); ORANGE  = fg(249, 115, 22)
YELLOW = fg(234, 179, 8)

BG_BASE   = bg(7, 11, 20)
BG_HEADER = bg(10, 18, 35)
BG_TAB_ON = bg(20, 35, 65)
BG_PANEL  = bg(9, 14, 26)

LEVEL_CLR = {
    "CRITICAL": RED, "LOW": ORANGE, "NOMINAL": YELLOW,
    "HIGH": GREEN,   "SURPLUS": TEAL,
}

HLINE = "─"; V = "│"; BAR_F = "█"; BAR_E = "░"

# ─── LAYOUT ───────────────────────────────────────────────────────────────────

TOTAL_W  = 100
TOTAL_H  = 30
CONTENT_H = TOTAL_H - 6   # header + tabbar + hint + sep + footer + 1
CONTENT_W = TOTAL_W - 2

ROW_HEADER  = 1
ROW_TABS    = 2
ROW_HINT    = 3
ROW_SEP     = 4
ROW_CONTENT = 5
ROW_FOOTER  = ROW_CONTENT + CONTENT_H + 1

# ─── INPUT ────────────────────────────────────────────────────────────────────

if sys.platform == "win32":
    import msvcrt

    def _get_key():
        if msvcrt.kbhit():
            ch = msvcrt.getch()
            if ch == b'\xe0':
                ch2 = msvcrt.getch()
                if ch2 == b'K': return "LEFT"
                if ch2 == b'M': return "RIGHT"
            elif ch.lower() == b'q': return "Q"
            elif ch.lower() == b'p': return "PAUSE"
            elif b'1' <= ch <= b'6': return str(int(ch))
        return None

    def enable_ansi():
        import ctypes
        k = ctypes.windll.kernel32
        k.SetConsoleMode(k.GetStdHandle(-11), 7)

else:
    import tty
    import termios
    import select

    _old_settings = None

    def enable_ansi():
        pass

    def _enable_raw():
        global _old_settings
        fd = sys.stdin.fileno()
        _old_settings = termios.tcgetattr(fd)
        tty.setraw(fd)

    def _disable_raw():
        if _old_settings is not None:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, _old_settings)

    def _get_key():
        fd = sys.stdin.fileno()
        r, _, _ = select.select([fd], [], [], 0)
        if not r:
            return None
        ch = os.read(fd, 3)
        if ch == b'\x1b[D': return "LEFT"
        if ch == b'\x1b[C': return "RIGHT"
        if ch in (b'q', b'Q', b'\x03'): return "Q"
        if ch in (b'p', b'P'): return "PAUSE"
        if b'1' <= ch <= b'6': return chr(ch[0])
        return None

# ─── HELPERS DE DESENHO ───────────────────────────────────────────────────────

def at(r, c, txt): return goto(r, c) + txt


def hbar(val, mx, w, color):
    filled = int((val / mx) * w) if mx > 0 else 0
    filled = max(0, min(w, filled))
    return color + BAR_F * filled + DIM_C + BAR_E * (w - filled) + RESET


def sparkline(vals, w, h, vmin=None, vmax=None):
    if not vals:
        return [DIM_C + "·" * w + RESET] * h
    if vmin is None: vmin = min(vals)
    if vmax is None: vmax = max(vals)
    vr = (vmax - vmin) or 1
    data = [int(((v - vmin) / vr) * (h - 1)) for v in vals][-w:]
    while len(data) < w:
        data.insert(0, 0)
    rows = []
    for ri in range(h - 1, -1, -1):
        row = ""
        for v in data:
            ratio = ri / (h - 1)
            if v >= ri:
                c = GREEN if ratio > 0.65 else (YELLOW if ratio > 0.35 else RED)
                row += c + BAR_F + RESET
            else:
                row += DIM_C + "·" + RESET
        rows.append(row)
    return rows


def miniline(vals, w, h):
    if not vals:
        return [" " * w] * h
    vmin = min(vals); vmax = max(vals); vr = vmax - vmin or 1
    data = [int(((v - vmin) / vr) * (h - 1)) for v in vals][-w:]
    while len(data) < w:
        data.insert(0, 0)
    rows = []
    for ri in range(h - 1, -1, -1):
        row = ""
        for i, v in enumerate(data):
            prev = data[i - 1] if i > 0 else v
            if v == ri:
                row += TEAL + "─" + RESET
            elif v > ri > prev or prev > ri > v:
                row += TEAL + "│" + RESET
            else:
                row += DIM_C + " " + RESET
        rows.append(row)
    return rows


def strip_ansi(text: str) -> str:
    import re
    return re.sub(r'\033\[[^m]*m', '', text)


def padto(text: str, width: int) -> str:
    plain_len = len(strip_ansi(text))
    diff = width - plain_len
    if diff < 0:
        return text
    return text + " " * diff

# ─── SCREENS ──────────────────────────────────────────────────────────────────

def screen_overview(storage: DataStorage, W: int, H: int, hist: dict) -> list:
    lines = []
    level  = storage.get("energy.level", "NOMINAL")
    lc     = LEVEL_CLR.get(level, WHITE)
    bat    = storage.get("energy.battery", 65.0)
    gen    = storage.get("energy.generated", 0.0)
    con    = storage.get("energy.consumed", 0.0)
    pred   = storage.get("energy.predicted_delta", 0.0)
    solar  = storage.get("energy.solar_gen", 0.0)
    wind   = storage.get("energy.wind_gen", 0.0)
    nuc    = storage.get("energy.nuclear_gen", 40.0)
    event  = storage.get("event.active")
    slope  = storage.get("energy.slope", 0.0)

    bat_bar = hbar(bat, 100, 28, lc)
    lines.append(
        f" {GRAY}Bateria: {lc}{bat:5.1f}%{RESET}  {bat_bar}  "
        f"{GRAY}Gerado:{GREEN}{gen:6.1f} kW{RESET}  "
        f"{GRAY}Consumido:{RED}{con:6.1f} kW{RESET}  "
        f"{GRAY}Saldo:{lc}{gen-con:+6.1f} kW{RESET}"
    )
    lines.append(DIM_C + HLINE * W + RESET)

    chart_h = max(3, H - 13)
    chart_w = W - 8
    lines.append(f"  {AMBER}Histórico da Bateria (%){RESET}")
    spark = sparkline(list(hist["bat"]), chart_w, chart_h, vmin=0, vmax=100)
    lbls  = {0: "100%", chart_h // 2: " 50%", chart_h - 1: "  0%"}
    for i, row in enumerate(spark):
        lbl = f"{GRAY}{lbls.get(i, '    ')}{RESET}"
        lines.append(f"  {lbl} {row}")
    lines.append(DIM_C + HLINE * W + RESET)

    lines.append(f"  {AMBER}Geração por Fonte{RESET}")
    bar_w = 28
    wind_status = storage.get("energy.wind_status", "OPERACIONAL")
    wind_status_clr = {
        "OPERACIONAL": GREEN, "SEM VENTO": GRAY,
        "EMBANDEIRADO": ORANGE, "DESLIGADO": RED,
    }.get(wind_status, GRAY)
    for label, val, c in [
        ("☀ Solar",   solar, GREEN),
        ("⚛ Nuclear", nuc,   AMBER),
    ]:
        b = hbar(val, gen if gen > 0 else 1, bar_w, c)
        lines.append(f"  {GRAY}{label:<10}{RESET} {b} {c}{val:6.1f} kW{RESET}")
    b = hbar(wind, gen if gen > 0 else 1, bar_w, TEAL)
    lines.append(
        f"  {GRAY}{'💨 Eólico':<10}{RESET} {b} {TEAL}{wind:6.1f} kW{RESET}"
        f"  {wind_status_clr}[{wind_status}]{RESET}"
    )

    lines.append(DIM_C + HLINE * W + RESET)
    lines.append(
        f"  {TEAL}Predição próx. delta: {lc}{BOLD}{pred:+6.1f} kW{RESET}  "
        f"{GRAY}Slope: {ORANGE}{slope:+.3f} kW/tick{RESET}  "
        f"{GRAY}Evento: {RESET}"
        + (f"{RED}{event}{RESET}" if event else f"{GREEN}Nenhum ✓{RESET}")
    )
    return lines


def screen_energia(storage: DataStorage, W: int, H: int, hist: dict) -> list:
    lines = []
    level = storage.get("energy.level", "NOMINAL")
    lc    = LEVEL_CLR.get(level, WHITE)
    half  = W // 2 - 2
    ch    = max(3, (H - 10) // 2)

    lines.append(f"  {AMBER}Bateria (%) — histórico{RESET}")
    lines.append(DIM_C + HLINE * W + RESET)
    spark = sparkline(list(hist["bat"]), W - 6, ch, vmin=0, vmax=100)
    lbls  = {0: "100%", ch // 2: " 50%", ch - 1: "  0%"}
    for i, row in enumerate(spark):
        lines.append(f"  {GRAY}{lbls.get(i,'    ')}{RESET} {row}")
    lines.append(DIM_C + HLINE * W + RESET)

    scale_w = 6
    chart_w = half - scale_w

    gen_vals = list(hist["gen"])
    con_vals = list(hist["con"])

    gen_min = min(gen_vals) if gen_vals else 0.0
    gen_max = max(gen_vals) if gen_vals else 0.0
    con_min = min(con_vals) if con_vals else 0.0
    con_max = max(con_vals) if con_vals else 0.0

    gen_lines = miniline(gen_vals, chart_w, ch)
    con_lines = miniline(con_vals, chart_w, ch)

    gen_lbls = {
        0:        f"{gen_max:5.1f}",
        ch // 2:  f"{(gen_max + gen_min) / 2:5.1f}",
        ch - 1:   f"{gen_min:5.1f}",
    }
    con_lbls = {
        0:        f"{con_max:5.1f}",
        ch // 2:  f"{(con_max + con_min) / 2:5.1f}",
        ch - 1:   f"{con_min:5.1f}",
    }

    lines.append(
        f"  {' ' * scale_w}{TEAL}Geração kW{' ' * (chart_w - 10)}"
        f"   {' ' * scale_w}{RED}Consumo kW{RESET}"
    )
    for i, (gl, cl) in enumerate(zip(gen_lines, con_lines)):
        g_lbl = f"{GRAY}{gen_lbls.get(i, '     ')}{RESET} "
        c_lbl = f"{GRAY}{con_lbls.get(i, '     ')}{RESET} "
        lines.append(f"  {g_lbl}{gl}   {c_lbl}{cl}")
    lines.append(DIM_C + HLINE * W + RESET)

    gen  = storage.get("energy.generated", 0.0)
    con  = storage.get("energy.consumed", 0.0)
    bat  = storage.get("energy.battery", 65.0)
    pred = storage.get("energy.predicted_delta", 0.0)
    slp  = storage.get("energy.slope", 0.0)
    solar = storage.get("energy.solar_gen", 0.0)
    wind  = storage.get("energy.wind_gen", 0.0)
    nuc   = storage.get("energy.nuclear_gen", 40.0)

    lines.append(
        f"  {GRAY}Solar:{GREEN}{solar:6.1f}{RESET}  "
        f"{GRAY}Eólico:{TEAL}{wind:6.1f}{RESET}  "
        f"{GRAY}Nuclear:{AMBER}{nuc:6.1f}{RESET}  "
        f"{GRAY}Total:{GREEN}{gen:7.1f}{RESET}  "
        f"{GRAY}Consumido:{RED}{con:7.1f}{RESET}"
    )
    lines.append(
        f"  {GRAY}Nível:{lc}{BOLD} {level:<9}{RESET}  "
        f"{GRAY}Bat:{lc}{bat:6.1f}%{RESET}  "
        f"{GRAY}Predição delta:{lc}{pred:+6.1f} kW{RESET}  "
        f"{GRAY}Slope:{ORANGE}{slp:+.3f}{RESET}"
    )
    lines.append(f"  {hbar(bat, 100, W - 6, lc)}")
    return lines


def screen_modulos(storage: DataStorage, W: int, H: int, hist: dict, module_manager) -> list:
    lines = []
    level = storage.get("energy.level", "NOMINAL")
    lc    = LEVEL_CLR.get(level, WHITE)
    lvl_map = {"CRITICAL": 1, "LOW": 2, "NOMINAL": 3, "HIGH": 4, "SURPLUS": 5}
    cur_lvl = lvl_map.get(level, 3)

    mods = storage.get("modules.snapshot", [])
    active_count = sum(1 for m in mods if m["active"] and not m["broken"])
    lines.append(f"  {AMBER}Módulos — {active_count} ativos / {len(mods)} total{RESET}")
    lines.append(DIM_C + HLINE * W + RESET)
    lines.append(
        f"  {GRAY}{'P.':<4}{'Nome':<12}{'Tipo':<14}{'Crit.':<7}"
        f"{'Cons.':<9}{'Status':<12}{'Risco?':<8}{RESET}"
    )
    lines.append(DIM_C + HLINE * W + RESET)

    for m in mods:
        if m["broken"]:
            sc, dot, st = RED, "✕", "quebrado"
        elif not m["active"]:
            sc, dot, st = DIM_C, "○", "offline "
        else:
            sc, dot, st = GREEN, "●", "online  "

        crit = m["criticality"]
        stars = AMBER + "★" * crit + DIM_C + "☆" * (5 - crit) + RESET
        at_risk = (crit < 4 and cur_lvl <= 2) or (crit < 3 and cur_lvl <= 3)
        risk = RED + "⚠" + RESET if at_risk else GREEN + "✓" + RESET

        lines.append(
            f"  {AMBER}{m['priority']:<4}{RESET}{sc}{dot} {m['name']:<11}{RESET}"
            f"{GRAY}{m['type']:<14}{RESET}"
            f"{stars}  "
            f"{sc}{m['consumption_kw']:<9.1f}{RESET}"
            f"{sc}{st:<12}{RESET}"
            f"{risk}"
        )
        if len(lines) >= H - 2:
            break

    lines.append(DIM_C + HLINE * W + RESET)
    total_active = sum(m["consumption_kw"] for m in mods if m["active"] and not m["broken"])
    gen = storage.get("energy.generated", 0.0)
    lines.append(
        f"  {GRAY}Consumo ativo:{RED}{total_active:7.1f} kW{RESET}  "
        f"{GRAY}Geração:{GREEN}{gen:7.1f} kW{RESET}  "
        f"{GRAY}Saldo:{lc}{gen - total_active:+7.1f} kW{RESET}"
    )
    return lines


def screen_sensores(storage: DataStorage, W: int, H: int, hist: dict) -> list:
    lines = []
    lines.append(f"  {AMBER}Leituras dos Sensores{RESET}")
    lines.append(DIM_C + HLINE * W + RESET)

    mini_h = 4
    mini_w = W // 2 - 6
    w_lines = miniline(list(hist["wind"]), mini_w, mini_h)
    s_lines = miniline(list(hist["solar"]), mini_w, mini_h)

    lines.append(
        f"  {TEAL}Velocidade do Vento (m/s){' ' * (mini_w - 22)}  {AMBER}Irradiância Solar (W/m²){RESET}"
    )
    for wl, sl in zip(w_lines, s_lines):
        lines.append(f"  {wl}   {sl}")
    lines.append(DIM_C + HLINE * W + RESET)

    temp  = storage.get("sensor.temperature", -30.0)
    wind  = storage.get("sensor.wind_speed", 8.0)
    irrad = storage.get("sensor.solar_irradiance", 200.0)
    dust  = storage.get("sensor.dust", 0.1)
    phase = storage.get("sensor.day_phase", 0.0)
    day_icon = "☀ DIA  " if phase > 0.2 else "☽ NOITE"
    phase_bar = AMBER + "▓" * int(phase * 20) + DIM_C + "░" * (20 - int(phase * 20)) + RESET

    sensors = [
        ("🌡 Temperatura",    f"{temp:+.1f} °C",   WHITE,  hbar(max(0, temp + 140), 170, 25, BLUE)),
        ("💨 Vel. Vento",     f"{wind:.1f} m/s",   TEAL,   hbar(wind, 100, 25, TEAL)),
        ("☀ Irradiância",    f"{irrad:.0f} W/m²", AMBER,  hbar(irrad, 590, 25, AMBER)),
        ("🌫 Poeira",         f"{dust:.2f}",        GRAY,   hbar(dust, 1, 25, RED)),
        (f"{day_icon}",      f"Fase: {phase:.2f}", AMBER,  phase_bar),
    ]
    for label, val, vc, bar in sensors:
        lines.append(
            f"  {GRAY}{label:<20}{RESET}  {vc}{BOLD}{val:<14}{RESET}  {bar}"
        )

    lines.append(DIM_C + HLINE * W + RESET)
    if wind >= 100:
        lines.append(f"  {RED}{BOLD}⚠ TURBINA PARADA — vento acima de 100 m/s{RESET}")
    elif wind >= 50:
        lines.append(f"  {ORANGE}▲ EMBANDEIRAMENTO parcial — vento {wind:.1f} m/s (50–100){RESET}")
    else:
        lines.append(f"  {GREEN}✓ Vento em faixa operacional ({wind:.1f} m/s){RESET}")
    return lines


def screen_eventos(storage: DataStorage, W: int, H: int, hist: dict, event_manager) -> list:
    lines = []
    lines.append(f"  {AMBER}Evento Climático Ativo{RESET}")
    lines.append(DIM_C + HLINE * W + RESET)

    event_type = storage.get("event.active")
    event_name = storage.get("event.name", event_type or "")
    ticks_left = storage.get("event.duration_ticks", 0)

    if event_type:
        lines.append(f"  {RED}{BOLD}  {event_name or event_type}{RESET}")
        if ticks_left > 0:
            lines.append(f"  {GRAY}  Ticks restantes: {ORANGE}{ticks_left}{RESET}")
            prog = hbar(ticks_left, 72, W - 20, RED)
            lines.append(f"  {prog}")
    else:
        lines.append(f"  {GREEN}  ✓ Nenhum evento ativo — condições nominais{RESET}")

    lines.append(DIM_C + HLINE * W + RESET)
    lines.append(f"  {AMBER}Log de Eventos{RESET}")
    lines.append(DIM_C + HLINE * W + RESET)

    log = storage.get("event.log", [])
    visible = log[-(H - len(lines) - 2):]
    for entry in reversed(visible):
        c = RED if "NOVO" in entry or "FALHA" in entry else (
            GREEN if "Encerrado" in entry or "Reparado" in entry else GRAY
        )
        lines.append(f"  {c}{entry[:W - 4]}{RESET}")
    return lines


def screen_crew(storage: DataStorage, W: int, H: int, hist: dict, crew_manager) -> list:
    lines = []
    members = list(crew_manager) if crew_manager else []
    active = sum(1 for c in members if c.status not in ("idle", "incapacitated"))
    lines.append(f"  {AMBER}Tripulantes — {len(members)} membros, {active} em operação{RESET}")
    lines.append(DIM_C + HLINE * W + RESET)
    lines.append(
        f"  {GRAY}{'Nome':<16}{'Cargo':<12}{'Saúde':<26}{'Status':<12}{'Módulo':<15}{RESET}"
    )
    lines.append(DIM_C + HLINE * W + RESET)

    status_c = {"working": GREEN, "resting": BLUE, "repairing": ORANGE,
                 "idle": DIM_C, "incapacitated": RED}
    status_icon = {"working": "⚙", "resting": "💤", "repairing": "🔧",
                   "idle": "—", "incapacitated": "✕"}

    for c in members:
        h = c.health
        h_bar = hbar(h, 1.0, 16, GREEN if h > 0.7 else (ORANGE if h > 0.4 else RED))
        h_pct = f"{h * 100:.0f}%"
        sc    = status_c.get(c.status, GRAY)
        icon  = status_icon.get(c.status, "?")
        mod_name = c.assigned_module.name if c.assigned_module else "—"
        lines.append(
            f"  {WHITE}{c.name:<16}{RESET}"
            f"{PURPLE}{c.role:<12}{RESET}"
            f"{h_bar} {GREEN if h > 0.7 else RED}{h_pct:<5}{RESET}"
            f"{sc}{icon} {c.status:<10}{RESET}"
            f"{GRAY}{mod_name:<15}{RESET}"
        )

    lines.append(DIM_C + HLINE * W + RESET)
    if members:
        avg = sum(c.health for c in members) / len(members)
        lines.append(
            f"  {GRAY}Saúde média: {GREEN if avg > 0.7 else RED}{avg * 100:.1f}%{RESET}  "
            + hbar(avg, 1.0, 40, GREEN if avg > 0.7 else RED)
        )
    return lines

# ─── TABS ─────────────────────────────────────────────────────────────────────

TABS = [
    ("Overview", "1"),
    ("Energia",  "2"),
    ("Módulos",  "3"),
    ("Sensores", "4"),
    ("Eventos",  "5"),
    ("Crew",     "6"),
]

# ─── RENDERER ─────────────────────────────────────────────────────────────────

def render(storage: DataStorage, tab_idx: int, paused: bool,
           hist: dict, module_manager, event_manager, crew_manager):
    buf = []
    level = storage.get("energy.level", "NOMINAL")
    lc    = LEVEL_CLR.get(level, WHITE)
    tick  = storage.get("tick", 0)
    sol   = storage.get("sol", 0)
    hr    = tick % 48
    bat   = storage.get("energy.battery", 65.0)
    alert = storage.get("energy.alert", "Operação nominal")

    # HEADER
    pause_tag = f" {RED}[PAUSADO]{RESET}" if paused else ""
    header = (
        f"{goto(ROW_HEADER, 1)}{BG_HEADER}"
        f"  {AMBER}{BOLD}◈ AURORA{RESET}{BG_HEADER}{pause_tag}"
        f"  {GRAY}Sol:{WHITE}{sol:>3}{RESET}{BG_HEADER}"
        f"  {GRAY}Tick:{WHITE}{tick:>5}{RESET}{BG_HEADER}"
        f"  {GRAY}Hora:{WHITE}{hr:02d}:00{RESET}{BG_HEADER}"
        + " " * max(0, TOTAL_W - 68)
        + f"{GRAY}Energia:{lc}{BOLD} {level:<9}{RESET}{BG_HEADER}"
        f"  {GRAY}Bat:{lc}{bat:5.1f}%{RESET}{BG_HEADER}"
        + "   " + "\033[K" + RESET
    )
    buf.append(header)

    # TAB BAR
    tab_line = f"{goto(ROW_TABS, 1)}{BG_PANEL} "
    for i, (name, num) in enumerate(TABS):
        label = f" {num}:{name} "
        if i == tab_idx:
            tab_line += f"{BG_TAB_ON}{AMBER}{BOLD}{label}{RESET}{BG_PANEL}{GRAY}│{RESET}{BG_PANEL}"
        else:
            tab_line += f"{GRAY}{label}{RESET}{BG_PANEL}{DIM_C}│{RESET}{BG_PANEL}"
    tab_line += "\033[K"
    buf.append(tab_line)

    # HINT
    hint = f"{goto(ROW_HINT, 1)}{BG_PANEL}  {DIM_C}← → ou 1-6 navegar  ·  P pausar  ·  Q sair\033[K{RESET}"
    buf.append(hint)

    # SEP
    buf.append(f"{goto(ROW_SEP, 1)}{DIM_C}{HLINE * TOTAL_W}{RESET}")

    # CONTENT
    if tab_idx == 0:
        lines = screen_overview(storage, CONTENT_W, CONTENT_H, hist)
    elif tab_idx == 1:
        lines = screen_energia(storage, CONTENT_W, CONTENT_H, hist)
    elif tab_idx == 2:
        lines = screen_modulos(storage, CONTENT_W, CONTENT_H, hist, module_manager)
    elif tab_idx == 3:
        lines = screen_sensores(storage, CONTENT_W, CONTENT_H, hist)
    elif tab_idx == 4:
        lines = screen_eventos(storage, CONTENT_W, CONTENT_H, hist, event_manager)
    else:
        lines = screen_crew(storage, CONTENT_W, CONTENT_H, hist, crew_manager)

    for i in range(CONTENT_H):
        row = ROW_CONTENT + i
        buf.append(goto(row, 1))
        if i < len(lines):
            buf.append(BG_BASE + lines[i] + BG_BASE + "\033[K" + RESET)
        else:
            buf.append(BG_BASE + "\033[2K" + RESET)

    # FOOTER
    alert_c = RED if "ALERTA" in alert else (TEAL if "SUGESTÃO" in alert else GREEN)
    footer = (
        f"{goto(ROW_FOOTER, 1)}{BG_HEADER}"
        f"  {alert_c}{alert[:TOTAL_W - 30]:<{TOTAL_W - 30}}{RESET}{BG_HEADER}"
        f"  {DIM_C}tickrate: 0.5s/tick{RESET}"
        + "   " + RESET
    )
    buf.append(footer)

    sys.stdout.write("".join(buf))
    sys.stdout.flush()

# ─── ENTRY POINT ──────────────────────────────────────────────────────────────

class Dashboard:
    def __init__(self, module_manager=None, event_manager=None, crew_manager=None, pause_event=None):
        self.module_manager = module_manager
        self.event_manager  = event_manager
        self.crew_manager   = crew_manager
        self.pause_event    = pause_event
        self._hist = {
            "bat":   deque([65.0] * CONTENT_W, maxlen=CONTENT_W),
            "gen":   deque([50.0] * (CONTENT_W // 2), maxlen=CONTENT_W // 2),
            "con":   deque([50.0] * (CONTENT_W // 2), maxlen=CONTENT_W // 2),
            "wind":  deque([8.0] * 40, maxlen=40),
            "solar": deque([200.0] * 40, maxlen=40),
        }

    def _update_hist(self, storage: DataStorage):
        self._hist["bat"].append(storage.get("energy.battery", 65.0))
        self._hist["gen"].append(storage.get("energy.generated", 0.0))
        self._hist["con"].append(storage.get("energy.consumed", 0.0))
        self._hist["wind"].append(storage.get("sensor.wind_speed", 8.0))
        self._hist["solar"].append(storage.get("sensor.solar_irradiance", 200.0))

    def run(self, stop_flag=None):
        enable_ansi()
        if sys.platform != "win32":
            _enable_raw()

        try:
            sz = os.get_terminal_size()
            if sz.columns < TOTAL_W or sz.lines < TOTAL_H:
                print(f"\n⚠  Terminal pequeno: {sz.columns}×{sz.lines}  |  Necessário: {TOTAL_W}×{TOTAL_H}")
                print("   Redimensione a janela e tente novamente.\n")
                return
        except OSError:
            pass

        hide_cur()
        sys.stdout.write(clr())
        sys.stdout.flush()

        storage      = DataStorage()
        tab_idx      = 0
        paused       = False
        tick_rate    = 0.5
        poll_rate    = 0.05
        last_tick    = time.monotonic()

        try:
            while True:
                # Drain ALL pending keystrokes so rapid presses jump straight
                # to the final destination instead of walking through each tab.
                pending = []
                while True:
                    k = _get_key()
                    if k is None:
                        break
                    pending.append(k)

                quit_requested = False
                nav_changed    = False
                for key in pending:
                    if key == "RIGHT":
                        tab_idx = (tab_idx + 1) % len(TABS)
                        nav_changed = True
                    elif key == "LEFT":
                        tab_idx = (tab_idx - 1) % len(TABS)
                        nav_changed = True
                    elif key in ("1", "2", "3", "4", "5", "6"):
                        tab_idx = int(key) - 1
                        nav_changed = True
                    elif key == "PAUSE":
                        paused = not paused
                        nav_changed = True
                        if self.pause_event:
                            if paused:
                                self.pause_event.clear()
                            else:
                                self.pause_event.set()
                    elif key == "Q":
                        quit_requested = True
                        break

                if quit_requested:
                    break

                now = time.monotonic()
                tick_due = (now - last_tick) >= tick_rate

                if tick_due or nav_changed:
                    if tick_due and not paused:
                        self._update_hist(storage)
                        last_tick = now
                    render(storage, tab_idx, paused,
                           self._hist, self.module_manager,
                           self.event_manager, self.crew_manager)

                time.sleep(poll_rate)

        except KeyboardInterrupt:
            pass
        finally:
            if sys.platform != "win32":
                _disable_raw()
            show_cur()
            sys.stdout.write(f"{goto(TOTAL_H + 1, 1)}{RESET}\n")
            tick = storage.get("tick", 0)
            sol  = storage.get("sol", 0)
            print(f"\n{AMBER}Simulação encerrada — Sol {sol}, Tick {tick}{RESET}\n")
