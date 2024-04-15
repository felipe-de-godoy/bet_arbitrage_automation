
import pandas as pd
from S3Funcoes import s3_upload_csv, s3_read_csv,s3_list_files
from Dominios import colunas_DICAS
from datetime import date, timedelta, datetime
HOJE_TEXTO = datetime.now().strftime("%Y%m%d")
ano = HOJE_TEXTO[0:4]
mes = HOJE_TEXTO[4:6]
dia = HOJE_TEXTO[6:8]
ONTEM_TEXTO = (date.today() - timedelta(days=1)).strftime('%Y%m%d')
ano_ontem = ONTEM_TEXTO[0:4]
mes_ontem = ONTEM_TEXTO[4:6]
dia_ontem = ONTEM_TEXTO[6:8]
amanha_TEXTO = (date.today() + timedelta(days=1)).strftime('%Y%m%d')
ano_amanha = amanha_TEXTO[0:4]
mes_amanha = amanha_TEXTO[4:6]
dia_amanha = amanha_TEXTO[6:8]

def armazena_bases_dicasfull_s3( base_dicas, id_cenario ='0',  tipo_processamento = 1, tipo_salvamento = 1, caminho_resultado = '' ):
    """""Sumario

    Parametros:
    base_dicas(pandas DataFrame): base de dicas consultados
    id_cenario (string) : id do cenario para rastreio posterior
    tipo_processamento (int) : tipo 1 é o processamento normal e o resto é simulação
    tipo_salvamento (int) default ': se é pra salvar local 2 ou no sql 1
    caminho_resultado (string): se for para salvar local, inputar o caminho
    Retorno:
    Guarda bases de DicasFull no banco S3
    """

    print('tamanho base de dicas')
    print(base_dicas.shape)
    if tipo_processamento == 1:
        print('TB_DICAS_ENVIADAS')
        # dicas_envio_full = base_dicas.query('(casa == "BetVictor" & Odd>=3 & Odd<5 & valuebet >= 3  & sport_id == 18)')
        if base_dicas.shape[0]>0:
            try:
                df_antigo = s3_read_csv('s3://magic-bet-raw/DicasFull/'+'ano='+ano + '/mes='+mes + '/dia='+dia+'/', 'BaseDicasFull_'+ano +mes +dia + '.csv')
                s3_upload_csv(base_dicas.append(df_antigo), 's3://magic-bet-raw/DicasFull/'+'ano='+ano + '/mes='+mes + '/dia='+dia+'/', 'BaseDicasFull_'+ano +mes +dia + '.csv')
            except:
                s3_upload_csv(base_dicas, 's3://magic-bet-raw/DicasFull/'+'ano='+ano + '/mes='+mes + '/dia='+dia+'/', 'BaseDicasFull_'+ano +mes +dia + '.csv')

    else:
        print('TB_DICAS_ENVIADAS')
        base_dicas['id_cenario'] = id_cenario
        if tipo_salvamento == 1:
            s3_upload_csv(base_dicas[colunas_DICAS+['id_cenario']], 's3://magic-bet-raw/DicasSimulacoes/'+'ano='+ano + '/mes='+mes + '/dia='+dia+'/', 'BaseSimulacao_'+ano +mes +dia + '.csv')
        else:
            base_dicas.to_csv(caminho_resultado, index=False)



def armazena_bases_jogos_s3(jogos_total_consulta,   tipo_processamento = 1):
    """""Sumario

    Parametros:
    jogos_total_consulta (pandas DataFrame) : base de jogos consultados
    tipo_processamento (int) default = 1  : tipo 1 é o processamento normal e o resto é simulação

    Retorno:
    Guarda Jogos no banco S3
    """
    print('tamanho base de jogos')
    print(jogos_total_consulta.shape)
    # print(odes_nao_enviadas_total.shape)
    # Converte as bases para string

    # FIZ DE MANEIRA QUE AS TABELAS jogos_antigos0 E odes_antigos0 SAO  A BASE DO DIA, DE MANEIRA QUE NAO DUPLIQUE DADO
    if tipo_processamento == 1:
        jogos_total_consulta[['id_jogo', 'sport_id']] = jogos_total_consulta[['id_jogo', 'sport_id']].astype(str)
        print('TB_JOGOS')
        try:
            jogos_antigos1 = s3_read_csv('s3://magic-bet-raw/Jogos/'+'ano='+ano_ontem + '/mes='+mes_ontem + '/dia='+dia_ontem+'/', 'BaseJogos_'+ano_ontem +mes_ontem +dia_ontem + '.csv')
            jogos_antigos0 = s3_read_csv('s3://magic-bet-raw/Jogos/'+'ano='+ano + '/mes='+mes + '/dia='+dia+'/', 'BaseJogos_'+ano +mes +dia + '.csv')
            jogos_antigos = jogos_antigos1.append(jogos_antigos0)
        except:
            try:
                jogos_antigos0 = s3_read_csv('s3://magic-bet-raw/Jogos/'+'ano='+ano + '/mes='+mes + '/dia='+dia+'/', 'BaseJogos_'+ano +mes +dia + '.csv')
                jogos_antigos = jogos_antigos0.copy()
            except:
                try:
                    jogos_antigos0 = s3_read_csv('s3://magic-bet-raw/Jogos/'+'ano='+ano_ontem + '/mes='+mes_ontem + '/dia='+dia_ontem+'/', 'BaseJogos_'+ano_ontem +mes_ontem +dia_ontem + '.csv')
                    jogos_antigos = jogos_antigos0.copy()
                    jogos_antigos0 =jogos_antigos0.head(0)
                except:
                    jogos_antigos0 = s3_read_csv('s3://magic-bet-raw/Jogos/'+'ano='+'2021' + '/mes='+'07' + '/dia='+'26'+'/', 'BaseJogos_'+'20210726' + '.csv')
                    jogos_antigos = jogos_antigos0.copy()
                    jogos_antigos0 =jogos_antigos0.head(0)
        # Bate e filtra as que nao tinham na base
        jogos_antigos['flag_antigo'] = 1
        jogos_total_consulta[['id_jogo','sport_id']]=jogos_total_consulta[['id_jogo','sport_id']].astype(int)
        jogos_total_consulta2 = pd.merge(jogos_total_consulta, jogos_antigos[['id_jogo','sport_id','flag_antigo']], on=['id_jogo', 'sport_id'], how='left')
        jogos_total_consulta2 = jogos_total_consulta2[jogos_total_consulta2['flag_antigo'].isnull()].drop(['flag_antigo'], axis=1)
        jogos_upload = jogos_antigos0.append(jogos_total_consulta2)
        # Salva bases filtradas exceto de dicas
        if jogos_total_consulta2.shape[0]>0:
            s3_upload_csv(  jogos_upload,'s3://magic-bet-raw/Jogos/'+'ano='+ano + '/mes='+mes + '/dia='+dia+'/', 'BaseJogos_'+ano +mes +dia + '.csv')
       

def armazena_bases_odes_s3(odds_total_consulta,  tipo_processamento = 1):
    """""Sumario

    Parametros:
    odds_total_consulta (pandas DataFrame) : base de odes consultados
    tipo_processamento (int) default = 1  : tipo 1 é o processamento normal e o resto é simulação
    Retorno:
    Guarda Odes no banco S3
    """
    print('tamanho base de odes')
    print(odds_total_consulta.shape)
    if tipo_processamento == 1:
        print('TB_ODES')
        colunas_base_odes = ['Timestamp', 'casa','end_1_add_time', 'end_1_away_od',       'end_1_draw_od', 'end_1_home_od', 'end_1_id', 'end_1_ss',       'end_1_time_str', 'end_2_add_time', 'end_2_away_od',       'end_2_handicap', 'end_2_home_od', 'end_2_id', 'end_2_ss',       'end_2_time_str', 'end_3_add_time', 'end_3_handicap', 'end_3_id',      'end_3_over_od', 'end_3_ss', 'end_3_time_str', 'end_3_under_od',       'esporte', 'id_jogo','matching_dir', 'odds_update_1','odds_update_2', 'odds_update_3','DiaConsulta']
        colunas_dup_odes = ['id_jogo', 'esporte', 'casa', 'end_1_away_od', 'end_1_draw_od', 'end_1_home_od',                        'end_2_away_od', 'end_2_handicap', 'end_2_home_od', 'end_3_handicap', 'end_3_over_od', 'end_3_under_od']
        odds_total_consulta[colunas_dup_odes] = odds_total_consulta[colunas_dup_odes].astype(str)
        try:    
            odes_antigos1 = s3_read_csv('s3://magic-bet-raw/Odes/'+'ano='+ano_ontem + '/mes='+mes_ontem + '/dia='+dia_ontem+'/', 'BaseOdes_'+ano_ontem +mes_ontem +dia_ontem + '.csv')
            odes_antigos0 = s3_read_csv('s3://magic-bet-raw/Odes/'+'ano='+ano + '/mes='+mes + '/dia='+dia+'/', 'BaseOdes_'+ano +mes +dia + '.csv')
            odes_antigos = odes_antigos0.append(odes_antigos1)
        except:
            try:
                odes_antigos0 = s3_read_csv('s3://magic-bet-raw/Odes/'+'ano='+ano + '/mes='+mes + '/dia='+dia+'/', 'BaseOdes_'+ano +mes +dia + '.csv')
                odes_antigos = odes_antigos0.copy()
            except:
                try:
                    odes_antigos0 = s3_read_csv('s3://magic-bet-raw/Odes/'+'ano='+ano_ontem + '/mes='+mes_ontem + '/dia='+dia_ontem+'/', 'BaseOdes_'+ano_ontem +mes_ontem +dia_ontem + '.csv')
                    odes_antigos = odes_antigos0.copy()
                    odes_antigos0 =odes_antigos0.head(0)
                except:
                    odes_antigos0 = s3_read_csv('s3://magic-bet-raw/Odes/'+'ano='+'2021' + '/mes='+'07' + '/dia='+'26'+'/', 'BaseOdes_'+'20210726' + '.csv')
                    odes_antigos = odes_antigos0.copy()
                    odes_antigos0 =odes_antigos0.head(0)
        odes_antigos['flag_antigo'] = 1
        odds_total_consulta[['id_jogo','esporte']] =odds_total_consulta[['id_jogo','esporte']].astype(int)
        odds_total_consulta2 = pd.merge(odds_total_consulta, odes_antigos[['id_jogo', 'esporte', 'casa','flag_antigo']], on=['id_jogo', 'esporte', 'casa'], how='left')
        odds_total_consulta2 = odds_total_consulta2[odds_total_consulta2['flag_antigo'].isnull()].drop(['flag_antigo'], axis=1)
        odes_upload = odes_antigos0.append(odds_total_consulta2)
        odes_upload['DiaConsulta'] = datetime.now().strftime("%Y%m%d")
        if odds_total_consulta2.shape[0]>0:
            s3_upload_csv( odes_upload[colunas_base_odes],'s3://magic-bet-raw/Odes/'+'ano='+ano + '/mes='+mes + '/dia='+dia+'/', 'BaseOdes_'+ano +mes +dia + '.csv')
    else:
        pass

def consulta_s3_dicas():
    """""
    Retorno:
    Retorna as dicas dos ultimos dias
    """
    print("Batendo com dicas" + ano +mes +dia)
    print("Batendo com dicas" + ano_ontem +mes_ontem +dia_ontem )
    print("Batendo com dicas" + ano_amanha +mes_amanha +dia_amanha)
    try:
        mensagens_enviadas_hist0 = s3_read_csv('s3://magic-bet-raw/DicasFull/'+'ano='+ano_ontem + '/mes='+mes_ontem + '/dia='+dia_ontem+'/', 'BaseDicasFull_'+ano_ontem +mes_ontem +dia_ontem + '.csv')
        mensagens_enviadas_hist1 = s3_read_csv('s3://magic-bet-raw/DicasFull/'+'ano='+ano + '/mes='+mes + '/dia='+dia+'/', 'BaseDicasFull_'+ano +mes +dia + '.csv')
        mensagens_enviadas_hist2 = mensagens_enviadas_hist0.append(mensagens_enviadas_hist1)
        try:
            mensagens_enviadas_hist3 = s3_read_csv('s3://magic-bet-raw/DicasFull/'+'ano='+ano_amanha + '/mes='+mes_amanha + '/dia='+dia_amanha+'/', 'BaseDicasFull_'+ano_amanha +mes_amanha +dia_amanha + '.csv')
            mensagens_enviadas_hist2 = mensagens_enviadas_hist2.append(mensagens_enviadas_hist3)
        except:
            pass
    except:
        try:
            mensagens_enviadas_hist2 = s3_read_csv('s3://magic-bet-raw/DicasFull/'+'ano='+ano + '/mes='+mes + '/dia='+dia+'/', 'BaseDicasFull_'+ano +mes +dia + '.csv')
        except:
            try:
                mensagens_enviadas_hist2 = s3_read_csv('s3://magic-bet-raw/DicasFull/'+'ano='+ano_ontem + '/mes='+mes_ontem + '/dia='+dia_ontem+'/', 'BaseDicasFull_'+ano_ontem +mes_ontem +dia_ontem + '.csv')
            except:
                mensagens_enviadas_hist2 = s3_read_csv('s3://magic-bet-raw/DicasFull/'+'ano='+'2021' + '/mes='+'07' + '/dia='+'25'+'/', 'BaseDicasFull_'+'20210725' + '.csv')
    return mensagens_enviadas_hist2


def manda_dica_para_s3(dicas_envio):
    """""Sumario

    Parametros:
    dicas_envio (pandas DataFrame) : base de novas dicas a serem armazenadas
    Retorno:
    Disponibiliza essa dica a parte para que o robo apostador capture
    """
    # enviadas  = s3_list_files('s3://magicbetbucketteste/DicasEnviadas/')
    enviadas  = s3_list_files('s3://magic-bet-raw/DicasCalculadas/'+'ano='+ano + '/mes='+mes + '/dia='+dia+'/')
    ultimo_id = max([int(i) for i in enviadas]+[0])
    dicas_envio = dicas_envio.drop_duplicates(['DICA','id_jogo','casa'])
    # dicas_envio = dicas_envio.query('(casa == "Bet365" & Odd>=2 & valuebet >= 3  & sport_id == 1)    |(casa == "BetVictor" & Odd>=2 & Odd<3 & valuebet >= 2  & sport_id == 18)|(casa == "BetVictor" & Odd>=3 & valuebet >= 2 & sport_id == 18)')
    dicas_envio_s3 = dicas_envio.rename(columns = dict(zip(['casa', 'Tipo', 'sport_id','league_name','home_name', 'away_name','DICA'   , 'Odd' ,'id_jogo' ,'valuebet' ],     ['Casa', 'Tipo', 'Esporte', 'Campeonato','Time1', 'Time2', 'Dica', 'Odd','id_jogo','valuebet'])))[['Casa', 'Tipo', 'Esporte', 'Campeonato','Time1', 'Time2', 'Dica', 'Odd','id_jogo','valuebet']]
    for i in range(dicas_envio_s3.shape[0]):
        series = dicas_envio_s3.iloc[i,:]
        #Aplica politica de dicas na linha abaixo
        # if series.Esporte ==18 and series.Odd>=3. and series.Odd<5. and series.valuebet>=3. and series.Casa =='BetVictor' and series.Dica in ['1_away', '1_home']:
        print("VALUEBET QUENTE, ENVIA PARA S3")
        # s3_upload_csv(pd.DataFrame(series.drop(labels=['valuebet'])).T,'s3://magicbetbucketteste/DicasEnviadas/'+ str(ultimo_id+ 1) + '.csv','')
        s3_upload_csv(pd.DataFrame(series.drop(labels=['valuebet'])).T,'s3://magic-bet-raw/DicasCalculadas/'+'ano='+ano + '/mes='+mes + '/dia='+dia+'/'+ str(ultimo_id+ 1) + '.csv','')
        ultimo_id = ultimo_id+ 1