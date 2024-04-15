# -*- coding: utf-8 -*-
import telebot, time
import numpy as np

from Dominios import probabilidade as probabilidade_padrao
from TratamentoTexto import gera_mensagem_final

def envia_dicas_telegram(dicas_para_envio):
    """Sumario

    Parametros:
    dicas_para_envio (pandas DataFrame): base de dicas para serem enviadas

    Retorno:
    Prepara o texto da dica e envia a Dica pelo Telegram

   """
    dicas_para_envio = dicas_para_envio.drop_duplicates(['DICA','id_jogo','casa'])
    for j in range(dicas_para_envio.shape[0]):
        series = dicas_para_envio.iloc[j,:]
        # SEMPRE QUE ALTERAR POLITICA DE DICAS AQUI, ALTERAR NO ARMAZENAMENTO DO CODIGO SQLConexao - GERARA MENSAGEM DUPLICADA SE NAO FIZER
        # if series.sport_id ==18 and series.Odd>=3. and series.Odd< 5. and series.valuebet>=3. and series.casa =='BetVictor' :
        string = gera_mensagem_final(series = series) 
        print("VALUEBET QUENTE, ENVIA MENSAGEM")
        manda_mensagem_telegram(idx = retorna_id_chat(esporte = int(series.sport_id)), string = string) 
        print(string)
        # else:
        #     print("dica nao enviada no VIP")
        # if (series.sport_id ==1 and series.Odd>=2. and series.valuebet>=3. and series.casa =='Bet365' and series.DICA in ['1_away', '1_home']  )            or (series.sport_id ==18 and series.Odd>=2.and series.Odd<3. and series.valuebet>=2. and series.casa =='BetVictor') :
        #     print("dica enviada FREE")
        #     manda_mensagem_telegram_free(string, 1.)
        # else:
        #     print("dica nao enviada no FREE")
            


            
def manda_mensagem_telegram(idx, string, BOT_API_TOKEN = "1039119605:AAHsBoGKTMvAU7pCNVAAQrcshfYgoOC0qYI",tempo_sono = 10):
    """Sumario

    Parametros:
    idx (int): id do chat para envio
    string (string): texto a ser enviado
    BOT_API_TOKEN (string): API do bot que enviara
    tempo_sono (int): caso de erro no telegram por muitas mensagens seguidas, esse sera o tempo de pausa entre um envio e outro

    Retorno:
    ID DO CHAT DO ESPORTE

   """
    contagem = 0
    variavel = True
    while variavel == True and contagem < 6:
        contagem = contagem +1
        try:
            tb= telebot.TeleBot(BOT_API_TOKEN)           
            tb.send_message(idx, string,   parse_mode='HTML')
            variavel = False 
        except: 
            print('entrou no except e foi dormir')
            time.sleep(tempo_sono)



def retorna_id_chat(esporte):
    """Sumario

    Parametros:
    esporte (int): id do esporte da consulta

    Retorno:
    ID DO CHAT DO ESPORTE

   """
    id_free = -1001187257152
    id_futebol=-1001151813283
    id_basketball=-1001327853475
    id_am_futebol=-1001449820119
    id_tennis=-1001160654374
    id_baseball=-1001176584782
    id_luta=-1001479558705
    id_cavalo=-1001249877140
    id_outros=-1001460514985
    
    if esporte == 1:
        idx = id_futebol
    elif esporte == 18:
        idx = id_basketball
    elif esporte == 13:
        idx = id_tennis
    elif esporte == 12:
        idx = id_am_futebol
    elif esporte == 16:
        idx = id_baseball
    elif esporte == 9:
        idx = id_luta
    elif esporte == -1:
        idx = id_free
    else:
        idx = id_outros
    return idx


def manda_mensagem_telegram_free(string , probabilidade = probabilidade_padrao):
    """Sumario

    Parametros:
    string (string): texto a ser enviado
    probabilidade (int): percentual de chance de envio da mensagem para o grupo free

    Retorno:
    ID DO CHAT DO ESPORTE

   """
    aleatorio = np.random.uniform()
    if aleatorio < probabilidade : #manda msg pro grupo free
        print("Enviou essa dica para o free tambem")
        
        manda_mensagem_telegram(idx = retorna_id_chat(-1), string = string)