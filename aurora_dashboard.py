"""
POC: Terminal Dashboard com Abas — Colônia Aurora
==================================================
Navegação por abas com teclas ← → do teclado.
Atualização em tempo real via tickrate configurável.

Uso:    python aurora_dashboard.py
Navega: ← → (setas do teclado)
Sair:   Q ou Ctrl+C

Compatível: Linux, macOS, Windows 10+ (CMD/PowerShell/Windows Terminal)
"""

import os, sys, time, math, random, threading
from collections import deque

# ─── ANSI ─────────────────────────────────────────────────────────────────────

ESC   = "\033"
RESET = f"{ESC}[0m"
BOLD  = f"{ESC}[1m"
DIM   = f"{ESC}[2m"

def fg(r,g,b):    return f"{ESC}[38;2;{r};{g};{b}m"
def bg(r,g,b):    return f"{ESC}[48;2;{r};{g};{b}m"
def goto(r,c):    return f"{ESC}[{r};{c}H"
def clr():        return f"{ESC}[2J{ESC}[H"
def clr_line():   return f"{ESC}[2K"
def hide_cur():   sys.stdout.write(f"{ESC}[?25l"); sys.stdout.flush()
def show_cur():   sys.stdout.write(f"{ESC}[?25h"); sys.stdout.flush()

AMBER  = fg(245,158,11);  AMBER_D  = fg(120, 75,  5)
TEAL   = fg(20, 184,166); TEAL_D   = fg(10,  80, 70)
RED    = fg(239, 68, 68); RED_D    = fg(100, 25, 25)
GREEN  = fg(34, 197, 94); GREEN_D  = fg(15,  80, 35)
BLUE   = fg(96, 165,250)
PURPLE = fg(167,139,250); PURPLE_D = fg(70,  50,130)
GRAY   = fg(107,128,168); DIM_C    = fg(40,  55, 85)
WHITE  = fg(210,220,255); ORANGE   = fg(249,115, 22)
YELLOW = fg(234,179,  8)

BG_BASE   = bg( 7, 11, 20)
BG_HEADER = bg(10, 18, 35)
BG_TAB_ON = bg(20, 35, 65)
BG_PANEL  = bg( 9, 14, 26)

LEVEL_CLR = {"CRITICAL":RED,"LOW":ORANGE,"NOMINAL":YELLOW,"HIGH":GREEN,"SURPLUS":TEAL}

# Box chars
H="─";V="│";TL="┌";TR="┐";BL="└";BR="┘"
LT="├";RT="┤";TT="┬";BT="┴";CC="┼"
BAR_F="█"; BAR_E="░"

# ─── CONFIGURAÇÃO DO LAYOUT ───────────────────────────────────────────────────

TOTAL_W   = 100   # largura total (cols)
TOTAL_H   = 30    # altura total  (rows)
HEADER_H  = 1     # linha do header
TABBAR_H  = 1     # linha da tab bar
SEP_H     = 1     # separador
FOOTER_H  = 1     # linha do footer
CONTENT_H = TOTAL_H - HEADER_H - TABBAR_H - SEP_H - FOOTER_H - 1
CONTENT_W = TOTAL_W - 2   # margem 1 col cada lado

ROW_HEADER  = 1
ROW_TABS    = 2
ROW_SEP     = 3
ROW_CONTENT = 4
ROW_FOOTER  = ROW_CONTENT + CONTENT_H + 1

# ─── INPUT NÃO-BLOQUEANTE ─────────────────────────────────────────────────────

if sys.platform == "win32":
    import msvcrt

    def _get_key():
        """Lê tecla no Windows. Retorna 'LEFT','RIGHT','Q' ou None."""
        if msvcrt.kbhit():
            ch = msvcrt.getch()
            if ch == b'\xe0':           # tecla especial
                ch2 = msvcrt.getch()
                if ch2 == b'K': return "LEFT"
                if ch2 == b'M': return "RIGHT"
            elif ch.lower() == b'q':
                return "Q"
        return None

    def enable_ansi():
        import ctypes
        k = ctypes.windll.kernel32
        k.SetConsoleMode(k.GetStdHandle(-11), 7)

else:
    import tty, termios, select

    _old_settings = None

    def enable_raw():
        global _old_settings
        fd = sys.stdin.fileno()
        _old_settings = termios.tcgetattr(fd)
        tty.setraw(fd)

    def disable_raw():
        if _old_settings is not None:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, _old_settings)

    def _get_key():
        """Lê tecla no Linux/macOS (modo raw, não bloqueante)."""
        fd = sys.stdin.fileno()
        r, _, _ = select.select([fd], [], [], 0)
        if not r:
            return None
        ch = os.read(fd, 3)
        if ch == b'\x1b[D': return "LEFT"
        if ch == b'\x1b[C': return "RIGHT"
        if ch in (b'q', b'Q', b'\x03'): return "Q"
        return None

    def enable_ansi():
        pass  # Linux/mac tem ANSI nativo

# ─── SIMULAÇÃO ────────────────────────────────────────────────────────────────

class Sim:
    MODULES = [
        # (id, nome, tipo, prioridade, consumo_kw, criticidade, ativo)
        (1,  "Command",    "command",      1,  5,  5, True),
        (2,  "ECLSS",      "life_support", 2,  20, 5, True),
        (3,  "Habitat",    "habitat",      3,  15, 4, True),
        (4,  "Solar",      "solar",        4,  2,  5, True),
        (5,  "Nuclear",    "nuclear",      5,  3,  5, True),
        (6,  "Eólico",     "wind",         6,  1,  5, True),
        (7,  "Comms",      "comms",        7,  8,  4, True),
        (8,  "Medical",    "medical",      8,  10, 4, True),
        (9,  "Food",       "food",         9,  12, 3, True),
        (10, "Logistics",  "logistics",    10, 6,  3, False),
        (11, "ISRU",       "isru",         11, 18, 2, False),
        (12, "Workshop",   "workshop",     12, 8,  2, True),
        (13, "Lab",        "lab",          13, 10, 2, False),
        (14, "Sensors",    "sensors",      14, 3,  4, True),
    ]
    CREW = [
        {"name":"Ana Silva",    "role":"engineer",   "health":0.97, "status":"working",   "mod": "Eólico"},
        {"name":"Bruno Reis",   "role":"medic",      "health":0.85, "status":"resting",   "mod": "—"},
        {"name":"Carla Matos",  "role":"scientist",  "health":0.91, "status":"repairing", "mod": "ISRU"},
        {"name":"Diego Alves",  "role":"commander",  "health":0.99, "status":"working",   "mod": "Command"},
        {"name":"Eva Torres",   "role":"technician", "health":0.78, "status":"idle",      "mod": "—"},
    ]

    def __init__(self):
        self.tick = 0; self.lock = threading.Lock()
        self.battery    = 65.0
        self.bat_hist   = deque([65.0]*CONTENT_W, maxlen=CONTENT_W)
        self.gen_hist   = deque([50.0]*(CONTENT_W//2), maxlen=CONTENT_W//2)
        self.con_hist   = deque([50.0]*(CONTENT_W//2), maxlen=CONTENT_W//2)
        self.wind_hist  = deque([8.0]*40, maxlen=40)
        self.solar_hist = deque([200.0]*40, maxlen=40)
        self.event_log  = deque(maxlen=CONTENT_H - 2)
        self.event = None; self.event_ticks = 0
        # estado dos módulos (cópia mutável)
        self.mods = [list(m) for m in self.MODULES]
        self.crew = [dict(c) for c in self.CREW]
        # valores de sensores
        self.temperature=0; self.wind_speed=0; self.solar_irrad=0
        self.day_phase=0;   self.dust=0
        self.generated=0;   self.consumed=0
        self.solar_gen=0;   self.wind_gen=0;   self.nuclear_gen=40
        self.predicted=0;   self.level="NOMINAL"
        self.alert=""

    def step(self):
        with self.lock:
            self.tick += 1
            t = self.tick
            angle     = (t % 24) / 24 * 2 * math.pi
            day_phase = (math.cos(angle - math.pi) + 1) / 2

            # Sensores
            self.temperature = round(-30 + 10*math.sin(t*0.1) + random.uniform(-1,1), 1)
            self.wind_speed  = round(max(0, 8 + 5*math.sin(t*0.07) + random.uniform(-1,1)), 1)
            self.solar_irrad = round(max(0, 350*day_phase + random.uniform(-20,20)), 0)
            self.day_phase   = round(day_phase, 2)
            self.dust        = round(random.uniform(0.05, 0.3), 2)
            self.wind_hist.append(self.wind_speed)
            self.solar_hist.append(self.solar_irrad)

            # Evento
            if self.event_ticks > 0:
                self.event_ticks -= 1
                if self.event_ticks == 0:
                    self.event_log.append(f"[T{t:04d}] ✓ Evento encerrado: {self.event}")
                    self.event = None
            elif random.random() < 0.04:
                opts = ["❄ Frente Fria","🌪 Tempestade","⚠ Falha: Solar","⚠ Falha: Comms"]
                self.event = random.choice(opts)
                self.event_ticks = random.randint(6, 18)
                self.event_log.append(f"[T{t:04d}] ⚡ NOVO: {self.event} (duração: {self.event_ticks} ticks)")
                if "Tempestade" in self.event:
                    self.solar_irrad *= 0.2
                    self.wind_speed = min(50, self.wind_speed + 15)

            # Geração
            self.solar_gen   = round(self.solar_irrad * 0.08 * day_phase, 1)
            self.wind_gen    = round(min(45, 0.002*self.wind_speed**3), 1) if self.wind_speed >= 3 else 0.0
            if self.wind_speed > 35: self.wind_gen = 0.0
            elif self.wind_speed > 25: self.wind_gen = round(self.wind_gen * 0.3, 1)
            self.nuclear_gen = 40.0
            self.generated   = round(self.solar_gen + self.wind_gen + self.nuclear_gen, 1)

            # Consumo
            active = [m for m in self.mods if m[6]]
            self.consumed = round(sum(m[4] for m in active) + random.uniform(-2, 2), 1)

            # Bateria
            delta = (self.generated - self.consumed) * 0.01
            self.battery = max(0, min(100, self.battery + delta + random.uniform(-0.3, 0.3)))
            self.bat_hist.append(self.battery)
            self.gen_hist.append(self.generated)
            self.con_hist.append(self.consumed)

            # Nível
            b = self.battery
            if   b < 20: self.level = "CRITICAL"
            elif b < 40: self.level = "LOW"
            elif b > 90: self.level = "SURPLUS"
            elif self.generated > self.consumed: self.level = "HIGH"
            else:        self.level = "NOMINAL"

            # Alerta
            if   self.level == "CRITICAL": self.alert = "⚠ ALERTA: consumo maior que geração — modo emergência ativado"
            elif self.level == "LOW":      self.alert = "▲ ALERTA: reduzir consumo — desligando sistemas não essenciais"
            elif self.level == "SURPLUS":  self.alert = "✓ SUGESTÃO: armazenar energia excedente"
            else:                          self.alert = "◈ Operação nominal — todos os sistemas estáveis"

            # Regressão linear (predição)
            xs = list(range(len(self.gen_hist)))
            ys = list(self.gen_hist)
            self.predicted = round(self._lr(xs, ys, len(xs)), 1)

    @staticmethod
    def _lr(xs, ys, xn):
        n = len(xs)
        if n < 2: return ys[-1] if ys else 0
        xm = sum(xs)/n; ym = sum(ys)/n
        num = sum((x-xm)*(y-ym) for x,y in zip(xs,ys))
        den = sum((x-xm)**2 for x in xs)
        s = num/den if den else 0
        return max(0, s*xn + (ym - s*xm))

# ─── UTILITÁRIOS DE DESENHO ───────────────────────────────────────────────────

def at(r, c, txt):
    return goto(r, c) + txt

def hbar(val, mx, w, color):
    filled = int((val/mx)*w) if mx > 0 else 0
    filled = max(0, min(w, filled))
    return color + BAR_F*filled + DIM_C + BAR_E*(w-filled) + RESET

def sparkline(vals, w, h):
    """Area chart de h linhas, w colunas. Retorna lista de strings."""
    if not vals: return [DIM_C + "·"*w + RESET]*h
    vmin=min(vals); vmax=max(vals); vr=vmax-vmin or 1
    data = [int(((v-vmin)/vr)*(h-1)) for v in vals][-w:]
    while len(data) < w: data.insert(0,0)
    rows = []
    for ri in range(h-1, -1, -1):
        row = ""
        for v in data:
            ratio = ri/(h-1)
            if v >= ri:
                if   ratio > 0.65: c = GREEN
                elif ratio > 0.35: c = YELLOW
                else:              c = RED
                row += c + BAR_F + RESET
            else:
                row += DIM_C + "·" + RESET
        rows.append(row)
    return rows

def miniline(vals, w, h):
    """Linha simples (waveform). Retorna lista de strings."""
    if not vals: return [" "*w]*h
    vmin=min(vals); vmax=max(vals); vr=vmax-vmin or 1
    data = [int(((v-vmin)/vr)*(h-1)) for v in vals][-w:]
    while len(data) < w: data.insert(0,0)
    rows = []
    for ri in range(h-1, -1, -1):
        row = ""
        for i,v in enumerate(data):
            prev = data[i-1] if i > 0 else v
            if v == ri: row += TEAL+"─"+RESET
            elif v > ri > prev or prev > ri > v: row += TEAL+"│"+RESET
            elif v > ri and prev < ri: row += TEAL+"╱"+RESET
            elif v < ri and prev > ri: row += TEAL+"╲"+RESET
            else: row += DIM_C+" "+RESET
        rows.append(row)
    return rows

def section_header(title, w, color=AMBER):
    line = DIM_C+H*w+RESET
    return [
        color+BOLD+" "+title+RESET,
        line,
    ]

def col(text, width):
    """Trunca/preenche string (ignora ANSI)."""
    import re
    plain = re.sub(r'\033\[[^m]*m','',text)
    diff  = width - len(plain)
    if diff < 0: return text
    return text + " "*diff

# ─── SCREENS ─────────────────────────────────────────────────────────────────
#
#  Cada screen é uma função que recebe (sim, w, h) e retorna lista de strings.
#  Cada string é uma linha completa (sem newline). O renderer posiciona.

def screen_overview(sim, W, H):
    lines = []
    lc = LEVEL_CLR.get(sim.level, WHITE)

    # ── Linha de status rápido
    bat_bar = hbar(sim.battery, 100, 30, lc)
    lines.append(
        f" {GRAY}Bateria: {lc}{sim.battery:5.1f}%{RESET}  {bat_bar}  "
        f"{GRAY}Gerado:{GREEN}{sim.generated:6.1f} kW{RESET}  "
        f"{GRAY}Consumido:{RED}{sim.consumed:6.1f} kW{RESET}  "
        f"{GRAY}Saldo:{lc}{sim.generated-sim.consumed:+6.1f} kW{RESET}"
    )
    lines.append(DIM_C+H*W+RESET)

    # ── Gráfico de bateria
    chart_h = H - 13
    chart_w = W - 8
    lines.append(f"  {AMBER}Histórico da Bateria (%){RESET}")
    spark = sparkline(list(sim.bat_hist), chart_w, chart_h)
    labels = {0:"100%", chart_h//2:" 50%", chart_h-1:"  0%"}
    for i,row in enumerate(spark):
        lbl = f"{GRAY}{labels.get(i,'    ')}{RESET}"
        lines.append(f"  {lbl} {row}")
    lines.append(DIM_C+H*W+RESET)

    # ── Fontes de energia
    lines.append(f"  {AMBER}Geração por Fonte{RESET}")
    bar_w = 30
    src = [("☀ Solar",   sim.solar_gen,   sim.generated, GREEN),
           ("💨 Eólico",  sim.wind_gen,    sim.generated, TEAL),
           ("⚛ Nuclear", sim.nuclear_gen, sim.generated, AMBER)]
    for label,val,mx,c in src:
        b = hbar(val, mx if mx else 1, bar_w, c)
        lines.append(f"  {GRAY}{label:<10}{RESET} {b} {c}{val:6.1f} kW{RESET}")

    lines.append(DIM_C+H*W+RESET)

    # ── Predição e evento
    lines.append(
        f"  {TEAL}Predição próx. tick: {RESET}{TEAL}{BOLD}{sim.predicted:6.1f} kW{RESET}"
        f"   {GRAY}Evento ativo: {RESET}"
        + (f"{RED}{sim.event}  {GRAY}({sim.event_ticks} ticks){RESET}"
           if sim.event else f"{GREEN}Nenhum ✓{RESET}")
    )
    return lines

def screen_energia(sim, W, H):
    lines = []
    lc = LEVEL_CLR.get(sim.level, WHITE)
    half_w = W // 2 - 2
    chart_h = (H - 10) // 2

    # ── Painel superior: bateria
    for s in section_header("Bateria (%) — histórico", W): lines.append(s)
    spark = sparkline(list(sim.bat_hist), W-6, chart_h)
    lbls  = {0:"100%", chart_h//2:" 50%", chart_h-1:"  0%"}
    for i,row in enumerate(spark):
        lines.append(f"  {GRAY}{lbls.get(i,'    ')}{RESET} {row}")

    lines.append(DIM_C+H*W+RESET)

    # ── Painel inferior esquerdo: geração | direito: consumo
    gen_lines = miniline(list(sim.gen_hist), half_w, chart_h)
    con_lines = miniline(list(sim.con_hist), half_w, chart_h)

    lines.append(
        f"  {TEAL}Geração kW — waveform{RESET}"
        + " "*(half_w-18)
        + f"  {RED}Consumo kW — waveform{RESET}"
    )
    for gl, cl in zip(gen_lines, con_lines):
        lines.append(f"  {gl}   {cl}")

    lines.append(DIM_C+H*W+RESET)

    # ── Stats numéricos
    lines.append(
        f"  {GRAY}Solar:{GREEN}{sim.solar_gen:6.1f}{RESET}  "
        f"{GRAY}Eólico:{TEAL}{sim.wind_gen:6.1f}{RESET}  "
        f"{GRAY}Nuclear:{AMBER}{sim.nuclear_gen:6.1f}{RESET}  "
        f"{GRAY}| Total gerado:{GREEN}{sim.generated:7.1f}{RESET}  "
        f"{GRAY}Consumido:{RED}{sim.consumed:7.1f}{RESET}  "
        f"{GRAY}Predição:{TEAL}{sim.predicted:7.1f}{RESET}"
    )
    lines.append(
        f"  {GRAY}Nível:{lc}{BOLD} {sim.level:<9}{RESET}  "
        f"{GRAY}Bateria:{lc}{sim.battery:6.1f}%{RESET}  "
        f"{hbar(sim.battery,100,40,lc)}"
    )
    return lines

def screen_modulos(sim, W, H):
    lines = []
    for s in section_header(f"Módulos ({len([m for m in sim.mods if m[6]])} ativos / {len(sim.mods)} total)", W):
        lines.append(s)

    # Cabeçalho tabela
    lines.append(
        f"  {GRAY}{'P.':<4}{'Nome':<13}{'Tipo':<14}{'Crit.':<7}"
        f"{'Cons.':<9}{'Status':<12}{'Nível ok?':<10}{RESET}"
    )
    lines.append(DIM_C + H*W + RESET)

    lc = LEVEL_CLR.get(sim.level, WHITE)
    lvl_map = {"CRITICAL":1,"LOW":2,"NOMINAL":3,"HIGH":4,"SURPLUS":5}
    cur_lvl = lvl_map.get(sim.level, 3)

    for m in sim.mods:
        mid,mname,mtype,mpri,mcons,mcrit,mact = m
        if not mact:
            status_c, dot, status_s = DIM_C, "○", "offline"
        else:
            status_c, dot, status_s = GREEN, "●", "online "

        # Criticidade: estrelas
        stars = AMBER+"★"*mcrit + DIM_C+"☆"*(5-mcrit) + RESET

        # O módulo sofre com o nível atual?
        # Módulos crit >=4 continuam; crit <3 sofrem em LOW/CRITICAL
        at_risk = (mcrit < 4 and cur_lvl <= 2) or (mcrit < 3 and cur_lvl <= 3)
        risk_c  = RED+"⚠"+RESET if at_risk else GREEN+"✓"+RESET

        lines.append(
            f"  {AMBER}{mpri:<4}{RESET}{status_c}{dot} {mname:<12}{RESET}"
            f"{GRAY}{mtype:<14}{RESET}"
            f"{stars}  "
            f"{status_c}{mcons:<9.1f}{RESET}"
            f"{status_c}{status_s:<12}{RESET}"
            f"{risk_c}"
        )

        if len(lines) >= H - 1: break

    lines.append(DIM_C+H*W+RESET)
    active_cons = sum(m[4] for m in sim.mods if m[6])
    lines.append(
        f"  {GRAY}Total consumo ativo:{RED}{active_cons:7.1f} kW{RESET}  "
        f"{GRAY}Geração:{GREEN}{sim.generated:7.1f} kW{RESET}  "
        f"{GRAY}Saldo:{lc}{sim.generated-active_cons:+7.1f} kW{RESET}"
    )
    return lines

def screen_sensores(sim, W, H):
    lines = []
    for s in section_header("Leituras dos Sensores", W): lines.append(s)

    mini_h = 4
    mini_w = W // 2 - 6

    # Vento
    w_lines  = miniline(list(sim.wind_hist),  mini_w, mini_h)
    s_lines  = miniline(list(sim.solar_hist), mini_w, mini_h)

    lines.append(f"  {TEAL}Velocidade do Vento (m/s){' '*(mini_w-22)}  {AMBER}Irradiância Solar (W/m²){RESET}")
    for wl, sl in zip(w_lines, s_lines):
        lines.append(f"  {wl}   {sl}")

    lines.append(DIM_C+H*W+RESET)

    # Tabela de leituras
    for s in section_header("Valores Atuais", W): lines.append(s)

    phase_str = "▓"*int(sim.day_phase*20)+"░"*(20-int(sim.day_phase*20))
    day_icon  = "☀ DIA  " if sim.day_phase > 0.2 else "☽ NOITE"

    sensors = [
        ("🌡 Temperatura",   f"{sim.temperature:+.1f} °C",    WHITE,
         hbar(max(0,sim.temperature+70), 90, 25, BLUE)),
        ("💨 Vel. do Vento", f"{sim.wind_speed:.1f} m/s",    TEAL,
         hbar(sim.wind_speed, 50, 25, TEAL)),
        ("☀ Irradiância",   f"{sim.solar_irrad:.0f} W/m²",  AMBER,
         hbar(sim.solar_irrad, 600, 25, AMBER)),
        ("🌫 Nível de Poeira",f"{sim.dust:.2f}",             GRAY,
         hbar(sim.dust, 1, 25, RED)),
        (f"{day_icon}",     f"Fase: {sim.day_phase:.2f}",    AMBER,
         f"{AMBER}{phase_str}{RESET}"),
    ]

    for label, val, vc, bar in sensors:
        lines.append(
            f"  {GRAY}{label:<20}{RESET}  {vc}{BOLD}{val:<14}{RESET}  {bar}"
        )

    lines.append(DIM_C+H*W+RESET)

    # Alerta de vento
    if sim.wind_speed > 35:
        lines.append(f"  {RED}{BOLD}⚠ TURBINA PARADA — vento acima de 35 m/s (embandeiramento total){RESET}")
    elif sim.wind_speed > 25:
        lines.append(f"  {ORANGE}▲ EMBANDEIRAMENTO — vento entre 25–35 m/s, geração reduzida 70%{RESET}")
    else:
        lines.append(f"  {GREEN}✓ Vento em faixa operacional segura{RESET}")

    return lines

def screen_eventos(sim, W, H):
    lines = []
    for s in section_header("Evento Climático Ativo", W): lines.append(s)

    if sim.event:
        lines.append(f"  {RED}{BOLD}  {sim.event}{RESET}")
        lines.append(f"  {GRAY}  Ticks restantes: {ORANGE}{sim.event_ticks}{RESET}")
        prog = hbar(sim.event_ticks, 18, W-20, RED)
        lines.append(f"  {prog}")
    else:
        lines.append(f"  {GREEN}  ✓ Nenhum evento ativo — condições nominais{RESET}")

    lines.append(DIM_C+H*W+RESET)
    for s in section_header(f"Log de Eventos ({len(sim.event_log)} registros)", W): lines.append(s)

    log = list(sim.event_log)
    visible = log[-(H - len(lines) - 2):]
    for entry in reversed(visible):
        c = RED if "NOVO" in entry else (GREEN if "encerrado" in entry else GRAY)
        lines.append(f"  {c}{entry[:W-4]}{RESET}")

    return lines

def screen_crew(sim, W, H):
    lines = []
    active = sum(1 for c in sim.crew if c["status"]!="idle")
    for s in section_header(f"Tripulantes — {len(sim.crew)} membros, {active} em operação", W):
        lines.append(s)

    # Cabeçalho tabela
    lines.append(
        f"  {GRAY}{'Nome':<16}{'Cargo':<12}{'Saúde':<24}"
        f"{'Status':<12}{'Módulo Atual':<15}{RESET}"
    )
    lines.append(DIM_C+H*W+RESET)

    status_c_map = {
        "working":   GREEN,
        "resting":   BLUE,
        "repairing": ORANGE,
        "idle":      DIM_C,
    }
    status_icon = {
        "working":  "⚙",
        "resting":  "💤",
        "repairing":"🔧",
        "idle":     "—",
    }

    for c in sim.crew:
        hval = c["health"]
        h_bar = hbar(hval, 1.0, 16,
                     GREEN if hval > 0.7 else (ORANGE if hval > 0.4 else RED))
        h_pct = f"{hval*100:.0f}%"
        sc    = status_c_map.get(c["status"], GRAY)
        icon  = status_icon.get(c["status"], "?")
        lines.append(
            f"  {WHITE}{c['name']:<16}{RESET}"
            f"{PURPLE}{c['role']:<12}{RESET}"
            f"{h_bar} {GREEN if hval>0.7 else RED}{h_pct:<5}{RESET}"
            f"{sc}{icon} {c['status']:<10}{RESET}"
            f"{GRAY}{c['mod']:<15}{RESET}"
        )

    lines.append(DIM_C+H*W+RESET)
    lines.append(f"  {AMBER}Resumo de Saúde da Tripulação{RESET}")
    avg_health = sum(c["health"] for c in sim.crew) / len(sim.crew)
    lines.append(
        f"  {GRAY}Saúde média: {GREEN if avg_health > 0.7 else RED}"
        f"{avg_health*100:.1f}%{RESET}  "
        + hbar(avg_health, 1.0, 40, GREEN if avg_health > 0.7 else RED)
    )
    lines.append(DIM_C+H*W+RESET)
    lines.append(f"  {GRAY}Nota: saúde decresce se ECLSS ficr em CRITICAL por 3+ ticks consecutivos.{RESET}")

    return lines

# ─── TABS ─────────────────────────────────────────────────────────────────────

TABS = [
    ("Overview",   screen_overview),
    ("Energia",    screen_energia),
    ("Módulos",    screen_modulos),
    ("Sensores",   screen_sensores),
    ("Eventos",    screen_eventos),
    ("Crew",       screen_crew),
]

# ─── RENDERER ─────────────────────────────────────────────────────────────────

def render(sim, tab_idx):
    buf = []

    with sim.lock:
        lc  = LEVEL_CLR.get(sim.level, WHITE)
        sol = sim.tick // 24
        hr  = sim.tick % 24

        # ── HEADER ────────────────────────────────────────────────────────────
        header = (
            f"{goto(ROW_HEADER,1)}{BG_HEADER}"
            f"  {AMBER}{BOLD}◈ AURORA{RESET}{BG_HEADER}"
            f"  {GRAY}Sol:{WHITE}{sol:>3}{RESET}{BG_HEADER}"
            f"  {GRAY}Tick:{WHITE}{sim.tick:>5}{RESET}{BG_HEADER}"
            f"  {GRAY}Hora:{WHITE}{hr:02d}:00{RESET}{BG_HEADER}"
            + " " * (TOTAL_W - 65)
            + f"{GRAY}Energia:{lc}{BOLD} {sim.level:<9}{RESET}{BG_HEADER}"
            f"  {GRAY}Bat:{lc}{sim.battery:5.1f}%{RESET}{BG_HEADER}"
            + "   " + RESET
        )
        buf.append(header)

        # ── TAB BAR ───────────────────────────────────────────────────────────
        tab_line = f"{goto(ROW_TABS,1)}{BG_PANEL} "
        for i,(name,_) in enumerate(TABS):
            if i == tab_idx:
                tab_line += f"{BG_TAB_ON}{AMBER}{BOLD} {name} {RESET}{BG_PANEL}{GRAY}│{RESET}{BG_PANEL}"
            else:
                tab_line += f"{GRAY} {name} {RESET}{BG_PANEL}{DIM_C}│{RESET}{BG_PANEL}"
        # hint de navegação
        hint = f" {DIM_C}← → navegar  Q sair{RESET}"
        tab_line += " " * (TOTAL_W - sum(len(n)+3 for n,_ in TABS) - 22) + hint
        buf.append(tab_line)

        # ── SEP ───────────────────────────────────────────────────────────────
        buf.append(f"{goto(ROW_SEP,1)}{DIM_C}{H*TOTAL_W}{RESET}")

        # ── CONTENT ───────────────────────────────────────────────────────────
        screen_fn = TABS[tab_idx][1]
        lines     = screen_fn(sim, CONTENT_W, CONTENT_H)

        for i in range(CONTENT_H):
            row = ROW_CONTENT + i
            buf.append(goto(row, 1))
            if i < len(lines):
                # Garante que a linha não ultrapasse a largura
                buf.append(BG_BASE + lines[i] + RESET)
            else:
                buf.append(BG_BASE + " " * TOTAL_W + RESET)

        # ── FOOTER ────────────────────────────────────────────────────────────
        alert = sim.alert
        alert_c = RED if "ALERTA" in alert else (TEAL if "SUGESTÃO" in alert else GREEN)
        footer = (
            f"{goto(ROW_FOOTER,1)}{BG_HEADER}"
            f"  {alert_c}{alert[:TOTAL_W-30]:<{TOTAL_W-30}}{RESET}{BG_HEADER}"
            f"  {DIM_C}tickrate: 0.5s/tick{RESET}"
            + " " * 3 + RESET
        )
        buf.append(footer)

    sys.stdout.write("".join(buf))
    sys.stdout.flush()

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    enable_ansi()

    # Verifica tamanho do terminal
    try:
        sz = os.get_terminal_size()
        if sz.columns < TOTAL_W or sz.lines < TOTAL_H:
            print(f"\n⚠  Terminal pequeno: {sz.columns}×{sz.lines}  |  Necessário: {TOTAL_W}×{TOTAL_H}")
            print("   Redimensione a janela e tente novamente.\n")
            return
    except OSError:
        pass

    if sys.platform != "win32":
        enable_raw()

    hide_cur()
    sys.stdout.write(clr())
    sys.stdout.flush()

    sim       = Sim()
    tab_idx   = 0
    running   = True
    TICK_RATE = 0.05  # segundos

    try:
        while running:
            # Lê tecla (não bloqueante)
            key = _get_key()
            if key == "RIGHT": tab_idx = (tab_idx + 1) % len(TABS)
            elif key == "LEFT": tab_idx = (tab_idx - 1) % len(TABS)
            elif key == "Q":    running = False; break

            # Avança simulação e renderiza
            sim.step()
            render(sim, tab_idx)
            time.sleep(TICK_RATE)

    except KeyboardInterrupt:
        pass
    finally:
        if sys.platform != "win32":
            disable_raw()
        show_cur()
        sys.stdout.write(f"{goto(TOTAL_H+1,1)}{RESET}\n")
        print(f"\n{AMBER}Simulação encerrada — Sol {sim.tick//24}, Tick {sim.tick}{RESET}\n")

if __name__ == "__main__":
    main()
