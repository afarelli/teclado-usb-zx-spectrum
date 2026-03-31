# boot_debug.py
#
# USE ESTE ARQUIVO APENAS PARA DEBUG.
# Renomeie para boot.py (substituindo o original) enquanto estiver diagnosticando.
# Após o debug, restaure o boot.py original.
#
# ATENÇÃO: Este arquivo libera escrita no filesystem pelo código Python,
# mas isso torna o drive CIRCUITPY somente-leitura pelo PC.
# Para editar arquivos, volte ao boot.py original.

import usb_host
import board
import supervisor
import storage

# Permite que o code.py escreva arquivos no drive CIRCUITPY
# (torna o drive read-only pelo lado do PC enquanto ativo)
storage.remount("/", readonly=False)

# Configura USB Host nos pinos GP0 (D+) e GP1 (D-)
usb_host.Port(board.GP0, board.GP1)

supervisor.runtime.autoreload = False
