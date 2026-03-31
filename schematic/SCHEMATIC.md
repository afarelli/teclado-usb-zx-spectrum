# Esquema Elétrico — USB para ZX Spectrum / TK90X
## Conversor de Teclado USB → Matriz de Membrana

---

## 1. Lista de Componentes (BOM)

| Ref.     | Descrição                        | Valor / Modelo         | Qtd |
|----------|----------------------------------|------------------------|-----|
| U1       | Microcontrolador                 | Raspberry Pi Pico      | 1   |
| R1–R8    | Resistor de proteção (Row)       | 10 kΩ 1/4 W            | 8   |
| R9–R10   | Resistor série USB (D+/D-)       | 27 Ω 1/4 W             | 2   |
| D1–D5    | Diodo de sinal                   | 1N4148                 | 5   |
| J1       | Conector USB-A Fêmea             | 4 pinos, PTH            | 1   |
| J2       | Barra de pinos fêmea             | 8 vias, 2,54 mm        | 1   |
| J3       | Barra de pinos fêmea             | 5 vias, 2,54 mm        | 1   |
| —        | Protoboard ou perfboard          | 170 furos ou maior     | 1   |
| —        | Fios Dupont                      | M-M e M-F              | ~20 |

---

## 2. Por que Resistores e Diodos?

A placa do TK90X opera com lógica **5 V** (circuito da época do Z80).
O Raspberry Pi Pico opera com lógica **3,3 V** e seus pinos GPIO **não suportam 5 V diretamente**.

| Situação              | Problema                          | Solução adotada               |
|-----------------------|-----------------------------------|-------------------------------|
| Row (TK90X → Pico)    | Sinal de 5 V no GPIO de 3,3 V     | Resistor série 10 kΩ (limitação de corrente via diodo de clamp interno) |
| Col (Pico → TK90X)    | GPIO de 3,3 V não pode ver 5 V    | Diodo 1N4148 em série (bloqueia a tensão alta no lado do ZX) |

### Funcionamento do diodo (saída Col)
```
                 +5V (trilho TK90X)
                  │
                  │  [10 kΩ pull-up já existente na placa ZX]
                  │
TK90X Col1 ───────┼──── Anodo ►| Catodo ──── GP10 (Pico)
                       (1N4148)

  GP10 = LOW  (0V)    →  diodo conduz  →  Col1 vai a ~0,7V  →  tecla PRESSIONADA
  GP10 = HIGH (3,3V)  →  diodo bloqueado → Col1 fica em ~4V  →  tecla SOLTA

  O pino GP10 permanece sempre em 3,3V ou 0V — nunca vê os 5V do ZX.
  Os ~4V quando solto ficam do lado do anodo (ZX), não chegam ao Pico.
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

### 3.4 Saídas Col (Pico → TK90X, via diodo 1N4148)

| Pico GPIO | Pino Físico | Catodo (Pico) | Diodo  | Anodo → TK90X   |
|-----------|-------------|---------------|--------|-----------------|
| GP10      | 14          | GP10          | D1     | J3 pino 1 (Col1)|
| GP11      | 15          | GP11          | D2     | J3 pino 2 (Col2)|
| GP12      | 16          | GP12          | D3     | J3 pino 3 (Col3)|
| GP13      | 17          | GP13          | D4     | J3 pino 4 (Col4)|
| GP14      | 19          | GP14          | D5     | J3 pino 5 (Col5)|

---

## 4. Diagrama ASCII Completo

```
                ┌─────────────────────────────────────────────────┐
                │           RASPBERRY PI PICO                     │
                │                                                 │
 USB-A Fêmea    │                                                 │
 ┌──────────┐   │  GP0 (pino 1) ───────────[27Ω]──────────────────── D+ (USB-A pino 3)
 │ VBUS(+5V)│◄──┼── VSYS (pino 39) ◄──────────────────────────────── +5V TK90X
 │ D-       │◄──┼── GP1 (pino 2) ──────────[27Ω]──────────────────── D- (USB-A pino 2)
 │ D+       │◄──┼── (ver acima)                                   │
 │ GND      │◄──┼── GND ◄─────────────────────────────────────────── GND TK90X
 └──────────┘   │                                                 │
                │  GP2  (pino  4) ◄──[10kΩ]◄──── TK90X Row1       │
                │  GP3  (pino  5) ◄──[10kΩ]◄──── TK90X Row2       │
                │  GP4  (pino  6) ◄──[10kΩ]◄──── TK90X Row3       │
                │  GP5  (pino  7) ◄──[10kΩ]◄──── TK90X Row4       │
                │  GP6  (pino  9) ◄──[10kΩ]◄──── TK90X Row5       │
                │  GP7  (pino 10) ◄──[10kΩ]◄──── TK90X Row6       │
                │  GP8  (pino 11) ◄──[10kΩ]◄──── TK90X Row7       │
                │  GP9  (pino 12) ◄──[10kΩ]◄──── TK90X Row8       │
                │                                                 │
                │  GP10 (pino 14) ──── Catodo ►| Anodo ──── TK90X Col1 │
                │  GP11 (pino 15) ──── Catodo ►| Anodo ──── TK90X Col2 │
                │  GP12 (pino 16) ──── Catodo ►| Anodo ──── TK90X Col3 │
                │  GP13 (pino 17) ──── Catodo ►| Anodo ──── TK90X Col4 │
                │  GP14 (pino 19) ──── Catodo ►| Anodo ──── TK90X Col5 │
                └─────────────────────────────────────────────────┘

  Diodos 1N4148 (D1–D5), todos idênticos:

    GPxx (Pico) ──── Catodo ►| Anodo ──── TK90X Colx

  Identificando a polaridade do 1N4148:
    A faixa/listra cinza ou preta na extremidade do diodo = CATODO (lado do Pico)
    O lado sem faixa = ANODO (lado do TK90X)
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
2. **Sequência de montagem recomendada**: solde os resistores e diodos primeiro, depois conecte os fios Dupont ao Pico, por último ligue ao TK90X.
3. **Não conecte o teclado USB enquanto a montagem não estiver completa**: evite curto-circuito na alimentação.
4. **Os pull-ups de 10 kΩ para as linhas Col** já existem na placa do TK90X — não adicione mais.
5. **Consumo estimado**: Pico ≈ 25 mA + teclado USB ≈ 100 mA = ~130 mA total. A fonte original do TK90X suporta isso tranquilamente.
