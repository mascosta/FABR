import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Configuração do banco de dados (usar variáveis de ambiente como fallback)
db_config = {
    'dbname': os.getenv('DB_NAME', 'firewall'),
    'user': os.getenv('DB_USER', 'admin'),
    'password': os.getenv('DB_PASSWORD', 'Q1w2e3r4'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')  # Porta padrão do PostgreSQL
}

def get_db_connection(logger=None):
    """
    Cria uma conexão com o banco de dados usando psycopg2.

    :param logger: Logger para registrar erros (opcional).
    :return: Objeto de conexão psycopg2.
    """
    try:
        # Estabelecendo conexão
        conn = psycopg2.connect(**db_config, cursor_factory=RealDictCursor)
        # Verificando a conexão
        if logger:
            logger.info("Conexão com o banco de dados estabelecida com sucesso.")
        return conn
    except Exception as e:
        error_msg = f"Erro ao conectar ao banco de dados: {e}"
        if logger:
            logger.error(error_msg)
        raise Exception(error_msg)