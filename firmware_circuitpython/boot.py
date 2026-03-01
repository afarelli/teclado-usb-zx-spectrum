# boot.py
# Executado automaticamente no início, antes do code.py
#
# Este arquivo configura o Pico para funcionar como HOST USB nos pinos GP0/GP1
# usando a PIO (hardware interno do RP2040).
#
# IMPORTANTE: Após copiar este arquivo para o Pico (drive CIRCUITPY),
# o Pico precisará ser reiniciado para que as configurações tenham efeito.

import usb_host
import board
import supervisor

# Configura a porta USB Host (PIO) nos pinos GP0 (D+) e GP1 (D-)
# O teclado USB será ligado ao conector USB-A conectado nesses pinos.
# A porta micro-USB do Pico continua livre para acesso ao drive CIRCUITPY.
usb_host.Port(board.GP0, board.GP1)

# Desativa o recarregamento automático do código para melhor desempenho.
# Para reativar (útil durante desenvolvimento): apague esta linha.
supervisor.runtime.autoreload = False
