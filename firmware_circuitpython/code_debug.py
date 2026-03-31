# code_debug.py — Diagnóstico do Conversor USB → ZX Spectrum
#
# Como usar:
#   1. Copie boot_debug.py para o CIRCUITPY renomeando para boot.py
#   2. Copie este arquivo para o CIRCUITPY renomeando para code.py
#   3. Reinicie o Pico (aperte o botão RESET ou desconecte/reconecte)
#   4. Aguarde o teste inicial dos LEDs (Fase 1)
#   5. Pressione algumas teclas no teclado USB
#   6. Reconecte o Pico ao PC e abra o arquivo debug_log.txt no CIRCUITPY
#
# O LED interno do Pico (plaquinha) também fornece feedback visual:
#   - Piscando devagar (0.5s) = sem teclado detectado
#   - Piscando rápido (0.05s) = teclado encontrado!
#   - Aceso fixo = tecla pressionada

import board
import digitalio
import usb.core
import time

LOG_FILE = "/debug_log.txt"

# ── LED interno do Pico (sem necessidade de componentes externos) ──────────────
onboard = digitalio.DigitalInOut(board.LED)
onboard.direction = digitalio.Direction.OUTPUT

# ── Pinos Col (GP10–GP14) ──────────────────────────────────────────────────────
COL_GPIOS = (board.GP10, board.GP11, board.GP12, board.GP13, board.GP14)
cols = []
for _pin in COL_GPIOS:
    _io = digitalio.DigitalInOut(_pin)
    _io.direction = digitalio.Direction.OUTPUT
    _io.value = False
    cols.append(_io)

# ── Pinos Row (GP2–GP9) — lidos mas não usados no debug ──────────────────────
ROW_GPIOS = (board.GP2, board.GP3, board.GP4, board.GP5,
             board.GP6, board.GP7, board.GP8, board.GP9)
rows = []
for _pin in ROW_GPIOS:
    _io = digitalio.DigitalInOut(_pin)
    _io.direction = digitalio.Direction.INPUT
    _io.pull = None
    rows.append(_io)


# ── Helpers ────────────────────────────────────────────────────────────────────
def blink(n, interval):
    for _ in range(n):
        onboard.value = True
        time.sleep(interval)
        onboard.value = False
        time.sleep(interval)


def log(msg):
    """Imprime no serial E salva no arquivo de log."""
    print(msg)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(msg + "\n")
    except Exception as e:
        print("(erro ao salvar log:", e, ")")


def cols_off():
    for c in cols:
        c.value = False


# ── Mapa de keycodes HID para nomes legíveis ───────────────────────────────────
HID_NAMES = {
    0x04: "A",   0x05: "B",   0x06: "C",   0x07: "D",   0x08: "E",
    0x09: "F",   0x0A: "G",   0x0B: "H",   0x0C: "I",   0x0D: "J",
    0x0E: "K",   0x0F: "L",   0x10: "M",   0x11: "N",   0x12: "O",
    0x13: "P",   0x14: "Q",   0x15: "R",   0x16: "S",   0x17: "T",
    0x18: "U",   0x19: "V",   0x1A: "W",   0x1B: "X",   0x1C: "Y",
    0x1D: "Z",
    0x1E: "1",   0x1F: "2",   0x20: "3",   0x21: "4",   0x22: "5",
    0x23: "6",   0x24: "7",   0x25: "8",   0x26: "9",   0x27: "0",
    0x28: "ENTER",   0x29: "ESC",     0x2A: "BACKSPACE",
    0x2C: "SPACE",   0x39: "CAPSLOCK",
    0x4F: "SETA_DIR", 0x50: "SETA_ESQ",
    0x51: "SETA_BAI", 0x52: "SETA_CIM",
    0x4C: "DELETE",
}

# ══════════════════════════════════════════════════════════════════════════════
# FASE 1 — Teste dos pinos Col (GP10–GP14)
# Cada LED deve acender por 0,4s em sequência.
# Se algum não acender, verifique a ligação daquele GPIO.
# ══════════════════════════════════════════════════════════════════════════════
log("=" * 40)
log("DIAGNOSTICO USB → ZX SPECTRUM")
log("=" * 40)
log("")
log("FASE 1: Testando saidas Col (GP10-GP14)")
log("Cada LED deve acender por 0.4s em sequencia.")

for i, col in enumerate(cols):
    log(f"  -> GP{10 + i} (Col{i + 1}) HIGH")
    col.value = True
    time.sleep(0.4)
    col.value = False
    time.sleep(0.15)

log("Fase 1 OK. Se algum LED nao acendeu, verifique a fiacao daquele pino.")
log("")

# ══════════════════════════════════════════════════════════════════════════════
# FASE 2 — Detecção do teclado USB
# Tenta encontrar um dispositivo HID em GP0/GP1 por até 8 segundos.
# ══════════════════════════════════════════════════════════════════════════════
log("FASE 2: Buscando teclado USB (GP0=D+, GP1=D-)...")
log("Aguarde ate 8 segundos...")

kbd = None
ep_addr = None

for tentativa in range(16):
    for dev in usb.core.find(find_all=True):
        try:
            cfg = dev.get_active_configuration()
            for intf in cfg:
                if intf.bInterfaceClass != 0x03:
                    continue
                for ep in intf:
                    if (ep.bmAttributes & 0x03) == 0x03 and (ep.bEndpointAddress & 0x80):
                        try:
                            dev.ctrl_transfer(0x21, 0x0B, 0, intf.bInterfaceNumber, None)
                        except Exception:
                            pass
                        kbd = dev
                        ep_addr = ep.bEndpointAddress
                        break
                if kbd:
                    break
        except Exception:
            continue
        if kbd:
            break
    if kbd:
        break
    onboard.value = not onboard.value  # pisca enquanto busca
    time.sleep(0.5)

onboard.value = False

if kbd:
    log(f"TECLADO ENCONTRADO! Endpoint IN: 0x{ep_addr:02X}")
    log("LED interno piscara rapidamente 5x como confirmacao.")
    blink(5, 0.05)
else:
    log("ERRO: Teclado NAO encontrado!")
    log("")
    log("Possiveis causas:")
    log("  - GP0 nao conectado ao D+ (fio verde) via 27 ohm")
    log("  - GP1 nao conectado ao D- (fio branco) via 27 ohm")
    log("  - VBUS (vermelho) sem +5V")
    log("  - GND (preto) desconectado")
    log("  - boot.py nao tem usb_host.Port(board.GP0, board.GP1)")
    log("  - Teclado USB com hub interno (tente outro teclado)")
    log("")
    log("O programa encerrara agora. Corrija e reinicie.")
    blink(10, 0.5)
    raise SystemExit

log("")

# ══════════════════════════════════════════════════════════════════════════════
# FASE 3 — Leitura e registro de teclas
# Pressione teclas no teclado USB.
# Cada tecla sera registrada no log e um LED acendera como feedback.
# O teste dura 60 segundos ou ate voce reiniciar o Pico.
# ══════════════════════════════════════════════════════════════════════════════
log("FASE 3: Aguardando teclas por 60 segundos...")
log("Pressione qualquer tecla no teclado USB.")
log("Estado dos Row pins (devem estar em GND para o teste com LEDs):")

for i, r in enumerate(rows):
    estado = "LOW (GND)" if not r.value else "HIGH (flutuando ou +5V)"
    log(f"  GP{2 + i} (Row{i + 1}): {estado}")

log("")

buf = bytearray(8)
last_buf = bytearray(8)
deadline = time.monotonic() + 60
count_keys = 0

while time.monotonic() < deadline:
    try:
        n = kbd.read(ep_addr, buf, timeout=50)
        if n and buf != last_buf:
            mod = buf[0]
            keycodes = [buf[i] for i in range(2, 8) if buf[i] != 0]

            mods = []
            if mod & 0x01: mods.append("LCTRL")
            if mod & 0x02: mods.append("LSHIFT")
            if mod & 0x04: mods.append("LALT")
            if mod & 0x10: mods.append("RCTRL")
            if mod & 0x20: mods.append("RSHIFT")
            if mod & 0x40: mods.append("RALT")

            if keycodes or mods:
                names = [HID_NAMES.get(k, f"0x{k:02X}") for k in keycodes]
                tecla_str = "+".join(mods + names)
                count_keys += 1
                log(f"[{count_keys:03d}] modifier=0x{mod:02X} keycodes={[hex(k) for k in keycodes]} -> {tecla_str}")

                # Feedback visual: acende o LED da Col correspondente à primeira tecla
                cols_off()
                if keycodes:
                    col_idx = keycodes[0] % 5
                    cols[col_idx].value = True
                onboard.value = True

            else:
                # Todas as teclas soltas
                cols_off()
                onboard.value = False

            last_buf[:] = buf

    except Exception as e:
        err = str(e).lower()
        if "timeout" not in err and "timed out" not in err:
            log(f"Erro de leitura USB: {e}")
            time.sleep(0.1)

cols_off()
onboard.value = False
log("")
log(f"FASE 3 concluida. {count_keys} eventos de tecla registrados.")
log("")
log("=" * 40)
log("FIM DO DIAGNOSTICO")
log("Reconecte o Pico ao PC e abra o arquivo debug_log.txt")
log("=" * 40)
