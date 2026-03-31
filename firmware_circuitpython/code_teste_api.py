# code_teste_api.py — Testa a API do dispositivo USB no CircuitPython 10.x
import usb.core
import time

time.sleep(1)

devices = list(usb.core.find(find_all=True))
print(f"Dispositivos encontrados: {len(devices)}")

if not devices:
    print("Nenhum dispositivo. Verifique a fiacao.")
    raise SystemExit

dev = devices[0]

# Mostra todos os atributos disponíveis no objeto Device
print("\nAtributos do Device:")
print(dir(dev))

# Tenta enviar SET_PROTOCOL = boot (interface 0)
print("\nTentando SET_PROTOCOL (boot) na interface 0...")
try:
    dev.ctrl_transfer(0x21, 0x0B, 0, 0, None)
    print("OK!")
except Exception as e:
    print(f"Erro: {e}")

# Tenta ler de endpoints comuns de teclado HID
print("\nTentando ler de endpoints HID...")
for ep in [0x81, 0x82, 0x83]:
    try:
        data = dev.read(ep, 8, timeout=200)
        print(f"  Endpoint 0x{ep:02X}: {[hex(b) for b in data]}")
        print("  -> Este e o endpoint certo! Pressione uma tecla para confirmar.")
        time.sleep(1)
        data2 = dev.read(ep, 8, timeout=2000)
        print(f"  -> Com tecla: {[hex(b) for b in data2]}")
        break
    except Exception as e:
        print(f"  Endpoint 0x{ep:02X}: {e}")
