/*
 * usb_zx_converter.ino
 *
 * Conversor de Teclado USB para Matriz ZX Spectrum / TK90X
 * =========================================================
 * Hardware : Raspberry Pi Pico (RP2040)
 * IDE      : Arduino IDE 2.x
 * Core     : arduino-pico (Earlephilhower) v3.x
 * USB Stack: Adafruit TinyUSB (modo Host via PIO-USB)
 *
 * Pinagem:
 *   GP0  (pino  1) — USB D+  (via 27Ω → USB-A pino 3)
 *   GP1  (pino  2) — USB D-  (via 27Ω → USB-A pino 2)
 *   GP2  (pino  4) — Row1 (entrada, via 10kΩ, vinda do TK90X)
 *   GP3  (pino  5) — Row2
 *   GP4  (pino  6) — Row3
 *   GP5  (pino  7) — Row4
 *   GP6  (pino  9) — Row5
 *   GP7  (pino 10) — Row6
 *   GP8  (pino 11) — Row7
 *   GP9  (pino 12) — Row8
 *   GP10 (pino 14) — Col1 (saída, via 1kΩ + transistor BC547)
 *   GP11 (pino 15) — Col2
 *   GP12 (pino 16) — Col3
 *   GP13 (pino 17) — Col4
 *   GP14 (pino 19) — Col5
 *   VSYS (pino 39) — +5V (alimentação vinda do TK90X)
 *   GND            — GND compartilhado com TK90X
 *
 * ATENÇÃO: O clock do sistema DEVE estar em 120 MHz para o PIO-USB.
 *          Selecione em: Ferramentas > Velocidade da CPU > 120 MHz
 */

// ---------------------------------------------------------------------------
// Includes
// ---------------------------------------------------------------------------
#include "Adafruit_TinyUSB.h"
#include "pio_usb.h"

// ---------------------------------------------------------------------------
// Definições de pinos
// ---------------------------------------------------------------------------
static const uint8_t ROW_PINS[8] = { 2, 3, 4, 5, 6, 7, 8, 9 };
static const uint8_t COL_PINS[5] = { 10, 11, 12, 13, 14 };

// Posições fixas na matriz
#define CS_ROW 5   // Caps Shift   — Row6 (índice 0)
#define CS_COL 0   // Caps Shift   — Col1 (índice 0)
#define SS_ROW 7   // Symbol Shift — Row8
#define SS_COL 1   // Symbol Shift — Col2

// ---------------------------------------------------------------------------
// Estrutura de posição na matriz ZX
// ---------------------------------------------------------------------------
struct ZXKey {
  uint8_t row;  // 0–7  (Row1–Row8)
  uint8_t col;  // 0–4  (Col1–Col5)
};

#define NO_KEY { 0xFF, 0xFF }

// ---------------------------------------------------------------------------
// Mapeamento: keycode HID → posição na matriz ZX
//
// Índice = (keycode HID - 0x04)  para letras  a–z  (0x04–0x1D)
// Índice = (keycode HID - 0x1E)  para números 1–0  (0x1E–0x27)
//
// Matriz ZX (row × col):
//         Row0  Row1  Row2  Row3  Row4  Row5  Row6  Row7
//  Col0:   1     Q     A     0     P    CAPS  Enter Space
//  Col1:   2     W     S     9     O     Z     L    Sym
//  Col2:   3     E     D     8     I     X     K     M
//  Col3:   4     R     F     7     U     C     J     N
//  Col4:   5     T     G     6     Y     V     H     B
// ---------------------------------------------------------------------------

// Letras a–z (HID 0x04–0x1D), indexadas como [keycode - 0x04]
static const ZXKey LETTER_MAP[26] = {
  {2, 0},  // a → Row3, Col1
  {7, 4},  // b → Row8, Col5
  {5, 3},  // c → Row6, Col4
  {2, 2},  // d → Row3, Col3
  {1, 2},  // e → Row2, Col3
  {2, 3},  // f → Row3, Col4
  {2, 4},  // g → Row3, Col5
  {6, 4},  // h → Row7, Col5
  {4, 2},  // i → Row5, Col3
  {6, 3},  // j → Row7, Col4
  {6, 2},  // k → Row7, Col3
  {6, 1},  // l → Row7, Col2
  {7, 2},  // m → Row8, Col3
  {7, 3},  // n → Row8, Col4
  {4, 1},  // o → Row5, Col2
  {4, 0},  // p → Row5, Col1
  {1, 0},  // q → Row2, Col1
  {1, 3},  // r → Row2, Col4
  {2, 1},  // s → Row3, Col2
  {1, 4},  // t → Row2, Col5
  {4, 3},  // u → Row5, Col4
  {5, 4},  // v → Row6, Col5
  {1, 1},  // w → Row2, Col2
  {5, 2},  // x → Row6, Col3
  {4, 4},  // y → Row5, Col5
  {5, 1},  // z → Row6, Col2
};

// Números 1–0 (HID 0x1E–0x27), indexados como [keycode - 0x1E]
// Ordem HID: 1,2,3,4,5,6,7,8,9,0
static const ZXKey NUMBER_MAP[10] = {
  {0, 0},  // 1 → Row1, Col1
  {0, 1},  // 2 → Row1, Col2
  {0, 2},  // 3 → Row1, Col3
  {0, 3},  // 4 → Row1, Col4
  {0, 4},  // 5 → Row1, Col5
  {3, 4},  // 6 → Row4, Col5
  {3, 3},  // 7 → Row4, Col4
  {3, 2},  // 8 → Row4, Col3
  {3, 1},  // 9 → Row4, Col2
  {3, 0},  // 0 → Row4, Col1
};

// ---------------------------------------------------------------------------
// Estado da matriz (volatile porque é atualizado no callback de interrupção USB)
// ---------------------------------------------------------------------------
volatile bool matrix[8][5];

// ---------------------------------------------------------------------------
// Objeto USB Host
// ---------------------------------------------------------------------------
Adafruit_USBH_Host USBHost;

// ---------------------------------------------------------------------------
// Funções auxiliares
// ---------------------------------------------------------------------------
static inline void pressKey(uint8_t row, uint8_t col) {
  if (row < 8 && col < 5) {
    matrix[row][col] = true;
  }
}

// Processa o relatório HID do teclado (protocolo boot, 8 bytes)
static void processKbdReport(hid_keyboard_report_t const* report) {
  // Limpa a matriz
  memset((void*)matrix, 0, sizeof(matrix));

  bool lshift = (report->modifier & 0x02) != 0;  // Left Shift
  bool rshift = (report->modifier & 0x20) != 0;  // Right Shift

  // Verifica se existe número pressionado junto com Left Shift
  // Nesse caso queremos SS+número (símbolos), não CS
  bool lshift_with_number = false;
  for (int i = 0; i < 6; i++) {
    uint8_t kc = report->keycode[i];
    if (kc >= 0x1E && kc <= 0x27 && lshift) {
      lshift_with_number = true;
    }
  }

  // Processa cada keycode pressionado
  for (int i = 0; i < 6; i++) {
    uint8_t kc = report->keycode[i];
    if (kc == 0x00) continue;  // sem tecla

    if (kc >= 0x04 && kc <= 0x1D) {
      // ── Letras a–z ──────────────────────────────────────────
      ZXKey k = LETTER_MAP[kc - 0x04];
      pressKey(k.row, k.col);
      if (lshift) pressKey(CS_ROW, CS_COL);  // Shift+letra → CS+letra

    } else if (kc >= 0x1E && kc <= 0x27) {
      // ── Números 0–9 ─────────────────────────────────────────
      ZXKey k = NUMBER_MAP[kc - 0x1E];
      pressKey(k.row, k.col);
      if (lshift) pressKey(SS_ROW, SS_COL);  // Shift+número → SS+número (símbolos)

    } else {
      // ── Teclas especiais ────────────────────────────────────
      switch (kc) {
        case HID_KEY_ENTER:
          pressKey(6, 0);
          break;

        case HID_KEY_SPACE:
          pressKey(7, 0);
          break;

        case HID_KEY_ESCAPE:
          // BREAK no ZX Spectrum = CS + Space
          pressKey(CS_ROW, CS_COL);
          pressKey(7, 0);
          break;

        case HID_KEY_BACKSPACE:
        case HID_KEY_DELETE:
          // DELETE no ZX = CS + 0
          pressKey(CS_ROW, CS_COL);
          pressKey(3, 0);
          break;

        case HID_KEY_ARROW_LEFT:
          // Seta esquerda = CS + 5
          pressKey(CS_ROW, CS_COL);
          pressKey(0, 4);
          break;

        case HID_KEY_ARROW_DOWN:
          // Seta abaixo = CS + 6
          pressKey(CS_ROW, CS_COL);
          pressKey(3, 4);
          break;

        case HID_KEY_ARROW_UP:
          // Seta acima = CS + 7
          pressKey(CS_ROW, CS_COL);
          pressKey(3, 3);
          break;

        case HID_KEY_ARROW_RIGHT:
          // Seta direita = CS + 8
          pressKey(CS_ROW, CS_COL);
          pressKey(3, 2);
          break;

        case HID_KEY_TAB:
          // TAB: sem equivalente direto — mapeado como CS+I (função Inverse Video no BASIC)
          // Pode ser remapeado conforme necessidade
          pressKey(CS_ROW, CS_COL);
          pressKey(4, 2);
          break;

        case HID_KEY_CAPS_LOCK:
          // Caps Lock do PC → Caps Shift do ZX
          pressKey(CS_ROW, CS_COL);
          break;

        default:
          break;
      }
    }
  }

  // ── Modificadores standalone ──────────────────────────────────
  // Left Shift sem número → apenas CS
  if (lshift && !lshift_with_number) {
    pressKey(CS_ROW, CS_COL);
  }
  // Right Shift → SS
  if (rshift) {
    pressKey(SS_ROW, SS_COL);
  }
}

// ---------------------------------------------------------------------------
// Atualiza as saídas de Col conforme o estado atual da matriz
// Lê quais Row estão em nível LOW (ULA do TK90X fazendo varredura)
// e, para cada Col, decide se deve acionar o transistor.
// ---------------------------------------------------------------------------
static void updateMatrix() {
  for (int col = 0; col < 5; col++) {
    bool press = false;
    for (int row = 0; row < 8; row++) {
      // Row em LOW = ULA está varrendo essa linha
      if (!digitalRead(ROW_PINS[row]) && matrix[row][col]) {
        press = true;
        break;
      }
    }
    // HIGH no GPIO → transistor conduz → Col vai a GND no TK90X (tecla "pressionada")
    digitalWrite(COL_PINS[col], press ? HIGH : LOW);
  }
}

// ---------------------------------------------------------------------------
// setup()
// ---------------------------------------------------------------------------
void setup() {
  // Configura pinos Row como entradas sem pull (pull-up já existe na placa ZX)
  for (int i = 0; i < 8; i++) {
    pinMode(ROW_PINS[i], INPUT);
  }

  // Configura pinos Col como saídas, inicialmente baixo (transistores desligados)
  for (int i = 0; i < 5; i++) {
    pinMode(COL_PINS[i], OUTPUT);
    digitalWrite(COL_PINS[i], LOW);
  }

  // Limpa matriz de estado
  memset((void*)matrix, 0, sizeof(matrix));

  // Configura PIO-USB no GP0 (D+) e GP1 (D-)
  // O clock DEVE estar em 120 MHz (configurar via Tools > CPU Speed no Arduino IDE)
  static pio_usb_configuration_t pio_cfg = PIO_USB_DEFAULT_CONFIG;
  pio_cfg.pin_dp = 0;  // GP0 = D+  (GP1 = D- automaticamente = D+ + 1)

  USBHost.configure_pio_usb(1, &pio_cfg);
  USBHost.begin(1);
}

// ---------------------------------------------------------------------------
// loop()
// ---------------------------------------------------------------------------
void loop() {
  // Processa eventos USB (callbacks TinyUSB)
  USBHost.task();

  // Atualiza a matriz do ZX em tempo real
  updateMatrix();
}

// ---------------------------------------------------------------------------
// Callbacks TinyUSB — Host HID
// ---------------------------------------------------------------------------

// Chamado quando um dispositivo HID é conectado
void tuh_hid_mount_cb(uint8_t dev_addr, uint8_t instance,
                      uint8_t const* desc_report, uint16_t desc_len) {
  (void)desc_report;
  (void)desc_len;
  // Solicita protocolo boot (formato de relatório fixo e simples)
  tuh_hid_set_protocol(dev_addr, instance, HID_PROTOCOL_BOOT);
  // Inicia a recepção de relatórios
  tuh_hid_receive_report(dev_addr, instance);
}

// Chamado quando um dispositivo HID é desconectado
void tuh_hid_umount_cb(uint8_t dev_addr, uint8_t instance) {
  (void)dev_addr;
  (void)instance;
  // Limpa a matriz para evitar teclas "presas"
  memset((void*)matrix, 0, sizeof(matrix));
}

// Chamado quando um relatório HID é recebido
void tuh_hid_report_received_cb(uint8_t dev_addr, uint8_t instance,
                                 uint8_t const* report, uint16_t len) {
  if (tuh_hid_get_protocol(dev_addr, instance) == HID_PROTOCOL_BOOT &&
      len >= sizeof(hid_keyboard_report_t)) {
    processKbdReport((hid_keyboard_report_t const*)report);
  }
  // Solicita o próximo relatório
  tuh_hid_receive_report(dev_addr, instance);
}
