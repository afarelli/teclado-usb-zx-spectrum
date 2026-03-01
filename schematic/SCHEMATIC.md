# Esquema Elétrico — USB para ZX Spectrum / TK90X
## Conversor de Teclado USB → Matriz de Membrana

---

## 1. Lista de Componentes (BOM)

| Ref.     | Descrição                        | Valor / Modelo         | Qtd |
|----------|----------------------------------|------------------------|-----|
| U1       | Microcontrolador                 | Raspberry Pi Pico      | 1   |
| R1–R8    | Resistor de proteção (Row)       | 10 kΩ 1/4 W            | 8   |
| R9–R13   | Resistor de base (Col)           | 1 kΩ 1/4 W             | 5   |
| R14–R15  | Resistor série USB (D+/D-)       | 27 Ω 1/4 W             | 2   |
| Q1–Q5    | Transistor NPN                   | BC547 ou 2N3904        | 5   |
| J1       | Conector USB-A Fêmea             | 4 pinos, PTH            | 1   |
| J2       | Barra de pinos fêmea             | 8 vias, 2,54 mm        | 1   |
| J3       | Barra de pinos fêmea             | 5 vias, 2,54 mm        | 1   |
| —        | Protoboard ou perfboard          | 170 furos ou maior     | 1   |
| —        | Fios Dupont                      | M-M e M-F              | ~20 |

---

## 2. Por que Resistores e Transistores?

A placa do TK90X opera com lógica **5 V** (circuito da época do Z80).
O Raspberry Pi Pico opera com lógica **3,3 V** e seus pinos GPIO **não suportam 5 V diretamente**.

| Situação              | Problema                          | Solução adotada               |
|-----------------------|-----------------------------------|-------------------------------|
| Row (TK90X → Pico)    | Sinal de 5 V no GPIO de 3,3 V     | Resistor série 10 kΩ (limitação de corrente via diodo de clamp interno) |
| Col (Pico → TK90X)    | GPIO de 3,3 V precisa drenar 5 V  | Transistor NPN em coletor aberto |

### Funcionamento do transistor (saída Col)
```
                 +5V (trilho TK90X)
                  │
                  │  [10 kΩ pull-up já existente na placa ZX]
                  │
TK90X Col1 ───────┼────────────── Coletor (Q1)
                               Base (Q1) ──[1 kΩ]── GP10 (Pico)
                               Emissor (Q1) ──────── GND

  GP10 = HIGH (3,3V)  →  Q1 conduz  →  Col1 vai a GND  →  tecla PRESSIONADA
  GP10 = LOW  (0V)    →  Q1 bloqueado →  Col1 fica em +5V →  tecla SOLTA
```

---

## 3. Mapeamento de Pinos

### 3.1 Alimentação

| Origem         | Destino                   | Observação                        |
|----------------|---------------------------|-----------------------------------|
| TK90X +5 V     | Pico VSYS (pino físico 39)| Alimenta o Pico                   |
| TK90X +5 V     | USB-A pino 1 (VBUS)       | Alimenta o teclado USB            |
| TK90X GND      | Pico GND (qualquer)       | GND compartilhado                 |
| TK90X GND      | USB-A pino 4 (GND)        | GND do teclado USB                |

### 3.2 USB Host (PIO-USB via GP0/GP1)

| Pico GPIO | Pino Físico | Via       | USB-A Pino | Sinal |
|-----------|-------------|-----------|------------|-------|
| GP0       | 1           | [27 Ω]    | 3          | D+    |
| GP1       | 2           | [27 Ω]    | 2          | D-    |

> **Nota:** A porta micro-USB do Pico **continua livre** para programação.
> O PIO-USB usa os pinos GP0 e GP1 via software (PIO state machine).

### 3.3 Entradas Row (TK90X → Pico, 5 V → 3,3 V)

| Conector TK90X | Sinal | Resistor | Pico GPIO | Pino Físico |
|----------------|-------|----------|-----------|-------------|
| J2 pino 1      | Row1  | 10 kΩ    | GP2       | 4           |
| J2 pino 2      | Row2  | 10 kΩ    | GP3       | 5           |
| J2 pino 3      | Row3  | 10 kΩ    | GP4       | 6           |
| J2 pino 4      | Row4  | 10 kΩ    | GP5       | 7           |
| J2 pino 5      | Row5  | 10 kΩ    | GP6       | 9           |
| J2 pino 6      | Row6  | 10 kΩ    | GP7       | 10          |
| J2 pino 7      | Row7  | 10 kΩ    | GP8       | 11          |
| J2 pino 8      | Row8  | 10 kΩ    | GP9       | 12          |

### 3.4 Saídas Col (Pico → TK90X, via transistor NPN)

| Pico GPIO | Pino Físico | Resistor Base | Transistor | Coletor → TK90X |
|-----------|-------------|---------------|------------|-----------------|
| GP10      | 14          | 1 kΩ          | Q1 (BC547) | J3 pino 1 (Col1)|
| GP11      | 15          | 1 kΩ          | Q2 (BC547) | J3 pino 2 (Col2)|
| GP12      | 16          | 1 kΩ          | Q3 (BC547) | J3 pino 3 (Col3)|
| GP13      | 17          | 1 kΩ          | Q4 (BC547) | J3 pino 4 (Col4)|
| GP14      | 19          | 1 kΩ          | Q5 (BC547) | J3 pino 5 (Col5)|

---

## 4. Diagrama ASCII Completo

```
                ┌─────────────────────────────────────────────────┐
                │           RASPBERRY PI PICO                     │
                │                                                 │
 USB-A Fêmea    │                                                 │
 ┌──────────┐   │  GP0 (pino 1) ──[27Ω]──────────────────────── D+ (USB-A pino 3)
 │ VBUS(+5V)│◄──┼── VSYS (pino 39) ◄───────────────────────── +5V TK90X
 │ D-       │◄──┼── GP1 (pino 2) ──[27Ω]──────────────────── D- (USB-A pino 2)
 │ D+       │◄──┼── (ver acima)                               │
 │ GND      │◄──┼── GND ◄─────────────────────────────────── GND TK90X
 └──────────┘   │                                                 │
                │  GP2  (pino  4) ◄──[10kΩ]◄──── TK90X Row1      │
                │  GP3  (pino  5) ◄──[10kΩ]◄──── TK90X Row2      │
                │  GP4  (pino  6) ◄──[10kΩ]◄──── TK90X Row3      │
                │  GP5  (pino  7) ◄──[10kΩ]◄──── TK90X Row4      │
                │  GP6  (pino  9) ◄──[10kΩ]◄──── TK90X Row5      │
                │  GP7  (pino 10) ◄──[10kΩ]◄──── TK90X Row6      │
                │  GP8  (pino 11) ◄──[10kΩ]◄──── TK90X Row7      │
                │  GP9  (pino 12) ◄──[10kΩ]◄──── TK90X Row8      │
                │                                                 │
                │  GP10 (pino 14) ──[1kΩ]──► Base Q1 (BC547)     │
                │  GP11 (pino 15) ──[1kΩ]──► Base Q2 (BC547)     │
                │  GP12 (pino 16) ──[1kΩ]──► Base Q3 (BC547)     │
                │  GP13 (pino 17) ──[1kΩ]──► Base Q4 (BC547)     │
                │  GP14 (pino 19) ──[1kΩ]──► Base Q5 (BC547)     │
                └─────────────────────────────────────────────────┘

  Transistores NPN (Q1–Q5), todos idênticos:

    TK90X Colx ──── Coletor (BC547)
                    Base ──[1kΩ]── GPxx (Pico)
                    Emissor ─────── GND
```

---

## 5. Matriz do Teclado (referência)

```
           Row1  Row2  Row3  Row4  Row5  Row6  Row7  Row8
           (GP2) (GP3) (GP4) (GP5) (GP6) (GP7) (GP8) (GP9)
Col1(GP10):  1     Q     A     0     P    CAPS  ENTER  SPACE
Col2(GP11):  2     W     S     9     O     Z     L     SYM
Col3(GP12):  3     E     D     8     I     X     K     M
Col4(GP13):  4     R     F     7     U     C     J     N
Col5(GP14):  5     T     G     6     Y     V     H     B
```

> **CAPS** = Caps Shift (pino Row6/Col1)
> **SYM**  = Symbol Shift (pino Row8/Col2)

---

## 6. Notas de Montagem

1. **GND comum**: O GND do Pico, do TK90X e do teclado USB devem estar todos ligados ao mesmo ponto de referência.
2. **Sequência de montagem recomendada**: solde os resistores e transistores primeiro, depois conecte os fios Dupont ao Pico, por último ligue ao TK90X.
3. **Não conecte o teclado USB enquanto a montagem não estiver completa**: evite curto-circuito na alimentação.
4. **Os pull-ups de 10 kΩ para as linhas Col** já existem na placa do TK90X — não adicione mais.
5. **Consumo estimado**: Pico ≈ 25 mA + teclado USB ≈ 100 mA = ~130 mA total. A fonte original do TK90X suporta isso tranquilamente.
