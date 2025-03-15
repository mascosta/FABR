import logging
import os
import time
from functools import wraps
from logging.handlers import RotatingFileHandler

# Diretório de logs
log_dir = "/var/log/fabr/"
os.makedirs(log_dir, exist_ok=True)

def get_logger(script_name, severity=logging.INFO, max_bytes=5*1024*1024, backup_count=3):
    """
    Configura um logger individual para cada script e severidade específica.

    :param script_name: Nome do script que será usado no arquivo de log.
    :param severity: Nível de severidade do log (DEBUG, INFO, WARNING, etc.).
    :param max_bytes: Tamanho máximo do arquivo de log antes de ser rotacionado (em bytes).
    :param backup_count: Número máximo de arquivos de log rotacionados a manter.
    :return: Logger configurado.
    """
    logger = logging.getLogger(script_name)

    # Evitar múltiplos handlers
    if not logger.hasHandlers():
        try:
            logger.setLevel(severity)

            # Formato do log
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

            # Handler para arquivo de log rotativo específico do script
            file_handler = RotatingFileHandler(
                os.path.join(log_dir, f'{script_name}.log'),
                maxBytes=max_bytes,
                backupCount=backup_count
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            # Opcional: log no console
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        except Exception as e:
            print(f"Erro ao configurar o logger para {script_name}: {e}")

    return logger

def log_execution_time(logger):
    """
    Decorador para medir e registrar o tempo de execução de uma função no log.

    :param logger: Logger configurado para registrar o tempo de execução.
    :return: Função decorada.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed_time = (time.time() - start_time) * 1000  # Tempo em milissegundos
                logger.info(f"Ação '{func.__name__}' executada em {elapsed_time:.2f} ms.")
                return result
            except Exception as e:
                logger.error(f"Erro na execução de '{func.__name__}': {e}")
                raise
        return wrapper
    return decorator

def log_contextual_data(logger, ip_address=None, task=None, severity=logging.INFO):
    """
    Registra informações contextuais (IP, tarefa, etc.) no log.

    :param logger: Logger configurado para registrar informações.
    :param ip_address: Endereço IP relacionado à ação (opcional).
    :param task: Descrição da tarefa sendo realizada (opcional).
    :param severity: Nível de severidade do log.
    """
    message = "Contexto: "
    if ip_address:
        message += f"IP: {ip_address} | "
    if task:
        message += f"Tarefa: {task} | "
    logger.log(severity, message)