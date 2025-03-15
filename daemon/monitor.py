import asyncio
import ipaddress
import os
from pathlib import Path
from subprocess import Popen
from scapy.all import AsyncSniffer, IP, TCP

# Caminhos configuráveis
fabr_path = Path(os.getenv("FABR_PATH", "/etc/fabr"))
python_path = Path(os.getenv("PYTHON_PATH", "/usr/bin/python3"))

# Função para acionar o Manager
def trigger_manager(src_ip, src_port, dst_port):
    try:
        # Aciona o script manager.py passando IP, porta de origem e porta de destino
        Popen([
            str(python_path),
            str(fabr_path / "manager.py"),
            src_ip,
            str(src_port),
            str(dst_port)
        ])
    except Exception as e:
        # Apenas imprime o erro, sem registrar em logs para evitar sobrecarga
        print(f"Erro ao acionar o Manager para o IP {src_ip}: {e}")

# Processa conexões TCP
async def handle_incoming_connection(packet):
    try:
        if not (IP in packet and TCP in packet):
            return

        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        src_port = packet[TCP].sport  # Porta de origem
        dst_port = packet[TCP].dport  # Porta de destino

        # Ignora pacotes com IPs privados ou sem destino
        if ipaddress.ip_address(src_ip).is_private or not dst_ip:
            return

        # Verifica flag SYN sem ACK
        if 'S' in packet[TCP].flags and not 'A' in packet[TCP].flags:
            # Aciona o manager para processar o IP e as portas
            trigger_manager(src_ip, src_port, dst_port)
    except Exception as e:
        # Apenas imprime o erro, sem registrar em logs
        print(f"Erro ao processar pacote: {e}")

# Captura de pacotes
async def packet_sniffer():
    try:
        # Função para lidar com pacotes no contexto assíncrono
        def handle_packet_sync(packet):
            asyncio.run(handle_incoming_connection(packet))

        # Inicia o sniffer assíncrono
        sniffer = AsyncSniffer(
            filter="tcp",
            prn=handle_packet_sync  # Chama a função síncrona que executa a coroutine
        )
        sniffer.start()
        await asyncio.sleep(float("inf"))
    except Exception as e:
        # Apenas imprime o erro, já que não há logs configurados
        print(f"Erro crítico na captura de pacotes: {e}")

if __name__ == "__main__":
    asyncio.run(packet_sniffer())