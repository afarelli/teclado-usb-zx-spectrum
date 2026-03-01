# code.py — USB para ZX Spectrum / TK90X — CircuitPython 9.x
#
# Conversor de Teclado USB para Matriz de Membrana ZX Spectrum
# ============================================================
# Hardware : Raspberry Pi Pico (RP2040)
# Software : CircuitPython 9.x
#
# Pinagem:
#   GP0  (pino  1) — USB D+  (via 27Ω → USB-A pino 3)
#   GP1  (pino  2) — USB D-  (via 27Ω → USB-A pino 2)
#   GP2  (pino  4) — Row1 (entrada, via 10kΩ, vinda do TK90X)
#   GP3  (pino  5) — Row2
#   GP4  (pino  6) — Row3
#   GP5  (pino  7) — Row4
#   GP6  (pino  9) — Row5
#   GP7  (pino 10) — Row6
#   GP8  (pino 11) — Row7
#   GP9  (pino 12) — Row8
#   GP10 (pino 14) — Col1 (saída, via 1kΩ + BC547 → TK90X Col1)
#   GP11 (pino 15) — Col2
#   GP12 (pino 16) — Col3
#   GP13 (pino 17) — Col4
#   GP14 (pino 19) — Col5
#   VSYS (pino 39) — +5V (alimentação vinda do TK90X)
#   GND            — GND compartilhado com TK90X

import board
import digitalio
import usb.core
import time

# ─────────────────────────────────────────────────────────────────────────────
# Configuração dos pinos
# ─────────────────────────────────────────────────────────────────────────────

_ROW_GPIOS = (board.GP2, board.GP3, board.GP4, board.GP5,
              board.GP6, board.GP7, board.GP8, board.GP9)

_COL_GPIOS = (board.GP10, board.GP11, board.GP12, board.GP13, board.GP14)

# Pinos Row: entradas sem pull (pull-up externo já existe na placa ZX)
rows = []
for _pin in _ROW_GPIOS:
    _io = digitalio.DigitalInOut(_pin)
    _io.direction = digitalio.Direction.INPUT
    _io.pull = None
    rows.append(_io)

# Pinos Col: saídas, inicialmente False (transistor desligado = tecla solta)
cols = []
for _pin in _COL_GPIOS:
    _io = digitalio.DigitalInOut(_pin)
    _io.direction = digitalio.Direction.OUTPUT
    _io.value = False
    cols.append(_io)

# ─────────────────────────────────────────────────────────────────────────────
# Mapeamento de teclas: HID keycode → posição (row, col) na matriz ZX
#
# Matriz ZX (índice 0):
#          row0  row1  row2  row3  row4  row5  row6  row7
#  col0:    1     Q     A     0     P    CAPS  ENTER SPACE
#  col1:    2     W     S     9     O     Z     L    SYM
#  col2:    3     E     D     8     I     X     K     M
#  col3:    4     R     F     7     U     C     J     N
#  col4:    5     T     G     6     Y     V     H     B
# ─────────────────────────────────────────────────────────────────────────────

# Letras a–z: índice = HID keycode − 0x04
_LETTER = (
    (2, 0),  # a  0x04
    (7, 4),  # b  0x05
    (5, 3),  # c  0x06
    (2, 2),  # d  0x07
    (1, 2),  # e  0x08
    (2, 3),  # f  0x09
    (2, 4),  # g  0x0A
    (6, 4),  # h  0x0B
    (4, 2),  # i  0x0C
    (6, 3),  # j  0x0D
    (6, 2),  # k  0x0E
    (6, 1),  # l  0x0F
    (7, 2),  # m  0x10
    (7, 3),  # n  0x11
    (4, 1),  # o  0x12
    (4, 0),  # p  0x13
    (1, 0),  # q  0x14
    (1, 3),  # r  0x15
    (2, 1),  # s  0x16
    (1, 4),  # t  0x17
    (4, 3),  # u  0x18
    (5, 4),  # v  0x19
    (1, 1),  # w  0x1A
    (5, 2),  # x  0x1B
    (4, 4),  # y  0x1C
    (5, 1),  # z  0x1D
)

# Números 1–0: índice = HID keycode − 0x1E
_NUMBER = (
    (0, 0),  # 1  0x1E
    (0, 1),  # 2  0x1F
    (0, 2),  # 3  0x20
    (0, 3),  # 4  0x21
    (0, 4),  # 5  0x22
    (3, 4),  # 6  0x23
    (3, 3),  # 7  0x24
    (3, 2),  # 8  0x25
    (3, 1),  # 9  0x26
    (3, 0),  # 0  0x27
)

# Posições dos modificadores na matriz ZX
_CS = (5, 0)  # Caps Shift   (Row6, Col1)
_SS = (7, 1)  # Symbol Shift (Row8, Col2)

# Estado da matriz: matrix[row][col] = True quando tecla pressionada
matrix = [[False] * 5 for _ in range(8)]


# ─────────────────────────────────────────────────────────────────────────────
# Processa um relatório HID de 8 bytes e atualiza a matriz ZX
# Formato boot protocol: [modifier, 0x00, key1, key2, key3, key4, key5, key6]
# ─────────────────────────────────────────────────────────────────────────────
def process_report(report):
    # Limpa toda a matriz
    for r in matrix:
        for c in range(5):
            r[c] = False

    modifier = report[0]
    lshift = bool(modifier & 0x02)   # Left Shift  → Caps Shift
    rshift = bool(modifier & 0x20)   # Right Shift → Symbol Shift

    # Detecta se há número pressionado com Left Shift (quer símbolo via SS)
    lshift_with_number = False
    for i in range(2, 8):
        kc = report[i]
        if 0x1E <= kc <= 0x27 and lshift:
            lshift_with_number = True
            break

    for i in range(2, 8):
        kc = report[i]
        if kc == 0:
            continue

        if 0x04 <= kc <= 0x1D:
            # ── Letra a–z ────────────────────────────────────────
            r, c = _LETTER[kc - 0x04]
            matrix[r][c] = True
            if lshift:
                matrix[_CS[0]][_CS[1]] = True   # Shift+letra → CS+letra

        elif 0x1E <= kc <= 0x27:
            # ── Número 1–0 ───────────────────────────────────────
            r, c = _NUMBER[kc - 0x1E]
            matrix[r][c] = True
            if lshift:
                matrix[_SS[0]][_SS[1]] = True   # Shift+número → SS+número (símbolos)

        elif kc == 0x28:   # Enter
            matrix[6][0] = True

        elif kc == 0x2C:   # Space
            matrix[7][0] = True

        elif kc == 0x29:   # Escape → CS + Space (BREAK)
            matrix[_CS[0]][_CS[1]] = True
            matrix[7][0] = True

        elif kc in (0x2A, 0x4C):  # Backspace / Delete → CS + 0
            matrix[_CS[0]][_CS[1]] = True
            matrix[3][0] = True

        elif kc == 0x50:   # Seta ← → CS + 5
            matrix[_CS[0]][_CS[1]] = True
            matrix[0][4] = True

        elif kc == 0x51:   # Seta ↓ → CS + 6
            matrix[_CS[0]][_CS[1]] = True
            matrix[3][4] = True

        elif kc == 0x52:   # Seta ↑ → CS + 7
            matrix[_CS[0]][_CS[1]] = True
            matrix[3][3] = True

        elif kc == 0x4F:   # Seta → → CS + 8
            matrix[_CS[0]][_CS[1]] = True
            matrix[3][2] = True

        elif kc == 0x39:   # Caps Lock → Caps Shift
            matrix[_CS[0]][_CS[1]] = True

    # Modificadores standalone
    if lshift and not lshift_with_number:
        matrix[_CS[0]][_CS[1]] = True
    if rshift:
        matrix[_SS[0]][_SS[1]] = True


# ─────────────────────────────────────────────────────────────────────────────
# Atualiza as saídas Col com base no estado da matriz e nos Rows ativos
# A ULA do TK90X varre os Rows: quando um Row vai a LOW, o Pico deve
# colocar a LOW as Col correspondentes às teclas pressionadas naquele Row.
# ─────────────────────────────────────────────────────────────────────────────
def update_cols():
    for ci in range(5):
        pressed = False
        for ri in range(8):
            # Row em LOW = ULA está varrendo esta linha agora
            if not rows[ri].value and matrix[ri][ci]:
                pressed = True
                break
        # HIGH no GPIO → transistor conduz → Col vai a GND no TK90X
        cols[ci].value = pressed


# ─────────────────────────────────────────────────────────────────────────────
# Localiza o teclado USB e retorna (dispositivo, endereço_do_endpoint_IN)
# ─────────────────────────────────────────────────────────────────────────────
def find_keyboard():
    for dev in usb.core.find(find_all=True):
        try:
            cfg = dev.get_active_configuration()
            for intf in cfg:
                # Classe HID = 0x03
                if intf.bInterfaceClass != 0x03:
                    continue
                # Procura endpoint Interrupt IN (bit 7 = 1 → IN)
                for ep in intf:
                    if (ep.bmAttributes & 0x03) == 0x03 and (ep.bEndpointAddress & 0x80):
                        # Solicita protocolo boot (relatório de 8 bytes fixos)
                        try:
                            dev.ctrl_transfer(
                                0x21,                    # bmRequestType: host→device, class, interface
                                0x0B,                    # bRequest: SET_PROTOCOL
                                0,                       # wValue: 0 = boot protocol
                                intf.bInterfaceNumber,   # wIndex: número da interface
                                None                     # sem dados extras
                            )
                        except Exception:
                            pass  # Alguns teclados ignoram este comando mas funcionam mesmo assim
                        return dev, ep.bEndpointAddress
        except Exception:
            continue
    return None, None


# ─────────────────────────────────────────────────────────────────────────────
# Loop principal
# ─────────────────────────────────────────────────────────────────────────────
print("USB ZX Converter (CircuitPython) iniciando...")

kbd = None
ep_addr = None
buf = bytearray(8)

while True:

    # ── Busca teclado se não conectado ──────────────────────────────────────
    if kbd is None:
        kbd, ep_addr = find_keyboard()
        if kbd is not None:
            print("Teclado USB conectado.")
        else:
            # Sem teclado: garante matriz limpa e aguarda um pouco
            for r in matrix:
                for c in range(5):
                    r[c] = False
            update_cols()
            time.sleep(0.2)
            continue

    # ── Lê relatório HID ────────────────────────────────────────────────────
    try:
        count = kbd.read(ep_addr, buf, timeout=5)  # timeout de 5 ms
        if count and count >= 8:
            process_report(buf)
    except Exception:
        # Dispositivo desconectado ou erro de comunicação
        kbd = None
        ep_addr = None
        buf = bytearray(8)
        for r in matrix:
            for c in range(5):
                r[c] = False
        print("Teclado USB desconectado. Aguardando...")
        time.sleep(0.3)
        continue

    # ── Atualiza saídas da matriz ZX ────────────────────────────────────────
    update_cols()
