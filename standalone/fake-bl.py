import psycopg2
import random
from scapy.all import IP, TCP, send

# Dados de conexão ao banco de dados
db_host = 'localhost'
db_name = 'firewall'
db_user = 'admin'
db_password = 'Q1w2e3r4'

# Conectar ao banco de dados PostgreSQL
conn = psycopg2.connect(
    host=db_host,
    database=db_name,
    user=db_user,
    password=db_password
)

# Criar um cursor
cur = conn.cursor()

# Consulta SQL para selecionar IPs com abuso maior que 90
query = """
    SELECT ip_address
    FROM bl_local_cache
    WHERE abuse_confidence_score > 90
"""

# Executar a consulta
cur.execute(query)

# Obter todos os resultados
ip_addresses = cur.fetchall()

# Fechar o cursor e a conexão
cur.close()
conn.close()

# Lista de portas comuns associadas a serviços conhecidos
common_ports = {
    "HTTP": 80,
    "HTTPS": 443,
    "SSH": 22,
    "FTP": 21,
    "SMTP": 25,
    "DNS": 53,
    "MySQL": 3306,
    "PostgreSQL": 5432,
    "RDP": 3389,
    "Telnet": 23
}

# Defina a interface de rede que será utilizada
interface = "eth0"  # Substitua pelo nome correto da interface (ex: eth0, wlan0)

# Defina o IP de destino para a simulação
target_ip = "203.0.113.10"  # Endereço de IP do servidor que deseja "conectar"

# Defina a quantidade aleatória de registros a serem usados
num_records = random.randint(1, 50)

# Selecione uma quantidade aleatória de IPs para testar
selected_ips = random.sample(ip_addresses, min(num_records, len(ip_addresses)))

# Enviar pacotes SYN usando os IPs selecionados
for ip_address in selected_ips:
    # Seleciona uma porta de origem aleatória dentro da faixa de 1024 a 65535
    source_port = random.randint(1024, 65535)

    # Seleciona uma porta de destino aleatoriamente da lista de portas conhecidas
    target_port = random.choice(list(common_ports.values()))

    # Criar o pacote IP
    ip = IP(src=ip_address[0], dst=target_ip)

    # Criar o pacote TCP SYN com a porta de destino definida
    tcp = TCP(sport=source_port, dport=target_port, flags="S")

    # Combine os pacotes
    packet = ip/tcp

    # Envie o pacote
    send(packet, iface=interface, verbose=0)
    print(f"Pacote SYN enviado de {ip_address[0]}:{source_port} para {target_ip}:{target_port}")
