import json
import numpy as np
import pandas as pd
# from time import sleep
from datetime import date, timedelta
from TratamentoDados import trata_placar_lista
from S3Funcoes import s3_read_csv, atualiza_bucket_s3
# PACOTES
from Dominios import path_s3_historico, file_s3_historico_name
def preenche_historico_placares(delta_dias = 7, tipo =1, dias_para_tras = 3):
    HISTORICO_PLACARES = s3_read_csv(path_s3_historico, file_s3_historico_name)
    HISTORICO_PLACARES=HISTORICO_PLACARES[HISTORICO_PLACARES['home']!=-1]    
    HISTORICO_PLACARES=HISTORICO_PLACARES[HISTORICO_PLACARES['home']!='-1'].reset_index(drop=True)    
    
    lista_datas = [(date.today() - timedelta(days=i)).strftime('%Y%m%d') for i in range(dias_para_tras,dias_para_tras+delta_dias)] #busca um mes pra tras
    df_jogos_full = pd.DataFrame([])
    for DATA_TEXTO in lista_datas:
        ano= DATA_TEXTO[0:4]
        mes= DATA_TEXTO[4:6]
        dia= DATA_TEXTO[6:8]
        try:
            df_jogos_full = df_jogos_full.append(s3_read_csv('s3://magic-bet-raw/Jogos/'+'ano='+ano + '/mes='+mes + '/dia='+dia+'/', 'BaseJogos_'+ano +mes +dia + '.csv'))
        except:
            pass
    df_jogos_full = df_jogos_full[df_jogos_full['sport_id']==18]
    df_jogos_full = df_jogos_full[~df_jogos_full['league_name'].str.contains("Ebasketball")]
    df_jogos_full = df_jogos_full[~df_jogos_full['league_name'].str.contains("Esoccer")]

    ids_missing = [i for i in df_jogos_full.id_jogo if i not in HISTORICO_PLACARES.id_jogo.values]
    ids_missing = list(set(ids_missing))
    qtd_split = 1+int(len(ids_missing)/2000)
    lista_bases = np.array_split(pd.DataFrame(ids_missing,columns=['ids_missing']).sort_values('ids_missing', ascending = False).reset_index(drop=True), qtd_split)

    if tipo ==1 :
        dfx = lista_bases[0]
        consulta_retorno = trata_placar_lista(dfx.ids_missing) 
        atualiza_bucket_s3(consulta_retorno, path_s3_historico, file_s3_historico_name) 
    elif tipo ==2:
        for i,dfx in enumerate(lista_bases):
            print("Estou comecando o arquivo " + str(i))
            consulta_retorno = trata_placar_lista(dfx.ids_missing)  
            atualiza_bucket_s3(consulta_retorno, path_s3_historico, file_s3_historico_name)
            # sleep(60*5)  # deixar programado para rodar tipo 2:55 para começar o looping seguinte na proxima hora
    return consulta_retorno


def main(event, context):
    consulta_retorno = preenche_historico_placares(delta_dias = 3, tipo = 1 , dias_para_tras = 0)
    return {
        'statusCode': 200,
        'body': json.dumps('Peguei mais  '+str(consulta_retorno.shape[0] ) + ' novos Placares')
    }
if __name__ == "__main__":   
    main('', '')
    
