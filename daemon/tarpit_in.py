import requests
import os
import sys
import logging
from db_config import get_db_connection
from geo_helper import get_geo_info
from logger import get_logger

# Configuração do logger
logger = get_logger("tarpit-in", severity=logging.INFO)

# Chave da API do AbuseIPDB
API_KEY = os.getenv('API_KEY')

if not API_KEY:
    logger.error("API_KEY não está configurada. Configure a variável de ambiente 'API_KEY' antes de executar o script.")

# Funções auxiliares
def execute_query(conn, query, params=()):
    """
    Executa uma consulta no banco de dados PostgreSQL.
    """
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if query.strip().lower().startswith("select"):
                return cur.fetchall()
            conn.commit()
    except Exception as e:
        logger.exception(f"Erro ao executar query: {query}")
        return []

def fetch_ip_reputation(ip):
    """
    Faz uma consulta à API do AbuseIPDB para buscar a reputação de um IP.
    """
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {'Key': API_KEY, 'Accept': 'application/json'}
    params = {'ipAddress': ip, 'maxAgeInDays': 90, 'verbose': True}
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()['data']
        else:
            logger.error(f"Erro na API AbuseIPDB para {ip}: {response.status_code} - {response.text}")
    except Exception as e:
        logger.exception(f"Erro ao buscar reputação do IP {ip}.")
    return None

def insert_or_update_tarpit(conn, ip, reputation, geo_data):
    """
    Insere ou atualiza um IP na tabela TARPIT com os dados mais recentes.
    """
    query = """
    INSERT INTO tp_address_local (
        ip_address, country_code, abuse_confidence_score,
        last_reported_at, src_longitude, src_latitude
    )
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (ip_address) DO UPDATE SET
        country_code = EXCLUDED.country_code,
        abuse_confidence_score = EXCLUDED.abuse_confidence_score,
        last_reported_at = EXCLUDED.last_reported_at,
        src_longitude = EXCLUDED.src_longitude,
        src_latitude = EXCLUDED.src_latitude;
    """
    execute_query(conn, query, (
        ip,
        geo_data['country_code'],
        reputation['abuseConfidenceScore'],
        reputation['lastReportedAt'],
        geo_data['longitude'],
        geo_data['latitude']
    ))
    logger.info(f"IP {ip} adicionado ou atualizado na TARPIT com score {reputation['abuseConfidenceScore']}.")

def insert_to_blacklist(conn, ip, reputation, geo_data):
    """
    Insere um IP na blacklist local com dados de geolocalização.
    """
    query = """
    INSERT INTO bl_address_local (
        ip_address, abuse_confidence_score,
        country_code, city, src_latitude, src_longitude
    )
    VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (ip_address) DO NOTHING;
    """
    execute_query(conn, query, (
        ip, reputation['abuseConfidenceScore'],
        geo_data['country_code'], geo_data['city'],
        geo_data['latitude'], geo_data['longitude']
    ))
    logger.info(f"IP {ip} adicionado à blacklist com score {reputation['abuseConfidenceScore']}.")

def remove_from_tarpit(conn, ip):
    """
    Remove um IP da tabela TARPIT.
    """
    query = "DELETE FROM tp_address_local WHERE ip_address = %s;"
    try:
        execute_query(conn, query, (ip,))
        logger.info(f"IP {ip} removido da tabela TARPIT.")
    except Exception as e:
        logger.error(f"Erro ao remover o IP {ip} da tabela TARPIT: {e}")

# Função principal
def main():
    """
    Função principal do script.
    """
    if len(sys.argv) < 2:
        logger.error("Nenhum IP fornecido ao tarpit-in.")
        return

    ip_to_check = sys.argv[1]

    # Log informando o IP sendo analisado
    logger.info(f"Iniciando checagem de reputação para o IP: {ip_to_check}")

    conn = None
    try:
        conn = get_db_connection()

        # Busca a reputação do IP
        reputation = fetch_ip_reputation(ip_to_check)
        if not reputation:
            logger.warning(f"Reputação do IP {ip_to_check} não encontrada. Ignorando.")
            return

        # Busca os dados de geolocalização
        geo_data = get_geo_info(ip_to_check, logger=logger)
        if not geo_data:
            geo_data = {"country_code": None, "city": None, "latitude": None, "longitude": None}

        # Avalia a reputação e insere na blacklist ou tarpit
        if reputation.get('abuseConfidenceScore', 0) >= 75:
            insert_to_blacklist(conn, ip_to_check, reputation, geo_data)
        else:
            insert_or_update_tarpit(conn, ip_to_check, reputation, geo_data)
    except Exception as e:
        logger.critical(f"Erro crítico no processamento do IP {ip_to_check}: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()