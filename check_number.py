
import requests, logging, socket,os, time, wx, sys
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


def timestamp ():    
    """ Retorna tempo  atual em segundos"""       
    t = time.time()
    return time.ctime(t)

def initCountTime(print_time=False):
    """ Inicia contagem de tempo """
    if print_time:
        print(timestamp())
    t_i = time.time() 
    return t_i

def finishCountTime(t_i, print_time=False):
    """ Encerra a contagem """
    if print_time:
        print(timestamp())
    t_f = int(time.time() - t_i)
    return t_f

def get_path_file(wildcard):
    """Abre janela de dialogo para abrir arquivo

    Args:
        wildcard (str): filtro de arquivos

    Returns:
        str: caminho do arquivo
    """
    try:
        app = wx.App(None)
        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        dialog = wx.FileDialog(None, 'Selecione o arquivo CSV', wildcard=wildcard, style=style)
        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
        else:
            path = None
        dialog.Destroy()
        return path
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error('ERRO DURANTE EXECUÇÃO {}: TIPO - {} - ARQUIVO - {} - LINHA - {} - MESSAGE:{}'.format(get_path_file.__name__, exc_type, fname, exc_tb.tb_lineno, exc_type.__doc__.replace('\n', '')))

def get_csv(delimiter=";"):
    """Abre janela para selecionar arquivo csv e realiza a leitura

    Returns:
        pd.DataFrame: planilha do csv
    """
    try:
        csv_path = None
        while csv_path is None:
            # filtro apenas arquivos csv
            csv_path = get_path_file("*.csv")
        # realiza leitura do csv
        df = pd.read_csv(csv_path, delimiter=delimiter)
        return df
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error('ERRO DURANTE EXECUÇÃO {}: TIPO - {} - ARQUIVO - {} - LINHA - {} - MESSAGE:{}'.format(get_csv.__name__, exc_type, fname, exc_tb.tb_lineno, exc_type.__doc__.replace('\n', '')))

def check_internet():
    timeout = 10
    try:
        requests.get('https://www.google.com', timeout=timeout)
        return True
    except ConnectionError:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error('ERRO DURANTE EXECUÇÃO {}: TIPO - {} - ARQUIVO - {} - LINHA - {} - MESSAGE:{}'.format(check_internet.__name__, exc_type, fname, exc_tb.tb_lineno, exc_type.__doc__.replace('\n', '')))
        return False
t_i = initCountTime()
dataframe = get_csv()
# lista para armazenar os numeros informados
numbers = []
for number in dataframe['Telefone']:
    if type(number) == 'str':
        number = number.replace('(', '')
        number = number.replace(')', '')
        number = number.replace(' ', '')
        number = number.replace('-', '')
        try:
            int(number)
            numbers.append(number)
        except:
            print()
    else:
        numbers.append(number)
# leitura via terminal dos numeros
""" while True:
    print('O numero deve ser no formato 64993457867')
    number = input("Digite o numero: ")
    if number:
        # testa se foi digitado apenas numeros
        try:
            int(number)
            numbers.append(number)
        except:
            print('O numero deve ser no formato 64993457867')
    else: # se não foi digitado nada encerra o loop
        break """

# https://web.whatsapp.com/send/?phone=%2B556499280948&text&type=phone_number&app_absent=0
# monta lista de links com os numeros informados
links_numbers = {x:'https://web.whatsapp.com/send/?phone=%2B55{}&text&type=phone_number&app_absent=0'.format(x) for x in numbers}

# configuração logger
# hostname da máquina que executa o script
hostname = socket.gethostname()
# formato do log
logger = logging.getLogger('check_number')
# configura nivel de log
logger.setLevel('DEBUG')

if check_internet():
    try:
        # verifica sistema operacional
        if os.name == 'nt':
            print('Windows')
            # configuração inicial webbdriver no chromium
            service = ChromeService(executable_path=ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install())
            # diretorio temp do windows
            path_log = os.environ['TEMP']
            log_format = '%(hostname)s - %(asctime)s - %(name)s - %(levelname)s - %(message)s'
            # aplica formato 
            formatter = logging.Formatter(log_format, defaults={"hostname": hostname})
        else:
            print('Linux')
            # configuração inicial webbdriver no chromium
            service = ChromeService(executable_path=ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
            # caminho do log
            path_log = os.path.join(os.environ['HOME'], '.check_number')
            # formato do log
            log_format = '{} - %(asctime)s - %(name)s - %(levelname)s - %(message)s'.format(hostname)
            formatter = logging.Formatter(log_format)
    except Exception as err:
        logger.error(err)
else:
    logger.error("Erro de conexão")
    raise ConnectionError("Internet fora do ar")

# configuração inicial webbdriver
chrome_options = Options()
# inicia o chrome com a janela maximizada
chrome_options.add_argument("--start-maximized")
try:
    driver = webdriver.Chrome(service=service, options=chrome_options)
except:
    # mude o valor de acordo com o local de instalação do navegador chrome na sua máquina
    chrome_options.binary_location = "C:\Program Files\Google\Chrome\Application\chrome.exe"
    driver = webdriver.Chrome(service=service, options=chrome_options)
    # driver2 = webdriver.Chrome(service=service, options=chrome_options)
# montando caminho do 
path_hostname = os.path.join(path_log, "check_number-{}".format(hostname))
# nome do arquivo de log
file_handler = logging.FileHandler("{}.log".format(path_hostname))
# configura formato do log
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

if check_internet():
    #login to WhatsApp web
    try:
        driver.get("https://web.whatsapp.com/")
    except Exception as err:
        logger.error("Erro no driver "+err)
else:
    logger.error("Erro de conexão")
    raise ConnectionError("Internet fora do ar")

# wait para scanear QR code do celular
wait = WebDriverWait(driver, 600)
# espera para carregar interface do whatsapp
time.sleep(10)
chat_header = wait.until(EC.visibility_of_element_located((By.XPATH, "//header[@data-testid='chatlist-header']")))
# dicionario para salvar numero checados
check_numbers = {'COM WHATSAPP': [], 'SEM WHATSAPP':[]}
if chat_header:
    for number, link in links_numbers.items():
        # abre link de conversa no numero
        driver.get(link)
        # aguarda carregamento
        time.sleep(5)
        try:
            # buscar popup de numero invalido
            element = driver.find_element(By.XPATH, "//div[@data-testid='confirm-popup']")
        except:
            # se não encontrar atribui vazio para variavel
            element = None
        if element:
            # adiciona informacao no log
            logger.info("Numero {} não existe conta no whatsapp".format(number))
            # adiciona no dicionario
            check_numbers.get('SEM WHATSAPP').append(number)  
            check_numbers.get('COM WHATSAPP').append('')  
            print('não existe')
        else:
            # adiciona informacao no log
            logger.info("Numero {} existe conta no whatsapp".format(number))
            # adiciona no dicionario
            check_numbers.get('COM WHATSAPP').append(number)  
            check_numbers.get('SEM WHATSAPP').append('')
        
    # gerando dataframe com dicionario
    df = pd.DataFrame(data=check_numbers)
    # salva csv
    df.to_csv('numeros_checados.csv', index=False, encoding='utf-8')
    df.to_excel('numeros_checados.xlsx', index=False, sheet_name="numeros_checados")
    # fecha navegador
    driver.quit()
t_f = finishCountTime(t_i)
segundos = t_f%60
minutos = int(t_f/60)
if minutos > 60:
    horas = int(minutos/60)
    minutos = minutos%60
else:
    horas = 0
print("Executado em {} horas {} minutos {} segundos".format(horas, minutos, segundos))