import numpy as np
import pandas as pd
from datetime import date, timedelta, datetime
from S3Funcoes import s3_upload_csv, s3_read_csv, s3_list_files
import json
from lambda_Preenche_Historico_Placar import preenche_historico_placares
from Dominios import QUERY_POLITICA_DICAS




def extrai_tabelas_s3(tipo, range_tempo =10, dias_para_tras=3):
    """Sumario

    Parametros:
    tipo(str){'ODES','JOGOS','DICAS','APURACAO','APURACAO_MISSING','RESULTADO','DICAS_APOSTADAS'}: tipo de tabela que será consultada
    range_tempo(int): Janela de tempo da consulta
    Retorno:
    Base requisitada
    """
    colunas_apuracao = ['sport_id','id_jogo','casa','Handicap','Odd','Odd_media','Prob','Prob_media','valuebet','Num_casas','Tipo','DICA','away_name','home_name','league_name','Timestamp','id_esporte','home','away','ss','TIPO1','TIPO2','VALOR_ODE','VALOR_HANDICAP','Date','Sucesso','Odd_Apostada','Razao','Timestamp_Aposta','RESULTADO_CALCULADO','RESULTADO_APOSTADO']
    colunas_dicas=['sport_id','id_jogo','casa','Handicap','Odd','Odd_media','Prob','Prob_media','valuebet','Num_casas','Tipo','DICA','away_name','home_name','league_name','Timestamp']
    colunas_jogos=['away_cc','away_id','away_image_id','away_name','bet365_id','home_cc','home_id','home_image_id','home_name','id_jogo','league_cc','league_id','league_name','sport_id','ss','time','time_status','Timestamp']
    colunas_odes = ['Timestamp','casa','end_1_add_time','end_1_away_od','end_1_draw_od','end_1_home_od','end_1_id','end_1_ss','end_1_time_str','end_2_add_time','end_2_away_od','end_2_handicap','end_2_home_od','end_2_id','end_2_ss','end_2_time_str','end_3_add_time','end_3_handicap','end_3_id','end_3_over_od','end_3_ss','end_3_time_str','end_3_under_od','esporte','id_jogo','matching_dir','odds_update_1','odds_update_2','odds_update_3','DiaConsulta']
#     datas = [(date.today() - timedelta(days=tempo)).strftime('%Y%m%d') for tempo in range(200,300)]
    datas = [(date.today() - timedelta(days=tempo)).strftime('%Y%m%d') for tempo in range(dias_para_tras,dias_para_tras+range_tempo)]

    if tipo in ['ODES','JOGOS','DICAS','APURACAO']:
        if tipo == 'ODES' :
            colunas = colunas_odes
            NOME_PADRAO_PASTA = 's3://magic-bet-raw/Odes/'
            NOME_PADRA_ARQUIVO = 'BaseOdes_'
        elif tipo == 'JOGOS':
            colunas = colunas_jogos
            NOME_PADRAO_PASTA = 's3://magic-bet-raw/Jogos/'
            NOME_PADRA_ARQUIVO = 'BaseJogos_'
        elif tipo == 'DICAS':
            colunas = colunas_dicas
            NOME_PADRAO_PASTA = 's3://magic-bet-raw/DicasFull/'
            NOME_PADRA_ARQUIVO = 'BaseDicasFull_'
        elif tipo == 'APURACAO':
            colunas = colunas_apuracao
            NOME_PADRAO_PASTA = 's3://magic-bet-raw/Apuracao/'
            NOME_PADRA_ARQUIVO = 'BaseApuracao_'
        consulta_total = pd.DataFrame([],columns = colunas)

        for data in datas:
            ano = data[0:4]
            mes = data[4:6]
            dia = data[6:8]
            
            try:
                consulta = s3_read_csv(NOME_PADRAO_PASTA+'ano='+ano + '/mes='+mes + '/dia='+dia+'/', NOME_PADRA_ARQUIVO+ano +mes +dia + '.csv')
                consulta_total = consulta_total.append(consulta)
                print("Carregou tabela " + tipo + ' da data ' + data)
            except:
                print("Erro na leitura da tabela " + tipo + ' da data ' + data)
                pass
    elif tipo == 'RESULTADO':
        consulta_total = s3_read_csv('s3://magic-bet-raw/Resultados/','historico.csv')
        print("Carregou tabela " + tipo +" historico")
    elif tipo =='APURACAO_MISSING':
        consulta_total = s3_read_csv("s3://magic-bet-raw/ApuracaoMissing/","BaseApuracaoMissing.csv")
        print("Carregou tabela " + tipo +" historico")
            
    elif tipo == 'DICAS_APOSTADAS':
        NOME_PADRAO_PASTA = 's3://magic-bet-raw/DicasApostadas/'
        consulta_total = pd.DataFrame([])
        for data in datas:
            ano = data[0:4]
            mes = data[4:6]
            dia = data[6:8]
            enviadas  = s3_list_files('s3://magic-bet-raw/DicasApostadas/'+'ano='+ano + '/mes='+mes + '/dia='+dia+'/')
            for arquivo in enviadas:
                try:
                    consulta = s3_read_csv(NOME_PADRAO_PASTA+'ano='+ano + '/mes='+mes + '/dia='+dia+'/', arquivo + '.csv')
                    consulta_total = consulta_total.append(consulta)
                except:
                    print("Erro no "+tipo + ' da tabela na data ' + data + ' NO ARQUIVO '+ arquivo)
                    pass

    return consulta_total

def resultado_bruto(placar_casa,placar_visitante,tipo_aposta,aposta,odd,hancap=None):
    """Sumario

    Parametros:
    placar_casa(int): Placar do time da casa
    placar_visitante(int): Placar  do time visitante
    tipo_aposta(int){1,2,3}: tipo 1 (resultado simples), 2 (handicap) e 3 (total de gols)
    aposta(int){1,2,3}: 1 casa/over, 2 visitante/under, 3 empate
    odd (float): Valor da ode da aposta
    handcap (float): Caso seja de handcap, qual o seu valor
    Retorno:
    Resultado bruto financeiro das dicas
    """

    if tipo_aposta == 1:
        if aposta == 1:
            result = odd if placar_casa > placar_visitante else 0
        elif aposta == 2:
            result = odd if placar_casa < placar_visitante else 0
        else:
            result = odd if placar_casa == placar_visitante else 0
    
    elif tipo_aposta == 2 and hancap != None and (aposta == 1 or aposta == 2):

        if hancap % 0.5 == 0:
            if aposta == 1:
                result = odd if (placar_casa + hancap > placar_visitante) else 1 if (placar_casa + hancap == placar_visitante) else 0
            elif aposta == 2:
                result = odd if placar_casa + hancap < placar_visitante else 1 if placar_casa + hancap == placar_visitante else 0
        elif (((hancap % 1) % 0.5) == 0.25):
            if aposta == 1:
                result = odd if placar_casa + hancap > placar_visitante + 1 else (odd/2)+1 if placar_casa + hancap > placar_visitante + 0.5 else 1 if placar_casa + hancap > placar_visitante else 0
            elif aposta == 2:
                result = odd if placar_casa + hancap < placar_visitante - 0.5 else (odd/2) + 1 if placar_casa + hancap < placar_visitante else 1 if placar_casa + hancap < placar_visitante + 0.5 else 0
        else:
            result = None

            
    elif tipo_aposta == 3 and hancap != None and (aposta == 1 or aposta == 2):
        if hancap % 0.5 == 0:
            if aposta == 1:
                result = odd if placar_casa + placar_visitante > hancap else 1 if placar_casa + placar_visitante == hancap else 0
            elif aposta == 2:
                result = odd if placar_casa + placar_visitante < hancap else 1 if placar_casa + placar_visitante == hancap else 0
        elif (((hancap % 1) % 0.5) == 0.25):
            if aposta == 1:
                result = odd if placar_casa + placar_visitante > hancap + 0.5 else ((odd/2)+1) if placar_casa + placar_visitante > hancap else 1 if placar_casa + placar_visitante > hancap - 0.5 else 0
            elif aposta == 2:
                result = odd if placar_casa + placar_visitante < hancap - 0.5 else ((odd/2)+1) if placar_casa + placar_visitante < hancap else 1 if placar_casa + placar_visitante < hancap + 0.5 else 0
        else:
            result = None
    else:
        result = None

    if result != None:
        result = result - 1 #para visao de resultados é se ele apostou e perdeu o resultado é negativo, não zero
    return result  

# def retorna_base_resultados_lista(jogos):
#     df_resultado = pd.DataFrame()
#     bet_token = '57659-nlPvoqXEFejq5s'
#     for jogo in jogos:
#         api_resultado = requests.get('https://api.betsapi.com/v1/event/view?token=' + bet_token + '&event_id=' + str(jogo))
#         api_resultado_json = json.loads(api_resultado.content.decode('utf-8'))
#         try:
#             ss = api_resultado_json['results'][0]['ss']
#         except:
#             ss = None
#         if ss ==None:
#             placar = ['-1', '-1']
#         else:
#             placar = ss.split('-')
#         # if placar == ['']:
#         #     print('quebrado')
#         #     placar = ['-1', '-1']
#         # print(placar)
#         try:
#             objeto = {
#                   'id_jogo':jogo,
#                   'home':placar[0],
#                   'away':placar[1],
#                     'ss' :ss}
#         except:
#             objeto = {
#                   'id_jogo':jogo,
#                   'home':'-1',
#                   'away':'-1',
#                     'ss' :ss}            
#         df_resultado = df_resultado.append(pd.DataFrame(objeto,index=[0]))
#     return df_resultado

# range_tempo_consulta = 100
# Cria gera_resultados_sql no s3
def layouta_dicas_para_apuracao(dicas2):
    """Sumario

    Parametros:
    dicas2(pandas DataFrame): Tabela com tipo de DICA e Ode
    Retorno:
    Tabela enriquecida com colunas para Apuracao
    """
    tipos_de_dicas = [ '1_home','1_away', '1_draw', '2_home','2_away', '3_over', '3_under']
    dicas2_1_1= dicas2[dicas2['DICA'] == tipos_de_dicas[0]]
    dicas2_1_2= dicas2[dicas2['DICA'] == tipos_de_dicas[1]]
    dicas2_1_3= dicas2[dicas2['DICA'] == tipos_de_dicas[2]]
    dicas2_2_1= dicas2[dicas2['DICA'] == tipos_de_dicas[3]]
    dicas2_2_2= dicas2[dicas2['DICA'] == tipos_de_dicas[4]]
    dicas2_3_1= dicas2[dicas2['DICA'] == tipos_de_dicas[5]]
    dicas2_3_2= dicas2[dicas2['DICA'] == tipos_de_dicas[6]]

    print(dicas2_1_1.shape[0]+dicas2_1_2.shape[0]+dicas2_1_3.shape[0]+dicas2_2_1.shape[0]+dicas2_2_2.shape[0]+dicas2_3_1.shape[0]+dicas2_3_2.shape[0])

    # tipo 1 :(resultado simples), 2 (handicap) e 3 (total de gols)
    # tipo2: 1 casa/over, 2 visitante/under, 3 empate
    if dicas2_1_1.shape[0] >0:
        dicas2_1_1.loc[:, 'TIPO1'] = 1
        dicas2_1_1.loc[:, 'TIPO2'] = 1
        dicas2_1_1.loc[:, 'VALOR_ODE'] = dicas2_1_1['Odd']
        dicas2_1_1.loc[:, 'VALOR_HANDICAP'] = 0.
    if dicas2_1_2.shape[0] >0:
        dicas2_1_2.loc[:, 'TIPO1'] = 1
        dicas2_1_2.loc[:, 'TIPO2'] = 2
        dicas2_1_2.loc[:, 'VALOR_ODE'] = dicas2_1_2['Odd']
        dicas2_1_2.loc[:, 'VALOR_HANDICAP'] = 0.
    if dicas2_1_3.shape[0] >0:
        dicas2_1_3.loc[:, 'TIPO1'] = 1
        dicas2_1_3.loc[:, 'TIPO2'] = 3
        dicas2_1_3.loc[:, 'VALOR_ODE'] = dicas2_1_3['Odd']
        dicas2_1_3.loc[:, 'VALOR_HANDICAP'] = 0.
    if dicas2_2_1.shape[0] >0:
        dicas2_2_1.loc[:, 'TIPO1'] = 2
        dicas2_2_1.loc[:, 'TIPO2'] = 1
        dicas2_2_1.loc[:, 'VALOR_ODE'] = dicas2_2_1['Odd']
        dicas2_2_1.loc[:, 'VALOR_HANDICAP'] = dicas2_2_1['Handicap']
    if dicas2_2_2.shape[0] >0:
        dicas2_2_2.loc[:, 'TIPO1'] = 2
        dicas2_2_2.loc[:, 'TIPO2'] = 2
        dicas2_2_2.loc[:, 'VALOR_ODE'] = dicas2_2_2['Odd']
        dicas2_2_2.loc[:, 'VALOR_HANDICAP'] = dicas2_2_2['Handicap']
    if dicas2_3_1.shape[0] >0:
        dicas2_3_1.loc[:, 'TIPO1'] = 3
        dicas2_3_1.loc[:, 'TIPO2'] = 1
        dicas2_3_1.loc[:, 'VALOR_ODE'] = dicas2_3_1['Odd']
        dicas2_3_1.loc[:, 'VALOR_HANDICAP'] = dicas2_3_1['Handicap']
    if dicas2_3_2.shape[0] >0:
        dicas2_3_2.loc[:, 'TIPO1'] = 3
        dicas2_3_2.loc[:, 'TIPO2'] = 2
        dicas2_3_2.loc[:, 'VALOR_ODE'] = dicas2_3_2['Odd']
        dicas2_3_2.loc[:, 'VALOR_HANDICAP'] = dicas2_3_2['Handicap']

    dicas3 = dicas2_1_1.append(dicas2_1_2.append(dicas2_1_3.append(dicas2_2_1.append(dicas2_2_2.append(dicas2_3_1.append(dicas2_3_2))))))
    return dicas3

def enriquece_dicas_apostadas(dicas3, DICAS_APOSTADAS):
    try:
        DICAS_APOSTADAS['Timestamp_Aposta'] = pd.to_datetime(DICAS_APOSTADAS['Timestamp_Aposta']) 
        DICAS_APOSTADAS['DICA'] = ['1_home' if x =='Time da Casa' else '1_away' if x == 'Visitante' else '' for x in DICAS_APOSTADAS['Dica']]
        DICAS_APOSTADAS = DICAS_APOSTADAS.sort_values(['Timestamp_Aposta','id_jogo'], ascending = False).drop_duplicates(['id_jogo','DICA'])
        dicas4 = pd.merge(dicas3,DICAS_APOSTADAS[['id_jogo', 'Sucesso', 'Odd_Apostada', 'Razao','Timestamp_Aposta','DICA']], on = ['id_jogo','DICA'], how = 'left')
    except:
        dicas4=dicas3.copy()
        dicas4['Sucesso']='false'
        dicas4['Odd_Apostada']=0.0
        dicas4['Razao']='Não consta na tabela de Apostas Realizadas'
        dicas4['Timestamp_Aposta']=0
    return dicas4

# range_tempo_consulta = 100
# Cria gera_resultados_sql no s3
def main(event, context):
    range_tempo_consulta = 20
    dias_para_tras=5
    preenche_historico_placares(delta_dias = range_tempo_consulta, tipo =1, dias_para_tras = dias_para_tras)

    HOJE_TEXTO = datetime.now().strftime("%Y%m%d")
    ano = HOJE_TEXTO[0:4]
    mes = HOJE_TEXTO[4:6]
    dia = HOJE_TEXTO[6:8]
    # jogos_base = extrai_tabelas_s3('JOGOS', range_tempo =range_tempo_consulta)
    # odes = extrai_tabelas_s3('ODES', range_tempo =range_tempo_consulta)
    dicas = extrai_tabelas_s3('DICAS', range_tempo =range_tempo_consulta, dias_para_tras = dias_para_tras)
    resultado = extrai_tabelas_s3('RESULTADO', range_tempo =range_tempo_consulta)

    DICAS_JA_APURADAS = extrai_tabelas_s3('APURACAO', range_tempo= int(1.25*range_tempo_consulta), dias_para_tras = dias_para_tras)
    DICAS_APOSTADAS = extrai_tabelas_s3('DICAS_APOSTADAS', range_tempo =range_tempo_consulta, dias_para_tras = dias_para_tras)
    try:
        DICAS_JA_APURADAS_MISSING = extrai_tabelas_s3('APURACAO_MISSING', range_tempo= 1)
    except:
        pass
    print("Acabei de ler " + str(dicas.shape[0] )+ " linhas da tabela DICAS" )
    print("Acabei de ler " + str(resultado.shape[0] )+ " linhas da tabela RESULTADOS" )
    print("Acabei de ler " + str(DICAS_APOSTADAS.shape[0] )+ " linhas da tabela DICAS_APOSTADAS" )
    print("Acabei de ler " + str(DICAS_JA_APURADAS.shape[0] )+ " linhas da tabela APURACAO" )

    dicas=dicas.query(QUERY_POLITICA_DICAS)
    dicas = dicas.replace([np.inf, -np.inf], np.nan)
    dicas = dicas[~dicas['valuebet'].isnull()]
    dicas['Num_casas'] = pd.to_numeric(dicas['Num_casas'], errors = 'coerce')
    dicas['valuebet'] = pd.to_numeric(dicas['valuebet'], errors = 'coerce')
    dicas = dicas[~dicas['league_name'].str.contains("Ebasketball", na=False)]
    dicas = dicas[~dicas['league_name'].str.contains("Esoccer", na=False)]
    dicas = dicas[ dicas['Num_casas'] > 5]
    dicas[ [ 'id_esporte']] = dicas[ ['sport_id']] 
    dicas = dicas[dicas['sport_id'].isin([1,18])]
    dicas['Date'] = dicas.Timestamp.str[:4] + dicas.Timestamp.str[5:7]+dicas.Timestamp.str[8:11]
    dicas['Timestamp'] = pd.to_datetime(dicas['Timestamp']) 
    dicas = dicas.sort_values(['Timestamp','id_jogo'], ascending = False).drop_duplicates(['id_jogo','casa','DICA'])



    #Puxa Resultados
    resultado = resultado[resultado['home']!='-1']
    resultado = resultado[~resultado['home'].astype(str).str.contains('-')]
    resultado[['id_jogo', 'home', 'away']]  =resultado[['id_jogo', 'home', 'away']].astype(float).astype(int)
    dx = resultado.drop_duplicates().groupby(['id_jogo']).count()
    blacklist = dx[dx['home']>1].reset_index().id_jogo.values
    resultado = resultado[~resultado['id_jogo'].isin(blacklist)]
    resultado = resultado.drop(['id_esporte'],axis =1)
    resultado=resultado[np.logical_and(resultado['home']!=-1,~resultado['home'].isnull() )].drop_duplicates()
    dicas2 = pd.merge(dicas,resultado, how = 'left' ,on = ['id_jogo']).drop_duplicates()

    for i in ['home','away']:
        dicas2[i] = dicas2[i].replace([np.inf, -np.inf], np.nan)
        dicas2[i] = dicas2[i].fillna(-1)
        dicas2[i] = pd.to_numeric(dicas2[i], errors = 'coerce').astype(int)


    dicas2=  enriquece_dicas_apostadas(layouta_dicas_para_apuracao(dicas2), DICAS_APOSTADAS)#cria colunas x['TIPO1'], x['TIPO2'], x['VALOR_ODE'], x['VALOR_HANDICAP'])
    # calcula resultado das apostas para o esperado e para o realizado
    dicas2['RESULTADO_CALCULADO'] = dicas2.apply(lambda x: resultado_bruto(x['home'], x['away'], x['TIPO1'], x['TIPO2'], x['VALOR_ODE'], x['VALOR_HANDICAP']), axis=1)
    dicas2['RESULTADO_APOSTADO']  = dicas2.apply(lambda x: resultado_bruto(x['home'], x['away'], x['TIPO1'], x['TIPO2'], x['Odd_Apostada'], x['VALOR_HANDICAP']), axis=1)
    dicas2.loc[dicas2['Odd_Apostada']==0,'RESULTADO_APOSTADO'] = 0
    dicas2.loc[dicas2['home']==-1,'RESULTADO_APOSTADO'] = -1
    dicas2.loc[dicas2['away']==-1,'RESULTADO_APOSTADO'] = -1
    dicas2.loc[dicas2['home']==-1,'RESULTADO_CALCULADO'] = -1
    dicas2.loc[dicas2['away']==-1,'RESULTADO_CALCULADO'] = -1
    dicas2.loc[dicas2['Sucesso'].isnull(), ['RESULTADO_APOSTADO']]=0
    # se nao tiver resultado no sucesso, o resultado apostado é zero

    # Retira as apuradas em arquivos anteriores
    DICAS_JA_APURADAS['flag_ja_apurado'] = 1
    DICAS_JA_APURADAS['Timestamp_Aposta']= pd.to_datetime(DICAS_JA_APURADAS['Timestamp_Aposta'],errors = 'coerce') 
    DICAS_JA_APURADAS = DICAS_JA_APURADAS.sort_values(['Timestamp_Aposta','id_jogo'], ascending = False).drop_duplicates(['id_jogo','DICA'])
    dicas3 = pd.merge(dicas2,DICAS_JA_APURADAS[['id_jogo','sport_id' ,'flag_ja_apurado','DICA']], on = ['id_jogo','sport_id','DICA'], how = 'left')
    dicas5 = dicas3[dicas3['flag_ja_apurado']!=1].drop('flag_ja_apurado', axis =1)

    #Ajusta placar inverso para NBA e WNBA
    dicas5_nba = dicas5[(dicas5['league_name'].str.contains("NBA", na=False) )| (dicas5['league_name'].str.contains("NCAAB", na=False))]
    dicas5_s_nba= dicas5[(~dicas5['league_name'].str.contains("NBA", na=False) )& (~dicas5['league_name'].str.contains("NCAAB", na=False))]
    dicas5_nba_pos=dicas5_nba[dicas5_nba['RESULTADO_CALCULADO']>0]
    dicas5_nba_neg=dicas5_nba[dicas5_nba['RESULTADO_CALCULADO']<=0]
    dicas5_nba_pos['RESULTADO_CALCULADO'] = -1
    dicas5_nba_neg['RESULTADO_CALCULADO'] = dicas5_nba_neg['VALOR_ODE']-1
    dicas5_ajustado = dicas5_nba_pos.append(dicas5_nba_neg).append(dicas5_s_nba).reset_index(drop = True)

    print("Estava com " + str(dicas3.shape[0] )+ "linhas de dicas apuradas no total" )
    print("Ficou com " + str(dicas5_ajustado.shape[0] )+ "linhas de dicas apuradas retirando as que ja estao na aws" )

    #reinclui as do proprio dia, para empilhar e salvar arquivo unico
    try:
        dicas_ja_apuradas_hoje = s3_read_csv('s3://magic-bet-raw/Apuracao/'+'ano='+ano + '/mes='+mes + '/dia='+dia+'/', 'BaseApuracao_'+ano +mes +dia + '.csv')
        dicas6 = dicas_ja_apuradas_hoje.append(dicas5_ajustado).drop_duplicates(['id_jogo','DICA']).reset_index(drop = True)
    except:
        dicas6 = dicas5_ajustado.copy()

    output_apuracao = dicas6[dicas6['home']!=-1]
    output_apuracao=output_apuracao[['sport_id', 'id_jogo', 'casa', 'Handicap', 'Odd', 'Odd_media', 'Prob',
       'Prob_media', 'valuebet', 'Num_casas', 'Tipo', 'DICA', 'away_name',
       'home_name', 'league_name', 'Timestamp', 'id_esporte', 'home',
       'away', 'ss', 'TIPO1', 'TIPO2', 'VALOR_ODE', 'VALOR_HANDICAP','Date', 
       'Sucesso', 'Odd_Apostada', 'Razao', 'Timestamp_Aposta',
       'RESULTADO_CALCULADO', 'RESULTADO_APOSTADO']]
    try:
        output_apuracao_missing = DICAS_JA_APURADAS_MISSING.append(dicas6[np.logical_or(dicas6['home']==-1,dicas6['home'].isnull())]).drop_duplicates(['id_jogo','DICA'])
        output_apuracao_missing  = pd.merge(output_apuracao_missing, dicas6[dicas6['home']!=-1].drop_duplicates(['id_jogo','DICA'])[['id_jogo','DICA','RESULTADO_CALCULADO']], on = ['id_jogo','DICA'], how = 'left', suffixes=['','_novo'])
        output_apuracao_missing = output_apuracao_missing[output_apuracao_missing['RESULTADO_CALCULADO_novo'].isnull()].drop(['RESULTADO_CALCULADO_novo'], axis = 1)
        output_apuracao_missing = output_apuracao_missing.drop_duplicates(['id_jogo','DICA'])
    except:
        output_apuracao_missing = dicas6[dicas6['home']==-1]

    print("Ficou com " + str(output_apuracao.shape[0] )+ "linhas de dicas apuradas reincluindo as que estao no msm arquivo que hj" )
    arquivo_output = "s3://magic-bet-raw/Apuracao/"+"ano="+ano + "/mes="+mes + "/dia="+dia+"/"+"BaseApuracao_"+ano +mes +dia + ".csv"
    arquivo_output_Missing = "s3://magic-bet-raw/ApuracaoMissing/BaseApuracaoMissing.csv"

    s3_upload_csv(output_apuracao, arquivo_output,'')
    s3_upload_csv(output_apuracao_missing, arquivo_output_Missing,'')

    return {
        'statusCode': 200,
        'body': json.dumps('Apurei mais  '+str(output_apuracao.shape[0] ) + ' resultados salvos no dia de hoje, e ' +str(output_apuracao_missing.shape[0] ) + ' missings' )
    }

if __name__ == "__main__":   
    main('', '')
