import subprocess
import logging
from db_config import get_db_connection
from geo_helper import get_geo_info
from logger import get_logger

# Configuração do logger
logger = get_logger("rule-manager", severity=logging.INFO)
logger.info("Iniciando o script rule_manager.")

# Funções auxiliares
def run_iptables_command(command):
    """
    Executa um comando do IPTables e registra o log.
    """
    try:
        subprocess.run(command, check=True, shell=True, stderr=subprocess.PIPE)
        logger.info(f"Comando executado com sucesso: {command}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao executar o comando {command}: {e.stderr.decode()}")

def execute_query(query, params=()):
    """
    Executa uma consulta no banco de dados e retorna o resultado.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall() if query.strip().lower().startswith("select") else None
    except Exception as e:
        logger.exception(f"Erro ao executar query: {query}")
        return []

def setup_chains():
    """
    Configura as chains TARPIT, BLACKLIST e WHITELIST no IPTables.
    """
    for chain_name in ["TARPIT", "BLACKLIST", "WHITELIST"]:
        run_iptables_command(f"sudo iptables -N {chain_name} || sudo iptables -F {chain_name}")
    run_iptables_command(f"sudo iptables -A TARPIT -m limit --limit 60/min -j ACCEPT")
    run_iptables_command(f"sudo iptables -A TARPIT -j DROP")
    run_iptables_command(f"sudo iptables -A BLACKLIST -p tcp -j REJECT --reject-with tcp-reset")
    run_iptables_command(f"sudo iptables -A BLACKLIST -j DROP")
    run_iptables_command(f"sudo iptables -A WHITELIST -j ACCEPT")
    logger.info("Chains TARPIT, BLACKLIST e WHITELIST configuradas com sucesso.")

def apply_tarpit_rule(ip):
    """
    Aplica a regra de TARPIT para o IP especificado.
    """
    for chain in ["FORWARD", "INPUT"]:
        run_iptables_command(f"sudo iptables -I {chain} -s {ip} -j TARPIT")
    logger.info(f"Regras de TARPIT aplicadas para o IP {ip}.")

def apply_blacklist_rule(ip):
    """
    Aplica a regra de BLACKLIST para o IP especificado.
    """
    for chain in ["FORWARD", "INPUT"]:
        run_iptables_command(f"sudo iptables -I {chain} -s {ip} -j BLACKLIST")
    logger.info(f"Regras de BLACKLIST aplicadas para o IP {ip}.")

def apply_whitelist_rules():
    """
    Aplica as regras da whitelist para todos os IPs na tabela wl_address_local.
    """
    whitelist_ips = execute_query("SELECT ip_address FROM wl_address_local")
    for ip, in whitelist_ips:
        for chain in ["FORWARD", "INPUT"]:
            run_iptables_command(f"sudo iptables -I {chain} -s {ip} -j WHITELIST")
    logger.info("Regras de WHITELIST aplicadas com sucesso.")

def process_ip(ip_to_process):
    """
    Determina se o IP deve ser tratado como TARPIT ou BLACKLIST e aplica as regras.
    """
    if execute_query("SELECT 1 FROM tp_address_local WHERE ip_address = %s", (ip_to_process,)):
        apply_tarpit_rule(ip_to_process)
    elif execute_query("SELECT 1 FROM bl_address_local WHERE ip_address = %s", (ip_to_process,)):
        apply_blacklist_rule(ip_to_process)
    else:
        logger.warning(f"IP {ip_to_process} não encontrado em TARPIT ou BLACKLIST.")

def main(ip_to_process=None):
    """
    Função principal do script. Configura as chains e aplica as regras.
    """
    logger.info("Configurando chains e aplicando regras gerais.")
    setup_chains()
    apply_whitelist_rules()

    if ip_to_process:
        logger.info(f"Processando regras específicas para o IP: {ip_to_process}")
        process_ip(ip_to_process)
    else:
        logger.info("Nenhum IP específico fornecido. Apenas regras gerais foram aplicadas.")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        ip = sys.argv[1]
        logger.info(f"Iniciando processamento para o IP: {ip}")
        main(ip_to_process=ip)
    else:
        logger.info("Nenhum IP fornecido. Aplicando apenas regras gerais.")
        main()