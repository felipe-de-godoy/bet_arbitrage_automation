from S3Funcoes import s3_upload_csv,s3_read_csv,s3_list_files

# Checa mensagem recebida

from datetime import date, timedelta, datetime
import pandas as pd
HOJE_TEXTO = datetime.now().strftime("%Y%m%d")
ano = HOJE_TEXTO[0:4]
mes = HOJE_TEXTO[4:6]
dia = HOJE_TEXTO[6:8]
ONTEM_TEXTO = (date.today() - timedelta(days=1)).strftime('%Y%m%d')
ano_ontem = ONTEM_TEXTO[0:4]
mes_ontem = ONTEM_TEXTO[4:6]
dia_ontem = ONTEM_TEXTO[6:8]

# Compara dicas calculadas e apostadas de ontem, se nao encontrar

try:
    enviadas  = s3_list_files('s3://magic-bet-raw/DicasCalculadas/'+'ano='+ano_ontem + '/mes='+mes_ontem + '/dia='+dia_ontem+'/')
except:
    enviadas =[]
try:
    recebidas = s3_list_files('s3://magic-bet-raw/DicasApostadas/'+'ano='+ano_ontem + '/mes='+mes_ontem + '/dia='+dia_ontem+'/')
except:
    recebidas =[]
novos = list()
for item in enviadas:
    if item not in recebidas:
        novos.append(int(item))

if novos != []:
    # Se encontrou alguma que foi calculada e não apostada, pega ela e salva como df_msg 
    df_msg = pd.DataFrame(s3_read_csv('s3://magic-bet-raw/DicasCalculadas/'+'ano='+ano_ontem + '/mes='+mes_ontem + '/dia='+dia_ontem+'/', str(novos[0]) + '.csv'))
    dia_aposta = dia_ontem
    mes_aposta = mes_ontem
    ano_aposta = ano_ontem
else:
    #  Senao, tenta faz a mesma coisa para o dia de hoje
    try:
        enviadas  = s3_list_files('s3://magic-bet-raw/DicasCalculadas/'+'ano='+ano + '/mes='+mes + '/dia='+dia+'/')
    except:
        enviadas =[]
    try:
        recebidas = s3_list_files('s3://magic-bet-raw/DicasApostadas/'+'ano='+ano + '/mes='+mes + '/dia='+dia+'/')
    except:
        recebidas =[]
    for item in enviadas:
        if item not in recebidas:
            novos.append(int(item))
    if novos != []:
    
        df_msg = pd.DataFrame(s3_read_csv('s3://magic-bet-raw/DicasCalculadas/'+'ano='+ano + '/mes='+mes + '/dia='+dia+'/', str(novos[0]) + '.csv'))
        dia_aposta = dia
        mes_aposta = mes
        ano_aposta = ano
    else:
        # Se mesmo assim não encontrar dicas nao efetuadas, ele sai do codigo
        exit()

print('Rodando dica numero ' + str(novos[0]) +' do dia '+ ano_aposta+mes_aposta+dia_aposta)
# criei essa variavel para quando for salvar no s3 ja ter o nome preparado  independente se foi dica de hoje ou ontem
caminho_s3_output = 's3://magic-bet-raw/DicasApostadas/'+'ano='+ano_aposta + '/mes='+mes_aposta + '/dia='+dia_aposta+'/'+str(novos[0])+ '.csv'

import time
from time import sleep
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from datetime import datetime
from datetime import timedelta
import telebot


# Funções

def atualiza_bucket(sucesso,df_msg,caminho,odd_apostada,razao):
    df_msg.loc[0,'Sucesso'] = sucesso
    df_msg.loc[0,'Odd_Apostada'] = odd_apostada
    df_msg.loc[0,'Razao'] = razao
    df_msg.loc[0,'Timestamp_Aposta'] = datetime.now()
# inclui parametro caminho para variar de acordo com a data
    s3_upload_csv(df_msg,caminho,'')


def envia_msg(sucesso, msg, razao, odd_apostada):
    BOT_API_TOKEN = "1040978461:AAGJNLe1HvkSCfGlXm7MTxR6rhVXAYIvAEc"
    id_chat_adm = -1001448035712
    
    tb = telebot.TeleBot(BOT_API_TOKEN)
    
    if sucesso:
        mensagem = ('Dica: \n\n' + msg + '\n\n' + 'Status : Aposta feita com sucesso! \n\nOdd : ' +
                    odd_apostada + '\nValor : $0.1')
    else:
        mensagem = ('Dica: \n\n' + msg + '\n\n' + 'Status : Aposta falhou! \n\nRazao : ' + razao)
    
    #print(mensagem)
    
    tb.send_message(id_chat_adm, mensagem, parse_mode='HTML')


# Configurações do driver para Linux VM

options = Options()
options.add_argument("--headless")
options.add_argument("window-size=1400,1500")


# Abrindo driver

flag_pc = 'linux'

print('Abrindo Driver')

if flag_pc == 'linux':
    from webdriver_manager.chrome import ChromeDriverManager
    driver = webdriver.Chrome(ChromeDriverManager().install(), options = options)
else:
    driver = webdriver.Chrome()

print('Driver aberto')


# Importa de/para de campeonatos

import json

with open('/home/ec2-user/betvictor_bot/FINAL_liga_dic.json', 'r') as jsonFile:
#with open('FINAL_liga_dic.json', 'r') as jsonFile:    
    jsonObject = json.load(jsonFile)
    jsonFile.close()


# Mensagem recebida

# msg = """Casa de apostas : BetVictor
# Tipo :  Pre-Match
# Esporte : Basketball
# Campeonato : WNBA
# Jogo : ATL Dream X CON Sun
# Dica : A favor do Visitante
# Odd : 7.5"""

if df_msg.loc[0,'Tipo'] == 1:
    df_msg.loc[0,'Dica'] = 'Time da Casa'
else:
    df_msg.loc[0,'Dica'] = 'Visitante'

df_msg.loc[0,'Esporte'] = 'Basketball'
df_msg.loc[0,'Tipo']    = 'Pre-Match'

msg = df_msg.iloc[0,:].to_string()

# Tratando dica recebida
try:
    champ = df_msg.loc[0,'Campeonato']
    pais  = jsonObject[champ]['pais']
    champ = jsonObject[champ]['liga']
    bet   = df_msg.loc[0,'Dica']
    odd   = df_msg.loc[0,'Odd']
    team1 = df_msg.loc[0,'Time1']
    team2 = df_msg.loc[0,'Time2']

    team1 = team1.replace('Women','(W)')
    team2 = team2.replace('Women','(W)')
except:
    driver.quit()
    razao = 'Favor cadastrar a liga ' + champ
    odd_apostada = 0.
    envia_msg(False, msg, razao, odd_apostada)
    atualiza_bucket(False,df_msg,caminho_s3_output,odd_apostada,razao)
    exit()

# champ = msg.split(":")[4].split("\n")[0][1:]
# pais  = jsonObject[champ]['pais']
# champ = \Object[champ]['liga']
# bet   = msg.split(":")[6].split(" ")[4].split("\n")[0]
# odd   = msg.split(":")[7].split(" ")[1]
# team1 = msg.split(":")[5].split("X")[0][1:-1]
# team2 = msg.split(":")[5].split("X")[1].split("\n")[0][1:]

odd_cut = 5.0 # Quantas vezes menor é a odd que eu aceito
valor   = 0.1 # Valor em dolares

print('De/PARA lido e abrindo site BetVictor')


# Abrindo Betvictor

try:
    driver.get("https://www.betvictor.com/en-en")
    driver.set_window_size(1440, 1500)
except:
    driver.quit()
    razao = 'Nao foi possível abrir o site BetVictor'
    odd_apostada = 0.
    envia_msg(False, msg, razao, odd_apostada)
    atualiza_bucket(False,df_msg,caminho_s3_output,odd_apostada,razao)
    exit()

sleep(10)

print('Site Aberto')


# Aceitando cookies

sleep(10)

try:
    print('Tentando aceitar cookies')
    driver.find_element(By.CLASS_NAME, "bvs-button-group").click()
    print('Cookies aceitos')
except:
    driver.quit()
    razao = 'Nao foi possível aceitar os cookies'
    odd_apostada = 0.
    envia_msg(False, msg, razao, odd_apostada)
    atualiza_bucket(False,df_msg,caminho_s3_output,odd_apostada,razao)
    exit()
    
sleep(5)


# Clicando em Login

try:
    driver.find_element(By.LINK_TEXT, "Log In").click()
    element = driver.find_element(By.LINK_TEXT, "Log In")
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()
    element = driver.find_element(By.CSS_SELECTOR, "body")
except:
    driver.quit()
    razao = 'Nao encontrou o botao de Login'
    odd_apostada = 0.
    envia_msg(False, msg, razao, odd_apostada)
    atualiza_bucket(False,df_msg,caminho_s3_output,odd_apostada,razao)
    exit()
    
sleep(5)

print('Login clicado')


# Preenchendo informações e fazendo Login

try:
    driver.find_element(By.NAME, "username").send_keys("miranda.gabriel.soares@gmail.com")
    driver.find_element(By.NAME, "password").send_keys("Gsm*1231")
    element = driver.find_element(By.CSS_SELECTOR, ".is-primary:nth-child(4)")
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()
    time.sleep(5)
    driver.find_element(By.CSS_SELECTOR, ".is-primary:nth-child(4)").click()
    time.sleep(10)
except:
    driver.quit()
    razao = 'Nao foi possível realizar o login'
    odd_apostada = 0.
    envia_msg(False, msg, razao, odd_apostada)
    atualiza_bucket(False,df_msg,caminho_s3_output,odd_apostada,razao)
    exit()

print('Login Realizado')


# Seleciona basquete
try:
    element = driver.find_element(By.CSS_SELECTOR, "body")
    driver.execute_script("window.scrollTo(0,14)")
    driver.find_element(By.LINK_TEXT, "Basketball").click()
except:
    driver.quit()
    razao = 'Nao foi possível selecionar o esporte Basquete'
    odd_apostada = 0.
    envia_msg(False, msg, razao, odd_apostada)
    atualiza_bucket(False,df_msg,caminho_s3_output,odd_apostada,razao)
    exit()
    
sleep(16)

print('Basquete selecionado')


# Seleciona Competitions
try:
    print(driver.find_element(By.CSS_SELECTOR, ".bvs-button-tab:nth-child(1)"))
    print(driver.find_elements(By.CSS_SELECTOR, ".bvs-button-tab"))
    for elemento in driver.find_elements(By.CSS_SELECTOR, ".bvs-button-tab"):
        print(elemento.text)
        if elemento.text == 'Competitions':
            elemento.click()
            break
        else:
            pass
except:
    driver.quit()
    razao = 'Nao foi possível selecionar a tab Competitions'
    odd_apostada = 0.
    envia_msg(False, msg, razao, odd_apostada)
    atualiza_bucket(False,df_msg,caminho_s3_output,odd_apostada,razao)
    exit()

sleep(10)

print('Aba competicao selecionada')


# Seleciona país e expande a lista se necessário

try:
    for item in driver.find_elements(By.CSS_SELECTOR, ".bvs-card"):
        if pais in item.text:
            if 'open' not in item.get_attribute('class'):
                item.click()
except:
    driver.quit()
    razao = 'Nao conseguiu encontrar a lista de paises'
    odd_apostada = 0.
    envia_msg(False, msg, razao, odd_apostada)
    atualiza_bucket(False,df_msg,caminho_s3_output,odd_apostada,razao)
    exit()

time.sleep(10)

print('Pais selecionado')


# Seleciona Liga

try:
    driver.find_element(By.LINK_TEXT, champ).click()
    driver.execute_script("window.scrollTo(0,0)")
except:
    driver.quit()
    razao = 'Nao conseguiu encontrar a Liga correta'
    odd_apostada = 0.
    envia_msg(False, msg, razao, odd_apostada)
    atualiza_bucket(False,df_msg,caminho_s3_output,odd_apostada,razao)
    exit()

time.sleep(12)

print('Liga selecionada')


# Seleciona partida e aposta a ser realizada

if 'Money Line' in driver.find_element(By.CSS_SELECTOR, ".bvs-carousel__slider .active").text:
    pass
else:
    for item in driver.find_elements(By.CSS_SELECTOR, ".bvs-carousel__slider .bvs-button-card-alternative"):
        if 'Money Line' in item:
            item.click()
            sleep(5)

try:
    check = driver.find_elements(By.CSS_SELECTOR, ".inply-coupon-row")
except:
    driver.quit()
    razao = 'Nao conseguiu encontrar a lista de partidas'
    odd_apostada = 0.
    envia_msg(False, msg, razao, odd_apostada)
    atualiza_bucket(False,df_msg,caminho_s3_output,odd_apostada,razao)
    exit()

encontrado = False
razao = 'Nao conseguiu encontrar o Time 1'
for item in driver.find_elements(By.CSS_SELECTOR, ".inply-coupon-row"):
    if encontrado == True:
        break
    else:
        pass

    continua = False

    for time_str in team1.split(" "):
        if (time_str in item.text) and (time_str not in '(W)'):
            continua = True
            break

    if continua:
        continua = False
        for time_str in team2.split(" "):
            if (time_str in item.text) and (time_str not in '(W)'):
                if 'Suspended' in item.text:
                    driver.quit()
                    razao = 'Encontrou a partida mas nao tem odd disponivel - partida suspensa'
                    odd_apostada = 0.
                    envia_msg(False, msg, razao, odd_apostada)
                    atualiza_bucket(False,df_msg,caminho_s3_output,odd_apostada,razao)
                    exit()
                else:
                    continua = True
                    break
        
        if not continua:
            razao = 'Nao conseguiu encontrar o Time 2'
            odd_apostada = 0.
            # driver.quit()
            # envia_msg(False, msg, razao, odd_apostada)
            # atualiza_bucket(False,df_msg,caminho_s3_output,odd_apostada,razao)
            # exit()

    if continua:
        encontrado = True
        if bet == 'Visitante':
            cont = 2
        else:
            cont = 1

        try:
            for item2 in item.find_elements(By.CSS_SELECTOR, ".bvs-button-multi-sport:nth-child(" + str(cont) + ") > strong"):
                if float(odd) <= float(item2.text)*odd_cut:
                    item2.click()
                    odd_apostada = item2.text
                    break
        except:
            driver.quit()
            razao = 'Nao conseguiu encontrar a odd esperada'
            odd_apostada = 0.
            envia_msg(False, msg, razao, odd_apostada)
            atualiza_bucket(False,df_msg,caminho_s3_output,odd_apostada,razao)
            exit()

if encontrado == False:
    driver.quit()
    odd_apostada = 0.
    envia_msg(False, msg, razao, odd_apostada)
    atualiza_bucket(False,df_msg,caminho_s3_output,odd_apostada,razao)
    exit()


time.sleep(10)


# Seleciona campo de valor

try:
    driver.find_element(By.CSS_SELECTOR, ".js-stake-value").click()
except:
    driver.quit()
    razao = 'Nao conseguiu selecionar o campo de valor'
    envia_msg(False, msg, razao, odd_apostada)
    atualiza_bucket(False,df_msg,caminho_s3_output,odd_apostada,razao)
    exit()

time.sleep(5)


# Seleciona +1 USD para ser apostado

# for item in driver.find_elements(By.CSS_SELECTOR, ".betslip-keypad__quick-stakes > .bvs-link"):
#     if ('1' in item.text) and ('0' not in item.text):
#         for i in range(0,valor):
#             item.click()

# time.sleep(3)


# Seleciona +0.1 USD para ser apostado - FASE de Testes

try:
    for item in driver.find_elements(By.CSS_SELECTOR, ".betslip-keypad-keys"):
        for tab_item in item.find_elements(By.TAG_NAME, 'td'):
            if ('.' in tab_item.text):
                tab_item.click()
        for tab_item in item.find_elements(By.TAG_NAME, 'td'):
            if ('1' in tab_item.text):
                tab_item.click()

except:
    driver.quit()
    razao = 'Nao conseguiu colocar o valor na tela de aposta'
    envia_msg(False, msg, razao, odd_apostada)
    atualiza_bucket(False,df_msg,caminho_s3_output,odd_apostada,razao)
    exit()

time.sleep(3)


# Confirma Valor

try:
    driver.find_element(By.CSS_SELECTOR, ".betslip-keypad-enter").click()
except:
    driver.quit()
    razao = 'Nao conseguiu confirmar o valor'
    envia_msg(False, msg, razao, odd_apostada)
    atualiza_bucket(False,df_msg,caminho_s3_output,odd_apostada,razao)
    exit()

time.sleep(3)


# Confirma Aposta

try:
    driver.find_element(By.ID, "place_bets_button").click()
except:
    driver.quit()
    razao = 'Nao conseguiu confirmar a aposta'
    envia_msg(False, msg, razao, odd_apostada)
    atualiza_bucket(False,df_msg,caminho_s3_output,odd_apostada,razao)
    exit()

time.sleep(5)


# Limpa tela de aposta

try:
    driver.find_element(By.ID, "clear_betslip").click()
except:
    driver.quit()
    razao = 'Nao conseguiu limpar a tela, mas a aposta foi feita'
    envia_msg(True, msg, razao, odd_apostada)
    atualiza_bucket(True,df_msg,odd_apostada,razao)
    exit()

time.sleep(5)


# Fecha janela

driver.quit()


# Salva aposta no bucket

razao = 'Sucesso'
atualiza_bucket(True,df_msg,odd_apostada,razao)


# Manda mensagem no telegram

envia_msg(True, msg, razao, odd_apostada)
