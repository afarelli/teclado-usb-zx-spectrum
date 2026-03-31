# code_teste_usbhost.py
# Cole este conteudo no code.py do CIRCUITPY
# Abra o Thonny (thonny.org) ou o Mu Editor para ver o resultado no console serial.
#
# Este teste verifica se o modulo usb_host esta disponivel e funcionando.

import time

time.sleep(2)  # aguarda o boot estabilizar

print("=" * 40)
print("TESTE: modulo usb_host")
print("=" * 40)

# Teste 1: importacao do usb_host
try:
    import usb_host
    print("OK  - 'import usb_host' funcionou")
except ImportError:
    print("ERRO - 'import usb_host' falhou: modulo nao existe neste firmware!")
    print("      Baixe o CircuitPython 9.x em circuitpython.org/board/raspberry_pi_pico")
    raise SystemExit

# Teste 2: usb_host.Port() foi chamado no boot.py?
# (Se o boot.py rodou corretamente, a porta ja esta configurada)
try:
    import usb.core
    print("OK  - 'import usb.core' funcionou")
except ImportError:
    print("ERRO - 'import usb.core' falhou")
    raise SystemExit

# Teste 3: enumera dispositivos USB
print()
print("Buscando dispositivos USB em GP0/GP1...")
time.sleep(1)

dispositivos = list(usb.core.find(find_all=True))
print(f"Dispositivos encontrados: {len(dispositivos)}")

if len(dispositivos) == 0:
    print()
    print("Nenhum dispositivo encontrado.")
    print("Possiveis causas:")
    print("  1. boot.py nao chamou usb_host.Port() - veja boot_out.txt")
    print("  2. Fiacao incorreta em GP0/GP1")
    print("  3. VBUS (+5V) nao chegando ao teclado")
else:
    for i, dev in enumerate(dispositivos):
        try:
            print(f"  Dispositivo {i}: VID=0x{dev.idVendor:04X} PID=0x{dev.idProduct:04X} Classe={dev.bDeviceClass}")
        except Exception as e:
            print(f"  Dispositivo {i}: (erro ao ler info: {e})")

print()
print("Teste concluido.")
