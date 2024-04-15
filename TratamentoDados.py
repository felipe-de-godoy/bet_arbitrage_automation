# -*- coding: utf-8 -*-
# Pacotes
import pandas as pd
import numpy as np
import time
from datetime import date, timedelta, datetime
from APIDados import retorna_placar
# Funcoes
from S3Conexao import consulta_s3_dicas
from TratamentoTexto import trata_handcap
from APIDados import retorna_jogos, retorna_odd
# Constantes
from Dominios import momentos10 ,momentos11 ,momentos12 ,momentos0 ,colunas_ods_1,colunas_ods_2 ,colunas_ods_3,colunas_hand, colunas_consulta_jogos
from Dominios import colunas_base_odes, colunas_DICAS, colunas_hand, colunas_nao_nulas, colunas_ods_1, colunas_ods_1, colunas_ods_2, colunas_ods_3, colunas_ods_total, jogos_colunas

from Dominios import QUERY_POLITICA_DICAS
# PARAMETROS
# ONTEM_TEXTO = (date.today() - timedelta(days=1)).strftime('%Y%m%d')
# HOJE_TEXTO = datetime.now().strftime("%Y%m%d")
# momentos10 = ['id', 'home_od', 'draw_od', 'away_od', 'ss', 'time_str', 'add_time']  
# momentos11 = ['id', 'home_od', 'handicap', 'away_od', 'ss', 'time_str', 'add_time']  
# momentos12 = ['id', 'over_od', 'handicap', 'under_od', 'ss', 'time_str', 'add_time']

# momentos0 = ['start', 'kickoff', 'end']

# tipos_aposta = ['_1', '_2', '_3']

# colunas_ods_1 = ['end_1_away_od', 'end_1_draw_od','end_1_home_od']
# colunas_ods_2 = ['end_2_away_od', 'end_2_home_od']
# colunas_ods_3 = ['end_3_over_od', 'end_3_under_od']

# colunas_hand = ['end_1_handicap','end_2_handicap', 'end_3_handicap']
def retorna_jogos_odes( lista_esporte, tipo_processamento = 1,caminho_base_odes_input='', caminho_base_jogos_input = '', quantidade_de_paginas =1):
    """Sumario

    Parametros:
    esporte(lista de ints): lista dos id's do esportes que estao sendo consultado
    tipo_processamento(int){1,2,3}: 1 para processamento normal, 2 para consulta sql e 3 para consulta no pc
    caminho_base_odes_input(string): caminho do csv de odes no pc
    caminho_base_jogos_input(string): caminho do csv de jogos no pc
    quantidade_de_paginas (int): numeros de paginas para consultar na api
    Retorno:
    Base de jogos e base de odes para as dicas
    """
    if tipo_processamento == 1:
        jogos_agora = pd.DataFrame([], columns = colunas_consulta_jogos)
        for esporte in lista_esporte:
            for pagina in range(1,quantidade_de_paginas+1):
                try:
                    jogos_agora = jogos_agora.append(trata_jogos(resposta=retorna_jogos(esporte=esporte, pagina = pagina)), sort=False)
                except:
                    pass
        data_pasta_salvamento = str(int(time.time()))
        HOJE_TEXTO = datetime.now().strftime("%Y%m%d")
        ano = HOJE_TEXTO[0:4]
        mes = HOJE_TEXTO[4:6]
        dia = HOJE_TEXTO[6:8]
        s3_upload_csv(jogos_agora,'s3://magic-bet-raw/jogos-brutos/'+'ano='+ano + '/mes='+mes + '/dia='+dia+'/',data_pasta_salvamento +'.csv')

        # EMPILHA COM HISTORICO DE JOGOS E ARMAZENA NUMA BASE DE JOGOS

        jogos_total_consulta = pd.DataFrame([], columns=jogos_colunas)
        odds_total_consulta = pd.DataFrame([], columns=colunas_base_odes)
        # odes_envio_total = pd.DataFrame([], columns=colunas_DICAS)
        # odes_nao_enviadas_total = pd.DataFrame([], columns=colunas_DICAS)
        # odes_envio = pd.DataFrame([], columns=colunas_DICAS)
        # odes_nao_enviadas = pd.DataFrame([], columns=colunas_DICAS)
        # PARAMETROS
        agora = time.time()
        jogos_total_consulta = jogos_agora.copy()
        jogos_agora = jogos_agora[jogos_agora['ss'].isnull()]

        # agora2 = datetime.today()
        # hora = agora2.hour
        # minuto = agora2.minute
        # if hora>0 and hora<6:
        #     tempo_minimo = (hora * 60 - minuto)*60
        # else:
        tempo_minimo = 20*60  #20 minutos de delay por padrao, so prematch
        
        jogos_agora = jogos_agora[jogos_agora['time'].astype(int) > agora + tempo_minimo ]
        jogos_agora = jogos_agora[jogos_agora['time'].astype(int) < agora + 86400]
        jogos_agora = jogos_agora[~jogos_agora['league_name'].str.contains(
            "Ebasketball")]
        jogos_agora = jogos_agora[~jogos_agora['league_name'].str.contains(
            "Esoccer")]
        # Pego json de cada jogo
        jogos_odds = []
        for idx in jogos_agora['id_jogo']:
            jogos_odds = jogos_odds + [retorna_odd(event_id=str(idx))]
        todas_odes = pd.DataFrame([], columns=colunas_base_odes)

        print('Retorna ODES para os jogos :')
        print(list(jogos_agora['id_jogo']))

        # for i in tqdm.tqdm(jogos_odds):
        for i , j in list(zip(jogos_odds, jogos_agora['sport_id'])):
            try:
                if i[0]['results'].keys() != []:

                    odds_jogo = trata_odd(
                        api_odes_json=i[0], event_id=i[1], esporte=int(j))
                    todas_odes = todas_odes.append(odds_jogo, sort=True)
            except:
                pass
        s3_upload_csv(todas_odes,'s3://magic-bet-raw/odes-brutas/'+'ano='+ano + '/mes='+mes + '/dia='+dia+'/',data_pasta_salvamento +'.csv')
        # CONVERTE A COLUNA DE TEMPO DA API PARA DATETIME
        todas_odes = transforma_em_datetime_add(todas_odes=todas_odes)
        # Transforma handcap num valor do nosso dominio, como a funcao retorna a base inteira, eu fiz assim
        todas_odes = trata_handcap(base=trata_handcap(
            base=todas_odes, coluna=colunas_hand[1]), coluna=colunas_hand[2])
        # SEPARA BASE PARA ARMAZENAMENTO
        odds_total_consulta = odds_total_consulta.append(todas_odes, sort=True)
        odds_total_consulta=odds_total_consulta.dropna(how='all',subset = colunas_ods_total,axis=0) #dropa linhas com todas odes vazias
        # A API AS VEZES RETORNA TODOS VALORES VAZIOS EXCETO A CASA, NESSA ETAPA EU DROP ESSES CARAS
        todas_odes[~pd.isnull(todas_odes[colunas_ods_total]).all(axis=1)]

        try:
            jogos_agora_merge = jogos_agora.drop(['Timestamp'], axis=1)
        except:
            jogos_agora_merge = jogos_agora
        jogos_atuais = pd.merge(todas_odes, jogos_agora_merge, on='id_jogo')
        jogos_atuais['id_jogo'] = jogos_atuais['id_jogo'].astype(int)

        jogos_atuais[colunas_ods_total] = jogos_atuais[colunas_ods_total].apply(pd.to_numeric, errors='coerce')
        jogos_atuais['end_1_handicap'] = 0
        # Tiro as que ja foram enviadas

        mensagens_enviadas_hist2 = consulta_s3_dicas()
        # mensagens_enviadas_hist2 = mensagens_enviadas_hist2.query(QUERY_POLITICA_DICAS)[['id_jogo', 'sport_id']]
        mensagens_enviadas_hist2 = mensagens_enviadas_hist2[['id_jogo', 'sport_id']]
        mensagens_enviadas_hist2.columns = ['id_jogo', 'esporte']
        mensagens_enviadas_hist2[['id_jogo', 'esporte']] = mensagens_enviadas_hist2[['id_jogo', 'esporte']].astype(float).astype(int)
        mensagens_enviadas_hist2['flag_jogo_antigo'] = 1

        jogos_atuais = pd.merge(jogos_atuais, mensagens_enviadas_hist2, how='left',  on=['id_jogo', 'esporte'])

        print('pre filtro de jogo repetido')
        print(jogos_atuais.shape)

        jogos_atuais = jogos_atuais[jogos_atuais['flag_jogo_antigo'] != 1]
        jogos_atuais = jogos_atuais.drop(['flag_jogo_antigo'], axis=1)
        print('pos filtro de jogo repetido')
        print(jogos_atuais.shape)

        print("tamanho da base de dicas historica")
        print(mensagens_enviadas_hist2.shape)
    else:
        #Quebro entre caso de captura da base no banco sql ou a partir de csv na maquina
        if tipo_processamento == 2:

            pass
            # comentei na migracao para s3, se for voltar a usar rever a estrutura
            # odds_total_consulta = retorna_base_sql_server(string_colunas='*', tabela_sql='VW_ODES', CONNECTION_STRING=CONNECTION_STRING)
            # jogos_total_consulta = retorna_base_sql_server(string_colunas='*', tabela_sql=' TB_JOGOS_FINAL', CONNECTION_STRING=CONNECTION_STRING)
        elif tipo_processamento == 3:

            # from SQLConexao import  retorna_base_sql_server, salva_sql_server
            # odds_total_consulta = retorna_base_sql_server(string_colunas='distinct TOP (10000) * ', tabela_sql='TB_ODES_FINAL' )
            # odds_total_consulta.to_csv('amostra_odes.csv', index = False)
            # jogos_total_consulta = retorna_base_sql_server(string_colunas='distinct TOP (1000) * ', tabela_sql=' TB_JOGOS_FINAL')
            # jogos_total_consulta.to_csv('amostra_jogos.csv', index = False)

            jogos_total_consulta = pd.read_csv(caminho_base_jogos_input)
            odds_total_consulta = pd.read_csv(caminho_base_odes_input)
        jogos_atuais = pd.merge(odds_total_consulta, jogos_total_consulta, on='id_jogo')
        jogos_atuais['id_jogo'] = jogos_atuais['id_jogo'].astype(int)
        jogos_atuais[colunas_ods_total] = jogos_atuais[colunas_ods_total].apply(
            pd.to_numeric, errors='coerce')
        jogos_atuais['end_1_handicap'] = 0

    return jogos_total_consulta, odds_total_consulta, jogos_atuais 

def trata_jogos(resposta):
    """Sumario

    Parametros:
    resposta(json): dict de jogos resultado da consulta a api

   """
    df_full = pd.DataFrame([], columns = colunas_consulta_jogos)

    if resposta['success']  == 1:
        # print('ITERA ENTRE JOGOS')
        for i in range(len(resposta['results'])):
            league     = resposta['results'][i]['league']
            home       = resposta['results'][i]['home']
            away       = resposta['results'][i]['away']



            id_jogo     = resposta['results'][i]['id']
            sport_id      = resposta['results'][i]['sport_id']
            time1          = resposta['results'][i]['time']
            time_status   = resposta['results'][i]['time_status']
            try:
                ss            = resposta['results'][i]['ss']
            except:
                ss = ""
            try:
                bet365_id     = resposta['results'][i]['bet365_id']
            except:
                bet365_id     = np.nan 
            league_id     = league['id']
            league_name   = league['name']
            league_cc     = league['cc']
            home_id       = home['id']
            home_name     = home[ 'name']
            home_image_id = home['image_id']
            home_cc       = home['cc']
            away_id       = away['id']
            away_name     = away[ 'name']
            away_image_id = away['image_id']
            away_cc       = away['cc']
        #PAra jogos live tem esses parametros abaixo tambem
        #     timer      = resposta['results'][i]['timer']
        #     scores     = resposta['results'][i]['scores']
        #     timer_tm      = timer['tm'] 
        #     timer_ts      = timer['ts']
        #     timer_tt      = timer['tt'] 
        #     timer_ta      = timer['ta'] 
        #     timer_md      = timer['md']
        #     scores_home   = scores['2']['home']
        #     scores_away   = scores['2']['away']

            linha = [id_jogo,sport_id,time1,time_status,league_id,league_name,league_cc,home_id,home_name,home_image_id,home_cc,away_id,away_name,away_image_id,away_cc,ss,bet365_id]
            df = pd.DataFrame([linha])
            df.columns = colunas_consulta_jogos

            df_full = df_full.append(df,sort=True)
        df_full['Timestamp'] = pd.to_datetime(time.time(), unit='s' )
        df_full.drop_duplicates()
        df_full = df_full.reset_index(drop = True)
        # print('RETORNA BASE DE JOGOS')
    else:
        print("Consulta sem sucesso na api")
    return df_full
def trata_placar_lista(jogos):
    """Sumario

    Parametros:
    jogos(lista de int): Lista dos ids dos jogos a serem consultados

   """
    df_resultado = pd.DataFrame()
    bet_token = '57659-nlPvoqXEFejq5s'
    for jogo in jogos:
        api_resultado_json = retorna_placar(jogo, bet_token)
        try:
            ss = api_resultado_json['results'][0]['ss']
        except:
            ss = None
        if ss ==None:
            placar = ['-1', '-1']
        else:
            placar = ss.split('-')

        try:
            objeto = {
                  'id_jogo':jogo,
                  'home':placar[0],
                  'away':placar[1],
                    'ss' :ss}
        except:
            objeto = {
                  'id_jogo':jogo,
                  'home':'-1',
                  'away':'-1',
                    'ss' :ss}            
        df_resultado = df_resultado.append(pd.DataFrame(objeto,index=[0]))
    return df_resultado
def trata_odd(api_odes_json, event_id, esporte):
    """Sumario

    Parametros:
    api_odes_json(json): dict odes resultado da consulta na API
    event_id(ind): id do jogo
    esporte(int): id do esporte

   """
    # import time
    # print('TRANSFORMA JSON ODES EM TABELA, JOGO ' +  event_id)
    casas = list(api_odes_json['results'].keys())
    colunas_API_ODES = ['start_1_id', 'start_1_home_od', 'start_1_draw_od', 'start_1_away_od', 'start_1_ss', 'start_1_time_str', 'start_1_add_time', 'start_2_id', 'start_2_home_od', 'start_2_handicap', 'start_2_away_od', 'start_2_ss', 'start_2_time_str', 'start_2_add_time', 'start_3_id', 'start_3_over_od', 'start_3_handicap', 'start_3_under_od', 'start_3_ss', 'start_3_time_str', 'start_3_add_time']
    
    df0 = pd.DataFrame([], columns = colunas_API_ODES+['casa','esporte', 'matching_dir', 'odds_update_1', 'odds_update_2', 'odds_update_3'])

    df = pd.DataFrame([], columns = colunas_API_ODES+['casa'])
    tipos_aposta = ['_1', '_2', '_3']
    momentos1 = [str(esporte) + l for l in tipos_aposta]
    for casa in casas:

        df0.loc[0,'casa']= casa 
        df0.loc[0,'id_jogo'] = event_id
        df0.loc[0,'esporte'] = esporte
        
        df0.loc[0,'matching_dir'] = api_odes_json['results'][casa]['matching_dir']
        
        try:
            df0.loc[0,'odds_update'+ tipos_aposta[0]] = api_odes_json['results'][casa]['odds_update'][momentos1[0]]
        except:
            df0.loc[0,'odds_update'+ tipos_aposta[0]] = None
        try:
            df0.loc[0,'odds_update'+ tipos_aposta[1]] = api_odes_json['results'][casa]['odds_update'][momentos1[1]]
        except:
            df0.loc[0,'odds_update'+ tipos_aposta[1]] = None
        try:
            df0.loc[0,'odds_update'+ tipos_aposta[2]] = api_odes_json['results'][casa]['odds_update'][momentos1[2]]
        except:
            df0.loc[0,'odds_update'+ tipos_aposta[2]] = None
        
        

        for k in momentos0:
            i = momentos1[0]
            i2 = tipos_aposta[0]
            for j in momentos10:
                try:
                    df0.loc[0,k+ i2+ '_'+ j] = api_odes_json['results'][casa]['odds'][k][i][j]
                except:
                    df0.loc[0,k+ i2+ '_'+ j] = np.nan 
            i = momentos1[1]
            i2 = tipos_aposta[1]
            for j in momentos11:
                try:
                    df0.loc[0,k+ i2+ '_'+ j] = api_odes_json['results'][casa]['odds'][k][i][j]
                except:
                    df0.loc[0,k+ i2+ '_'+ j] = np.nan 
            i = momentos1[2]
            i2 = tipos_aposta[2]
            for j in momentos12:
                try:
                    df0.loc[0,k+ i2+ '_'+ j] = api_odes_json['results'][casa]['odds'][k][i][j]
                except:
                    df0.loc[0,k+ i2+ '_'+ j] = np.nan 
        #INCLUIDO 05/07/2020
        
        

        df=df0.append(df,sort=True)
    # print('TRANSFORMA JSON ODES EM TABELA, JOGO ' +  event_id)
    return df




def transforma_em_datetime_add(todas_odes):
    """Sumario

    Parametros:
    todas_odes(pandas DataFrame): Base de odes para tratamento da coluna add_time

   """
    for i in ['end_1_add_time','end_2_add_time','end_3_add_time']:
        try:
            todas_odes[i] = pd.to_datetime(todas_odes[i], unit='s' )
        except:
            pass
    todas_odes['Timestamp']= pd.to_datetime(time.time(), unit='s' )
    
    return todas_odes




# def manipula_por_tipo(melhores_odes,odes_nao_enviadas,odes_envio):
#     """Sumario

#     Parametros:
#     jogo_selc(pandas DataFrame): Base com as odes para calculo da Valuebet

#    """
#     #Trata _1
#     melhores_odes2 = melhores_odes[melhores_odes['DICA'].isin(colunas_ods_1)]
#     try:
#         valuebet_max_home_1 = max(melhores_odes2[melhores_odes2['DICA']==colunas_ods_1[2]]['valuebet'])
#     except:
#         valuebet_max_home_1 = -100
#     try:
#         valuebet_max_away_1 = max(melhores_odes2[melhores_odes2['DICA']==colunas_ods_1[0]]['valuebet'])
#     except:
#         valuebet_max_away_1 = -100
#     try:
#         valuebet_max_draw_1 = max(melhores_odes2[melhores_odes2['DICA']==colunas_ods_1[1]]['valuebet'])     
#     except:
#         valuebet_max_draw_1 = -100


#     melhor_valuebet = max(valuebet_max_home_1,valuebet_max_away_1,valuebet_max_draw_1,-99)
#     if valuebet_max_home_1 == melhor_valuebet:
#         odes_envio = odes_envio.append(melhores_odes2[melhores_odes2['DICA']==colunas_ods_1[2]],sort=True)
#         odes_nao_enviadas = odes_nao_enviadas.append(melhores_odes2[melhores_odes2['DICA']!=colunas_ods_1[2]],sort=True)
#     elif valuebet_max_away_1 == melhor_valuebet:
#         odes_envio = odes_envio.append(melhores_odes2[melhores_odes2['DICA']==colunas_ods_1[0]],sort=True)
#         odes_nao_enviadas = odes_nao_enviadas.append(melhores_odes2[melhores_odes2['DICA']!=colunas_ods_1[0]],sort=True)
#     elif valuebet_max_draw_1 == melhor_valuebet:
#         odes_envio = odes_envio.append(melhores_odes2[melhores_odes2['DICA']==colunas_ods_1[1]],sort=True)
#         odes_nao_enviadas = odes_nao_enviadas.append(melhores_odes2[melhores_odes2['DICA']!=colunas_ods_1[1]],sort=True)
#     else:
#         odes_nao_enviadas = odes_nao_enviadas.append(melhores_odes2,sort=True)        


#     #Trata _2    
#     col_hand = colunas_hand[1]
#     handicaps = melhores_odes[melhores_odes['DICA'].isin(colunas_ods_2)][col_hand].unique()
#     for h in handicaps:
#         melhores_odes2 = melhores_odes[melhores_odes[col_hand]==h]
#         melhores_odes2 = melhores_odes2[melhores_odes2['DICA'].isin(colunas_ods_2)]
#         try:
#             valuebet_max_home_2 = max(melhores_odes2[melhores_odes2['DICA']==colunas_ods_2[1]]['valuebet'])
#         except:
#             valuebet_max_home_2 = -100
#         try:
#             valuebet_max_away_2 = max(melhores_odes2[melhores_odes2['DICA']==colunas_ods_2[0]]['valuebet'])
#         except:
#             valuebet_max_away_2 = -100

#         melhor_valuebet_2 = max(valuebet_max_home_2,valuebet_max_away_2,-99)

#         if valuebet_max_home_2 == melhor_valuebet_2:
#             odes_envio = odes_envio.append(melhores_odes2[melhores_odes2['DICA']==colunas_ods_2[1]],sort=True)
#             odes_nao_enviadas = odes_nao_enviadas.append(melhores_odes2[melhores_odes2['DICA']!=colunas_ods_2[1]],sort=True)
#         elif valuebet_max_away_2 == melhor_valuebet_2:
#             odes_envio = odes_envio.append(melhores_odes2[melhores_odes2['DICA']==colunas_ods_2[0]],sort=True)
#             odes_nao_enviadas = odes_nao_enviadas.append(melhores_odes2[melhores_odes2['DICA']!=colunas_ods_2[0]],sort=True)
#         else:            
#             odes_nao_enviadas = odes_nao_enviadas.append(melhores_odes2,sort=True)           


#      #Trata _3    
#     col_hand = colunas_hand[2]
#     handicaps = melhores_odes[melhores_odes['DICA'].isin(colunas_ods_3)][col_hand].unique()
#     for h in handicaps:  
#         melhores_odes2 = melhores_odes[melhores_odes[col_hand]==h]
#         melhores_odes2 = melhores_odes2[melhores_odes2['DICA'].isin(colunas_ods_3)]
#         try:
#             valuebet_max_home = max(melhores_odes2[melhores_odes2['DICA']==colunas_ods_3[1]]['valuebet'])
#         except:
#             valuebet_max_home = -100
#         try:
#             valuebet_max_away = max(melhores_odes2[melhores_odes2['DICA']==colunas_ods_3[0]]['valuebet'])
#         except:
#             valuebet_max_away = -100

#         melhor_valuebet = max(valuebet_max_home,valuebet_max_away,-99)

#         if valuebet_max_home == melhor_valuebet:
#             odes_envio = odes_envio.append(melhores_odes2[melhores_odes2['DICA']==colunas_ods_3[1]],sort=True)
#             odes_nao_enviadas = odes_nao_enviadas.append(melhores_odes2[melhores_odes2['DICA']!=colunas_ods_3[1]],sort=True)
#         elif valuebet_max_away == melhor_valuebet:
#             odes_envio = odes_envio.append(melhores_odes2[melhores_odes2['DICA']==colunas_ods_3[0]],sort=True)
#             odes_nao_enviadas = odes_nao_enviadas.append(melhores_odes2[melhores_odes2['DICA']!=colunas_ods_3[0]],sort=True)
#         else:
#             odes_nao_enviadas = odes_nao_enviadas.append(melhores_odes2,sort=True)
#     odes_envio.drop_duplicates(inplace = True)
#     odes_nao_enviadas.drop_duplicates(inplace = True)
#     return odes_envio, odes_nao_enviadas

# # -*- coding: utf-8 -*-
# import pandas as pd
# import numpy as np
# import time
# # colunas_ods_total = [ 'end_1_away_od', 'end_1_draw_od', 'end_1_home_od', 'end_2_away_od', 'end_2_home_od', 'end_3_over_od', 'end_3_under_od']
# # colunas_DICAS = ['DICA','Timestamp','Timestamp_DICA','away_name','casa','end_1_away_od','end_1_draw_od','end_1_handicap','end_1_home_od','end_2_away_od','end_2_handicap','end_2_home_od','end_3_handicap','end_3_over_od','end_3_under_od','handicap_valor','home_name','id_jogo','league_name','numero_casas','odd_media','odd_melhor','prob','prob_media','prob_melhor','sport_id','ss', 'valuebet','bet365_id','esporte']
# from Dominios import colunas_ods_total, colunas_DICAS
# from Dominios import bet_token, BOT_API_TOKEN, colunas_API_ODES, colunas_base_odes, colunas_DICAS, colunas_hand, colunas_nao_nulas, colunas_ods_1, colunas_ods_1, colunas_ods_2, colunas_ods_3,colunas_ods_total ,ods_visitante ,jogos_colunas , colunas_API_ODES ,CONNECTION_STRING
# from Dominios import minimo_de_casas as minimo_de_casas_padrao
# from Dominios import baseline_valuebet as baseline_valuebet_padrao
# from Dominios import ode_maxima_aceitavel as ode_maxima_aceitavel_padrao
# from Dominios import casas_interesse as casas_interesse_padrao

# from APIDados import retorna_jogos, retorna_odd
# from SQLConexao import  retorna_base_sql_server, salva_sql_server
# from TratamentoDados import trata_odd,manipula_por_tipo,transforma_em_datetime_add, trata_jogos
# from TratamentoTexto import trata_nome_dica, trata_nome_esporte, trata_handcap, gera_mensagem_final,retorna_text_handicap, retorna_mensagem_handicap, retorna_nome_pontos
# # from APITelegram import retorna_id_chat, manda_mensagem_telegram
