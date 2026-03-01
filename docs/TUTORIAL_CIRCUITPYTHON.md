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
