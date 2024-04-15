# PACOTES


import pandas as pd
from datetime import datetime,timedelta
import telebot
import json
from APIDados import retorna_placar_dia
from S3Funcoes import  atualiza_bucket_s3
from Dominios import path_s3_historico, file_s3_historico_name

# FUNCOES

def main(event, context):   

    print("")
    print("Lista Parametros")
    # PARAMETROS
    BOT_API_TOKEN = "1040978461:AAGJNLe1HvkSCfGlXm7MTxR6rhVXAYIvAEc"
    id_chat_adm = -1001448035712
    esportes = [18]
    bet_token = '57659-nlPvoqXEFejq5s'

    data_ontem = datetime.now() + timedelta(days=-1)
    data_string = data_ontem.strftime("%Y%m%d")

    # ABRE HISTORICO

    df_historico = pd.DataFrame()


    # REQUEST #1 API

    eventos_futebol = list()
    for esporte in esportes:
        print("Consulta API Primeira Vez")
        contador = 0
        pagina = 1
        resposta = retorna_placar_dia(bet_token,esporte,data_string,pagina)

        events_total = resposta['pager']['total']
        pag_total = events_total/50 if events_total%50 == 0 else 1 + events_total//50


        # INSERCAO DE NOVOS EVENTOS

        for pagina in range(1,pag_total):

            if pagina != 1:
                print("Consulta API na Pagina" + str(pagina))
                resposta = retorna_placar_dia(bet_token,esporte,data_string,pagina)

            for i in range(len(resposta['results'])):
                if (('Esoccer' not in resposta['results'][i]['league']['name']) and ('Ebasketball' not in resposta['results'][i]['league']['name'])):
                    if resposta['results'][i]['ss'] == None:
                        pass
                    else:
                        try:
                            placar = resposta['results'][i]['ss'].split('-')
                            if esporte == 1:
                                eventos_futebol.append(str(resposta['results'][i]['id']))
                            novo_evento = {'id_esporte': str(esporte), 'id_jogo': str(resposta['results'][i]['id']),'home': str(placar[0]), 'away': str(placar[1]), 'ss':str(resposta['results'][i]['ss'])}
                            df_historico = pd.concat([df_historico,pd.DataFrame(novo_evento,index=[0])]).reset_index(drop=True)
                            contador += 1
                        except:
                                    novo_evento = {'id_esporte': str(esporte), 'id_jogo': str(resposta['results'][i]['id']),'home': "-", 'away': "-", 'ss':str(resposta['results'][i]['ss'])}
                                    if esporte == 1:
                                        eventos_futebol.append(str(resposta['results'][i]['id']))
                                    df_historico = pd.concat([df_historico,pd.DataFrame(novo_evento,index=[0])]).reset_index(drop=True)
                                    contador += 1
                                    print(str(pagina) + ' - ' + resposta['results'][i]['id'])

        print("Faz Filtros e Manda no Telegram")
        esporte_string = "Futebol" if esporte == 1 else "Basquete" if esporte == 18 else "Baseball"
        tb = telebot.TeleBot(BOT_API_TOKEN)
        mensagem = "Resultados capturados com sucesso!\n\n" + str(contador) + " partidas de " + esporte_string
        tb.send_message(id_chat_adm, mensagem, parse_mode='HTML')


    # EXPORTA SAIDA
    print("Exporta para bucket s3")
    atualiza_bucket_s3(df_historico, path_s3_historico, file_s3_historico_name)
    return {
        'statusCode': 200,
        'body': json.dumps('Peguei mais  '+str(df_historico.shape[0] ) + ' novos Placares')}
if __name__ == "__main__":   
    main('', '')





