# FABR - Firewall Automatizado Baseado em Reputação

O **FABR (Firewall Automatizado com Blacklists e Reputação)** é uma solução desenvolvida para automação do bloqueio e degradação de conexões suspeitas em redes computacionais. Ele monitora conexões de entrada, consulta blacklists e toma ações baseadas na reputação dos endereços IPs. A solução foi projetada para integrar-se ao AbuseIPDB e a regras dinâmicas de IPTables, garantindo maior segurança e eficiência no tratamento de conexões maliciosas.

# Estrutura do repositório

```
📄 pgsql.sql
📄 fabr.service
📄 .gitignore
📄 README.md
📄 conexoes.json
📂 daemon/
├── 📄 db_config.py
├── 📄 geo_helper.py
├── 📄 logger.py
├── 📄 manager.py
├── 📄 monitor.py
├── 📄 rule_manager.py
├── 📄 tarpit_in.py
├── 📄 update_bl.py
📂 docker/
├── 📄 docker-compose.yaml
├── 📂 grafana
├── 📂 postgres
    ├── 📂 data
📂 standalone/
├── 📄 fake-bl.py
├── 📄 fake.py
```
# Selos Considerados
Os selos considerados são: **Disponíveis**, **Funcionais**, **Sustentáveis** e **Reprodutíveis**

# Informações básicas

Para a execução e replicação dos experimentos, o seguinte ambiente é necessário:

## Requisitos de Hardware:

* Processador: 4 vCPUs ou superior

* Memória RAM: 4GB ou superior

 * Espaço em disco: 20GB livres

* Rede: Conectividade com a internet para consulta a blacklists

## Requisitos de Software:

* Sistema operacional: Debian 12 ou compatível

* Dependências:

* Docker e Docker Compose

* IPTables

* Python 3.9+

* Bibliotecas Python: geoip2, scapy, requests, datetime, psycopg2-binary e ipaddress

# Dependências

O FABR utiliza as seguintes dependências externas:

* AbuseIPDB: Para verificação da reputação dos IPs.

* MaxMind GeoIP: Para geolocalização de IPs.

* Grafana: Para visualização de métricas coletadas.

# Preocupações com segurança

A execução do firewall pode afetar o fluxo de conexões na rede. Recomenda-se:

* Executá-lo inicialmente em um ambiente de testes.

* Realizar backups do banco de dados antes da execução.

* Configurar listas de permissão (wl_address_local) para evitar bloqueios acidentais.

# Instalação



#### Clone o repositório:
```bash
git clone https://github.com/mascosta/FABR.git
```

#### Instalação do Docker
```bash
curl -fsSL https://get.docker.com | bash 
```

#### Instalação demais pacotes

```bash
apt install vim wget bash-completion \
 tcpdump net-tools curl telnet \
 nmap zip unzip cron python3-pip python3-venv -y 
```

#### Criar estrutura complementar ao repositório

```bash
mkdir -p /opt/python  

chmod 777 -R FABR/docker 
```
#### Criando ambiente virtual para instalação das dependências.

```bash
python3 -m venv /opt/python/ 
```

### 1. Baixando e armazenando a base de Geolocalização

Alguns provedores oferecem, de forma gratuita, uma base de dados que relaciona **Endereços IP** com **Geolocalização**. 

Para a solução, foi adotada a base da *MaxMind*, através do processo descrito abaixo:


```bash
# Baixando e instalando o executável do geoipupdate

wget https://github.com/maxmind/geoipupdate/releases/download/v6.1.0/geoipupdate_6.1.0_linux_amd64.deb && \

# Realizando a instalação.

dpkg -i geoipupdate_6.1.0_linux_amd64.deb && \

# Editar o arquivo de configuração

vim /usr/share/doc/geoipupdate/GeoIP.conf
```

A *MaxMind* precisa que seja feito um cadastro para a disponibilização dessa base. Sendo assim, após o cadastro devidamente feito, serão gerados o ```AccountID``` e a ```LicenseKey```.

Sendo necessário apenas inserir essas informações no arquivo citado assim, como o exemplo abaixo:

```conf
# GeoIP.conf file for `geoipupdate` program, for versions >= 3.1.1.
# Used to update GeoIP databases from https://www.maxmind.com.
# For more information about this config file, visit the docs at
# https://dev.maxmind.com/geoip/updating-databases.

# `AccountID` is from your MaxMind account.
AccountID S3u1D4qu1

# Replace YOUR_LICENSE_KEY_HERE with an active license key associated
# with your MaxMind account.
LicenseKey Su4L1c3ns3K3y4qu1

# `EditionIDs` is from your MaxMind account.
EditionIDs GeoLite2-ASN GeoLite2-City GeoLite2-Country
```

Após a configuração, basta gerar o comando abaixo para coleta da base:

```bash
geoipupdate -f /usr/share/doc/geoipupdate/GeoIP.conf
```

Usar o ambiente virtual Python, criado previamente:

```bash
source /opt/python/bin/activate
pip install -r requirements.txt
```

### 2. Executando os containers

A execução dos containers é feita via docker-compose. Por conta do stack de serviços (Banco de dados e dashboard). Para essa execução, basta executar o seguinte comando:

```bash
docker compose -f FABR/docker/docker-compose.yaml up -d
```

Com os containers em execução, faz-se necessário o ajuste para execução das ferramentas. Onde uma executa em forma de daemon e outras em forma de rotinas, carregando e liberando dados de acordo com o agendamento (CRON). 

### 3. Criando a estrutura da base de dados 

Apos a execução dos containers, precisamos criar a estrutura das tabelas antes de realizar qualquer importação por parte da ferramenta e rotinas. Para essa criação, basta seguir os seguintes passos

#### 3.1 - Acessar o PGAdmin4 Web.

Serviço que está configurado no docker compose para ser executado na porta 80.

```bash
http://IP_Do_Servidor
```
#### 3.2 - Realizar login com as credenciais existentes no arquivo ```docker/docker-compose.yaml```

**Atenção**, após três tentativas sem sucesso o usuário é bloqueado.

```yaml
      PGADMIN_DEFAULT_EMAIL: admin@admin.com
      PGADMIN_DEFAULT_PASSWORD: Q1w2e3r4!@#
```
#### 3.3 - Acessar a base de dados local, com os dados existentes no ```docker/docker-compose.yaml```

```yaml 
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: Q1w2e3r4
      POSTGRES_DB: firewall
```

#### 3.4 - Criar estrutura do banco

Basta navegar até o schema **public**, abrir as tabelas, com o botão direito, clicar em *Query tool*, copiar o conteúdo do arquivo ```sql/pgsql.sql```, colar na consulta, selecionar tudo com o ```ctrl+A``` e executar.

Configure as credenciais no arquivo ```daemon/db_config.py```.

### 4. Adicionando dados à base

Popular a tabela local de blacklist e adicionar a rotina de coleta da blacklist ao ```cron```, do sistema operacional

```bash
python3 /etc/fabr/update_bl.py

# Adicionar rotina ao crontab

echo "0 0,12 * * * python3 /etc/fabr/update_bl.py" >> /etc/crontab
```

### 5. Criando o ```daemon``` para execução

Instale e habilite o serviço systemd:

```bash
# Copiar o arquivo do serviço para o diretório do sistema

sudo cp FABR/fabr.service /etc/systemd/system/

# Criar link simbolico dos componentes

ln -s $(PWD)/FABR/daemon /etc/fabr 

# Habilitar o serviço

sudo systemctl daemon-reload
sudo systemctl enable fabr.service
sudo systemctl start fabr.service
```

Verifique o status do serviço:

```bash
sudo systemctl status fabr.service
```

6. Ajustando o dashboard :chart_with_upwards_trend:

O dashboard necessário para exibição da solução é o arquivo *Conexões.json*. Para seu uso, basta acessar ```https://IP_Do_Servidor:3000```. Na interface do grafana, logar com as credenciais iniciais ```admin/admin``` e atlerar a senha à critério.

Depois, apontar o datasource da solução, navegando em:

```
Connections > Add connection > procurar por PostgreSQL > Create a PostgreSQL data source
```

Na criação do data source, basta fazer as seguintes alterações, baseadas nas configurações do docker compose:

**Host:** postgres

**Database:** firewall 

**Username:** admin

**Password:** Q1w2e3r4

**TLS/SSL Mode:** disable

Depois do data source criado, é necessária a importação do arquivo JSON para visualização do dashboard.

```
Dashboards > New > Import > Upload dashboard JSON file
```

Em seguida, basta clicar em ```Load```.


# Teste mínimo

Execute os scripts dentro do diretório ```standalone```, sendo estes:

- ```fake.py```, responsável por coletar endereços IP da base de dados de geolocalização e usa o ```scapy``` para simular a conexão.
```bash
/opt/python/bin/python3 FABR/standalone/fake.py
```

- ```fake_bl.py```, utilização similar ao script anterior, diferenciado pelo uso da base de blacklist para validação do fluxo.
```bash
/opt/python/bin/python3 FABR/standalone/fake_bl.py
```

# Experimentos

Os experimentos estão estruturados para validar as reivindicações do artigo. Cada experimento possui uma subseção detalhando:
- Arquivos de configuração a serem alterados
- Comandos a serem executados
- Flags e parâmetros necessários
- Tempo esperado de execução e recursos utilizados (ex.: 1GB de RAM/Disk)
- Resultado esperado para cada cenário
  
# Licença
Este projeto não está sob nenhuma licença específica, portanto, pode ser utilizado livremente, sem restrições. Use-o conforme desejar.

