import requests
import psycopg2
import os
from datetime import datetime
from logger import get_logger
import logging
from time import time

# Configurar o logger
logger = get_logger("update-bl", severity=logging.INFO)

logger.info("Iniciando atualização da blacklist.")

# Dados de conexão ao banco de dados PostgreSQL
db_host = 'localhost'
db_name = 'firewall'
db_user = 'admin'
db_password = 'Q1w2e3r4'

# Sua chave de API do AbuseIPDB
API_KEY = os.getenv('API_KEY')

def buscar_dados():
    start_time = time()
    try:
        url = "https://api.abuseipdb.com/api/v2/blacklist"
        headers = {
            'Key': API_KEY,
            'Accept': 'application/json'
        }
        params = {
            'confidenceMinimum': 75,
            'limit': 9999999
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            logger.info("Dados da API AbuseIPDB obtidos com sucesso.")
            return response.json()
        else:
            logger.error(f"Erro ao buscar dados da API: {response.status_code}")
            return None
    except Exception as e:
        logger.exception("Erro ao conectar à API AbuseIPDB.")
        return None
    finally:
        elapsed_time = (time() - start_time) * 1000
        logger.info(f"Busca de dados na API concluída em {elapsed_time:.2f} ms.")

def truncar_tabela():
    start_time = time()
    try:
        conexao = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host
        )
        cursor = conexao.cursor()
        cursor.execute("TRUNCATE TABLE bl_local_cache")
        conexao.commit()
        logger.info("Tabela bl_local_cache truncada com sucesso.")
    except Exception as e:
        logger.exception("Erro ao truncar a tabela bl_local_cache.")
    finally:
        cursor.close()
        conexao.close()
        elapsed_time = (time() - start_time) * 1000
        logger.info(f"Operação de truncate concluída em {elapsed_time:.2f} ms.")

def inserir_dados_no_postgresql(dados):
    start_time = time()
    try:
        conexao = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host
        )
        cursor = conexao.cursor()

        for registro in dados['data']:
            # Formata a data para o padrão aceito pelo PostgreSQL
            data_formatada = datetime.strptime(registro['lastReportedAt'], "%Y-%m-%dT%H:%M:%S+00:00")

            comando_sql = """
            INSERT INTO bl_local_cache (ip_address, country_code, abuse_confidence_score, last_reported_at)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(comando_sql, (registro['ipAddress'], registro['countryCode'], registro['abuseConfidenceScore'], data_formatada))

        conexao.commit()
        logger.info(f"{len(dados['data'])} registros inseridos no banco de dados.")
    except Exception as e:
        logger.exception("Erro ao inserir dados no PostgreSQL.")
    finally:
        cursor.close()
        conexao.close()
        elapsed_time = (time() - start_time) * 1000
        logger.info(f"Inserção de dados no PostgreSQL concluída em {elapsed_time:.2f} ms.")

def main():
    start_time = time()
    try:
        dados = buscar_dados()
        if dados:
            truncar_tabela()  # Adicionado: Limpa a tabela antes de inserir
            inserir_dados_no_postgresql(dados)
        else:
            logger.error("Nenhum dado retornado pela API. Encerrando execução.")
    except Exception:
        logger.exception("Erro inesperado na execução principal.")
    finally:
        elapsed_time = (time() - start_time) * 1000
        logger.info(f"Execução do script principal concluída em {elapsed_time:.2f} ms.")

if __name__ == "__main__":
    main()