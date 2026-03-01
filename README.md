# teclado-usb-zx-spectrum
Um projeto para utilizarmos um teclado USB em um ZX Spectrum ou um TK90X, com o auxílio de um Raspberry PI PICO.

Abaixo, temos duas partes da construção: o tutorial sobre o Esquema Elétrico (encontrado em schematic/schematic.md), e o tutorial para Circuit Python (docs/tutorial_circuitpython.md). Caso prefira utilizar o Arduino IDE, siga o tutorial em: docs/tutorial.md.

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


---
---

# Tutorial: Instalação via CircuitPython (Arrastar e Soltar)
## Conversor USB → ZX Spectrum / TK90X — Sem necessidade de IDE

---

## Por que CircuitPython?

| | CircuitPython | Arduino IDE |
|---|---|---|
| Instalação de software | Nenhuma | Arduino IDE + bibliotecas |
| Envio do firmware | Arrastar arquivos (como pendrive) | Compilar e fazer upload |
| Edição do código | Qualquer editor de texto | Arduino IDE |
| Dificuldade | Fácil | Moderada |
| Velocidade de resposta | Boa (suficiente para teclado) | Ótima |

> **O hardware (circuito elétrico) é IDÊNTICO** ao descrito em `schematic/SCHEMATIC.md`.
> A diferença é apenas no software instalado no Pico.

---

## O que você vai precisar

- Raspberry Pi Pico
- Cabo **micro-USB** (para conectar o Pico ao PC)
- PC com qualquer sistema operacional (Windows, Linux, macOS)
- Um gerenciador de arquivos (Explorador de Arquivos do Windows, Nautilus, Finder, etc.)
- Editor de texto simples (Bloco de Notas, Notepad++, gedit, nano — qualquer um)

---

## Visão Geral do Processo

```
Passo 1: Baixar o CircuitPython (.uf2)
    ↓
Passo 2: Entrar no modo de programação (BOOTSEL)
    ↓
Passo 3: Arrastar o .uf2 para o Pico → Pico vira pendrive "CIRCUITPY"
    ↓
Passo 4: Copiar boot.py e code.py para o pendrive CIRCUITPY
    ↓
Passo 5: Reiniciar o Pico → Firmware em execução!
```

---

## Passo 1 — Baixar o CircuitPython para o Pico

1. Acesse o site oficial: **https://circuitpython.org/board/raspberry_pi_pico/**
2. Clique em **"DOWNLOAD .UF2 NOW"** (versão estável mais recente, 9.x ou superior)
3. Um arquivo chamado algo como `adafruit-circuitpython-raspberry_pi_pico-pt_BR-9.x.x.uf2` será baixado

> Use sempre a versão **9.x ou superior** — versões anteriores não têm suporte a USB Host.

---

## Passo 2 — Colocar o Pico em modo de programação (BOOTSEL)

1. **Certifique-se de que o Pico está desconectado** de qualquer coisa (não conectado ao TK90X nem ao PC)
2. **Pressione e segure** o botão **BOOTSEL** (o único botão branco na placa)
3. Enquanto segura, **conecte o cabo micro-USB ao PC**
4. **Solte o botão BOOTSEL**
5. O Pico aparecerá no seu computador como um **pendrive chamado `RPI-RP2`**

```
Windows: aparece no Explorador de Arquivos como "RPI-RP2 (D:)" ou letra similar
Linux:   montado em /media/usuario/RPI-RP2
macOS:   aparece na Área de Trabalho como "RPI-RP2"
```

---

## Passo 3 — Instalar o CircuitPython

1. **Arraste** (ou copie e cole) o arquivo `.uf2` baixado no Passo 1 para dentro do pendrive `RPI-RP2`
2. Aguarde alguns segundos
3. O pendrive `RPI-RP2` **desaparecerá automaticamente** e um novo pendrive chamado **`CIRCUITPY`** aparecerá

> Isso é normal! O Pico reiniciou com o CircuitPython instalado.

---

## Passo 4 — Copiar os arquivos do firmware

Os arquivos do firmware estão na pasta `firmware_circuitpython/` deste projeto:
- `boot.py`
- `code.py`

**Copie os dois arquivos diretamente para a raiz do pendrive `CIRCUITPY`:**

```
CIRCUITPY/
├── boot.py    ← copiar aqui
└── code.py    ← copiar aqui
```

> Não crie subpastas. Os dois arquivos devem estar na raiz do drive CIRCUITPY.

### No Windows:
1. Abra o pendrive `CIRCUITPY` no Explorador de Arquivos
2. Copie `boot.py` e `code.py` para dentro dele (Ctrl+C / Ctrl+V)

### No Linux:
```bash
cp firmware_circuitpython/boot.py /media/$USER/CIRCUITPY/
cp firmware_circuitpython/code.py /media/$USER/CIRCUITPY/
```

### No macOS:
```bash
cp firmware_circuitpython/boot.py /Volumes/CIRCUITPY/
cp firmware_circuitpython/code.py /Volumes/CIRCUITPY/
```

---

## Passo 5 — Reiniciar o Pico

Após copiar os arquivos, o Pico pode reiniciar automaticamente. Se não reiniciar:

1. **Ejete o pendrive CIRCUITPY** com segurança (como qualquer pendrive)
2. **Desconecte o cabo micro-USB** do PC
3. Reconecte o Pico ao circuito do TK90X e ligue o teclado USB

Na primeira inicialização com `boot.py`, o Pico configurará a porta USB Host nos pinos GP0/GP1.

---

## Passo 6 — Testar

1. Ligue o TK90X com o Pico conectado ao circuito
2. Conecte o teclado USB ao conector USB-A do circuito (nos pinos GP0/GP1)
3. Teste as teclas — elas devem funcionar no TK90X

**Teclas para testar primeiro:**

| Teclado USB | Esperado no TK90X |
|---|---|
| Letras A–Z | Letras A–Z |
| Números 1–0 | Números 1–0 |
| Enter | ENTER |
| Space | SPACE |
| Backspace | DELETE |
| Setas ← ↑ ↓ → | Movimento do cursor |
| Esc | BREAK |

---

## Como editar o código (para quem quiser personalizar)

Uma das grandes vantagens do CircuitPython é que **você pode editar o código diretamente no pendrive CIRCUITPY**, sem instalar nada.

1. Conecte o Pico ao PC via micro-USB (a qualquer momento, sem precisar do BOOTSEL)
2. O pendrive `CIRCUITPY` aparecerá
3. Abra `code.py` com qualquer editor de texto
4. Faça suas modificações e salve
5. O Pico reiniciará automaticamente com o novo código

> **Atenção**: como o `boot.py` desativa o recarregamento automático, pode ser necessário apertar o botão de RESET (ou desligar/ligar) após salvar alterações em `boot.py`.

---

## Solução de Problemas

### O pendrive CIRCUITPY não aparece após copiar o .uf2
- Verifique se o Pico estava em modo BOOTSEL ao copiar (drive `RPI-RP2` deve ter aparecido antes)
- Use outro cabo micro-USB (alguns cabos são apenas de carga, sem dados)
- Tente um computador ou porta USB diferente

### O teclado USB não é reconhecido
- Verifique as conexões nos pinos GP0 (D+) e GP1 (D-) com os resistores de 27 Ω
- Verifique se o VBUS (+5V) está chegando ao pino 1 do conector USB-A
- Confirme que o GND do USB-A está ligado ao GND do circuito
- Tente outro teclado USB padrão (teclados com hubs internos ou protocolos proprietários podem não funcionar)

### Teclas "grudadas" mesmo após soltar
- Verifique as conexões dos transistores BC547 (base, coletor, emissor na ordem correta)
- Confirme que os emissores de Q1–Q5 estão ligados ao GND
- Com um multímetro em modo DC, meça o pino Col enquanto pressiona uma tecla: deve ir de ~5V para ~0V

### O drive CIRCUITPY aparece mas o código não executa
- Verifique se `boot.py` e `code.py` estão na **raiz** do drive (não em subpastas)
- Conecte o Pico ao PC, abra o drive CIRCUITPY e procure o arquivo `boot_out.txt` — ele mostra mensagens de erro

### Como ver erros e mensagens de debug
1. Instale o **Mu Editor** (gratuito em [codewith.mu](https://codewith.mu/))
   - Ou qualquer terminal serial (PuTTY no Windows, `screen /dev/ttyACM0 115200` no Linux)
2. Conecte o Pico ao PC
3. Abra a conexão serial — você verá as mensagens `print()` do código:
   ```
   USB ZX Converter (CircuitPython) iniciando...
   Teclado USB conectado.
   ```

---

## Atualizando o firmware no futuro

Para atualizar para uma nova versão do `code.py`:

1. Conecte o Pico ao PC via micro-USB (sem BOOTSEL, modo normal)
2. O pendrive `CIRCUITPY` aparecerá
3. Substitua o arquivo `code.py` pelo novo
4. Ejete o drive e reinicie o Pico

Para atualizar o CircuitPython em si (nova versão .uf2):
1. Segure BOOTSEL + conecte ao PC (como no Passo 2)
2. Arraste o novo .uf2 para o drive `RPI-RP2`
3. O Pico reiniciará e o drive `CIRCUITPY` voltará com seus arquivos intactos

---

## Diferenças em relação à versão Arduino

| Aspecto | CircuitPython | Arduino (.ino) |
|---|---|---|
| Instalação | Mais fácil | Requer IDE |
| Velocidade de resposta | Boa | Melhor |
| Modificação do código | Direto no pendrive | Requer recompilação |
| Indicada para | Comunidade/distribuição | Uso final definitivo |

> Para uso diário de digitação, a versão CircuitPython funciona perfeitamente.
> Se perceber alguma lentidão em jogos que exigem respostas muito rápidas,
> a versão Arduino (`.ino`) pode ser mais adequada.