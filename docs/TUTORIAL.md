# Tutorial: Instalação do Firmware no Raspberry Pi Pico
## Conversor USB → ZX Spectrum / TK90X

---

## Pré-requisitos

### Hardware necessário
- Raspberry Pi Pico (montado conforme o esquema elétrico em `schematic/SCHEMATIC.md`)
- Cabo **micro-USB** (para conectar o Pico ao PC durante a programação)
- PC com Windows 10/11, Linux ou macOS

### Software necessário
- Arduino IDE 2.x (gratuito em [arduino.cc](https://www.arduino.cc/en/software))
- Conexão com a internet (para instalar pacotes)

---

## Passo 1 — Instalar o Arduino IDE

1. Acesse [arduino.cc/en/software](https://www.arduino.cc/en/software)
2. Baixe e instale a versão **2.x** para o seu sistema operacional
3. Abra o Arduino IDE após a instalação

---

## Passo 2 — Adicionar o suporte ao Raspberry Pi Pico

O Arduino IDE não inclui o Pico por padrão. Precisamos instalar o núcleo **arduino-pico** de Earlephilhower.

1. No Arduino IDE, vá em **Arquivo → Preferências**
2. No campo **"URLs adicionais para Gerenciador de Placas"**, cole esta URL:
   ```
   https://github.com/earlephilhower/arduino-pico/releases/download/global/package_rp2040_index.json
   ```
3. Clique em **OK**
4. Vá em **Ferramentas → Placa → Gerenciador de Placas**
5. Na barra de busca, digite: `rp2040`
6. Localize **"Raspberry Pi RP2040 Boards (Earlephilhower)"** e clique em **Instalar**
7. Aguarde o download (pode demorar alguns minutos)

---

## Passo 3 — Instalar as bibliotecas necessárias

### 3.1 Adafruit TinyUSB Library

1. No Arduino IDE, vá em **Sketch → Incluir Biblioteca → Gerenciar Bibliotecas**
2. Busque por: `Adafruit TinyUSB`
3. Localize **"Adafruit TinyUSB Library"** (por Adafruit) e clique em **Instalar**

### 3.2 Pico PIO USB

Esta biblioteca já vem incluída no núcleo arduino-pico. Não é necessário instalar separadamente.

> **Verificação**: Se ao compilar aparecer erro com `#include "pio_usb.h"`, instale manualmente a biblioteca **"Pico PIO USB"** pelo Gerenciador de Bibliotecas.

---

## Passo 4 — Configurar a placa no Arduino IDE

Com o projeto aberto (ou antes de abrir), configure:

1. **Placa**: Ferramentas → Placa → Raspberry Pi RP2040 Boards → **Raspberry Pi Pico**
2. **Velocidade da CPU**: Ferramentas → CPU Speed → **120 MHz**
   > **Crítico!** O PIO-USB exige exatamente 120 MHz (ou 240 MHz). O padrão de 125 MHz causará falha na comunicação USB com o teclado.
3. **USB Stack**: Ferramentas → USB Stack → **Adafruit TinyUSB**
4. **Porta**: Por ora, deixe em branco (será configurada no Passo 6)

---

## Passo 5 — Abrir o firmware

1. No Arduino IDE, vá em **Arquivo → Abrir**
2. Navegue até a pasta do projeto:
   ```
   firmware/usb_zx_converter/usb_zx_converter.ino
   ```
3. O sketch será aberto

### 5.1 Compilar (verificar antes de enviar)

1. Clique no botão **✓ (Verificar/Compilar)** ou pressione `Ctrl+R`
2. Aguarde a compilação. Ao final, a mensagem deve ser:
   ```
   Sketch uses XXXXX bytes (XX%) of program storage space.
   ```
3. Se houver erros, confira se as etapas anteriores foram feitas corretamente.

**Erros comuns e soluções:**

| Erro | Causa | Solução |
|------|-------|---------|
| `pio_usb.h: No such file` | Biblioteca PIO USB ausente | Instalar "Pico PIO USB" no Gerenciador |
| `Adafruit_TinyUSB.h: No such file` | Biblioteca TinyUSB ausente | Instalar "Adafruit TinyUSB Library" |
| `USB Stack: invalid` | CPU Speed errada | Selecionar 120 MHz em Ferramentas |
| `tuh_hid_set_protocol not declared` | Versão antiga do TinyUSB | Atualizar "Adafruit TinyUSB Library" |

---

## Passo 6 — Colocar o Pico em modo de programação (BOOTSEL)

O Pico deve estar **desconectado do circuito do TK90X** durante a programação.

1. **Certifique-se de que o Pico está desconectado do TK90X** (remova os fios ou desconecte o cabo de alimentação do TK90X)
2. **Pressione e segure** o botão **BOOTSEL** (o único botão branco na placa do Pico)
3. Enquanto segura o BOOTSEL, **conecte o cabo micro-USB** do Pico ao PC
4. **Solte o botão BOOTSEL**
5. O Pico aparecerá como um **pendrive/drive USB** no seu sistema operacional com o nome `RPI-RP2`

> No Windows: aparece como "RPI-RP2 (D:)" ou similar no Explorador de Arquivos.
> No Linux/macOS: será montado automaticamente.

---

## Passo 7 — Enviar o firmware

### Método A — Via Arduino IDE (recomendado)

1. Com o Pico em modo BOOTSEL e aparecendo como drive, volte ao Arduino IDE
2. Em **Ferramentas → Porta**, selecione a porta que corresponde ao Pico
   - Windows: algo como `COM3 (UF2 Board)`
   - Linux: `/dev/ttyACM0` ou similar
3. Clique no botão **→ (Enviar)** ou pressione `Ctrl+U`
4. O Arduino IDE compilará e enviará automaticamente o firmware
5. O Pico reiniciará sozinho ao terminar

### Método B — Arrastar o arquivo .uf2 manualmente

1. Compile o sketch (Passo 5) e localize o arquivo `.uf2` gerado:
   - Windows: `%TEMP%\arduino_build_XXXXX\usb_zx_converter.ino.uf2`
   - Linux/macOS: `/tmp/arduino-build-XXXXX/usb_zx_converter.ino.uf2`
2. Copie (arraste) o arquivo `.uf2` para o drive `RPI-RP2`
3. O drive desaparecerá e o Pico reiniciará automaticamente com o novo firmware

---

## Passo 8 — Verificar o funcionamento

Após o envio do firmware:

1. **Desconecte o cabo micro-USB do PC**
2. **Reconecte o Pico ao circuito do TK90X** (fios de alimentação, Row e Col)
3. **Conecte o teclado USB** ao conector USB-A do circuito
4. **Ligue o TK90X**
5. Teste algumas teclas no teclado USB — elas devem aparecer no ZX Spectrum/TK90X

### Teste rápido recomendado

| Tecla no teclado USB | Esperado no TK90X |
|----------------------|-------------------|
| `J` | Letra J          |
| `1` a `0` | Números 1–0 |
| `Enter` | Enter |
| `Space` | Espaço |
| `Backspace` | DELETE (apaga o último caractere) |
| `Seta esquerda` | Cursor para esquerda |
| `Seta direita` | Cursor para direita |
| `Esc` | BREAK |
| `Shift` (esquerdo) + letra | Caps Shift + letra |
| `Shift` (direito) + letra | Symbol Shift + letra |

---

## Mapeamento completo de teclas

### Teclas diretas

| Teclado USB | ZX Spectrum |
|-------------|-------------|
| A–Z         | A–Z         |
| 0–9         | 0–9         |
| Enter       | ENTER       |
| Space       | SPACE       |
| Shift esquerdo | CAPS SHIFT (CS) |
| Shift direito  | SYMBOL SHIFT (SS) |

### Teclas especiais

| Teclado USB     | ZX Spectrum equivalente |
|-----------------|-------------------------|
| Backspace       | CS + 0 (DELETE)         |
| Delete          | CS + 0 (DELETE)         |
| Seta ←          | CS + 5                  |
| Seta ↓          | CS + 6                  |
| Seta ↑          | CS + 7                  |
| Seta →          | CS + 8                  |
| Escape          | CS + Space (BREAK)      |
| Caps Lock       | CAPS SHIFT              |
| Tab             | CS + I                  |

### Símbolos via Shift + número

| Teclado USB | ZX Spectrum (SS + número) |
|-------------|--------------------------|
| Shift + 1 = `!` | SS + 1 |
| Shift + 2 = `@` | SS + 2 |
| Shift + 3 = `#` | SS + 3 |
| Shift + 4 = `$` | SS + 4 |
| Shift + 5 = `%` | SS + 5 |
| Shift + 6 = `&` | SS + 6 |
| Shift + 7 = `'` | SS + 7 |
| Shift + 8 = `(` | SS + 8 |
| Shift + 9 = `)` | SS + 9 |
| Shift + 0 = `_` | SS + 0 |

---

## Como atualizar o firmware no futuro

Quando quiser gravar uma nova versão do firmware:

1. **Desconecte o teclado USB** do conector USB-A do circuito
2. **Desconecte o Pico do TK90X** (retire a alimentação)
3. Segure **BOOTSEL**, conecte o **micro-USB ao PC**, solte o botão
4. O Pico entra em modo de programação
5. Envie o novo firmware normalmente (Passo 7)
6. Desconecte o micro-USB, reconecte ao TK90X e ao teclado

> **Dica**: Se quiser facilitar atualizações frequentes, adicione um interruptor de 2 posições entre a saída VSYS e o +5V do TK90X. Assim você pode ligar/desligar o Pico sem desmontar o circuito.

---

## Troubleshooting

### O teclado USB não é reconhecido
- Verifique se a CPU está em **120 MHz** (não 125 MHz)
- Confirme as conexões dos resistores de 27 Ω no GP0 e GP1
- Teste com outro teclado USB (alguns teclados com hub interno podem precisar de adaptação)
- Verifique se o VBUS (5V) está chegando ao conector USB-A

### Teclas "grudadas" ou saída errada
- Verifique se os transistores Q1–Q5 estão funcionando (medir tensão no coletor)
- Confira se os emissores dos transistores estão ligados ao GND
- Verifique se as ligações Row estão na ordem correta (Row1→GP2, Row2→GP3, etc.)

### O Pico não aparece como drive (BOOTSEL não funciona)
- Tente com outro cabo micro-USB (alguns cabos são apenas de carga)
- Mantenha o BOOTSEL pressionado **antes** de conectar o USB, e solte **depois**

### O Arduino IDE não encontra a porta do Pico
- Verifique se o drive `RPI-RP2` aparece no sistema
- Reinicie o Arduino IDE após conectar o Pico em modo BOOTSEL

### O TK90X não responde às teclas, mas o circuito está correto
- Verifique se o GND do Pico e do TK90X estão conectados
- Meça com multímetro: quando uma tecla é pressionada no USB, o pino Col correspondente deve ir para ~0V
- Verifique se a CPU está em 120 MHz — se estiver em 125 MHz, o USB pode parecer funcionar mas ter drops de pacotes
