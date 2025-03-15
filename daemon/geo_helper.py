import os
from geoip2.database import Reader

def get_geo_info(ip_address, logger=None):
    """
    Busca informações de geolocalização de um endereço IP usando a base MaxMind.

    :param ip_address: Endereço IP a ser consultado.
    :param logger: Logger configurado para registrar informações e erros (opcional).
    :return: Dicionário contendo as informações de geolocalização (país, cidade, latitude, longitude).
    """
    # Caminho para o banco de dados GeoLite
    geoip_db_path = os.getenv('GEOIP_DB_PATH', '/usr/share/GeoIP/GeoLite2-City.mmdb')

    # Validar se o arquivo da base de dados existe
    if not os.path.isfile(geoip_db_path):
        error_msg = f"Base de dados GeoIP não encontrada em {geoip_db_path}"
        if logger:
            logger.error(error_msg)
        return {"country_code": None, "city": None, "latitude": None, "longitude": None}

    try:
        # Ler o banco de dados e obter as informações de geolocalização
        with Reader(geoip_db_path) as reader:
            response = reader.city(ip_address)
            geo_info = {
                "country_code": response.country.iso_code,
                "city": response.city.name,
                "latitude": response.location.latitude,
                "longitude": response.location.longitude,
            }
            if logger:
                logger.info(f"Geolocalização encontrada para {ip_address}: {geo_info}")
            return geo_info
    except Exception as e:
        error_msg = f"Erro ao obter informações de geolocalização para {ip_address}: {e}"
        if logger:
            logger.error(error_msg)
        return {"country_code": None, "city": None, "latitude": None, "longitude": None}