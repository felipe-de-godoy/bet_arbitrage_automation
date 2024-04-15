# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
colunas_ods_total = [ 'end_1_away_od', 'end_1_draw_od', 'end_1_home_od', 'end_2_away_od', 'end_2_home_od', 'end_3_over_od', 'end_3_under_od']
# corte_casa = 6 # Numero de corte de casas (>n)
from Dominios import minimo_de_casas as corte_casa
from Dominios import ode_maxima_aceitavel as corte_odd
from Dominios import baseline_valuebet as corte_valuebet
from Dominios import lista_casas_media
from Dominios import casas_interesse as  lista_casas_dica
from Dominios import corte_minimo_odd
# from Dominios import   lista_casas_dica
# corte_odd = 20 # Numero de corte de odd maxima (<n)
# corte_valuebet = 1.9999999 # Numero de corte de valuebet minima (>n)
# Nao estao sendo usadas
# CONNECTION_STRING = 'Driver={ODBC Driver 17 for SQL Server};Server=tcp:magicbet.database.windows.net,1433;Database=MagicBet;Uid=mb;Pwd=Magicbet123*;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
# colunas_DICAS = ['DICA','Timestamp','Timestamp_DICA','away_name','casa','end_1_away_od','end_1_draw_od','end_1_handicap','end_1_home_od','end_2_away_od','end_2_handicap','end_2_home_od','end_3_handicap','end_3_over_od','end_3_under_od','handicap_valor','home_name','id_jogo','league_name','numero_casas','odd_media','odd_melhor','prob','prob_media','prob_melhor','sport_id','ss', 'valuebet','bet365_id','esporte']

# def retorna_base_sql_server(tabela_sql,string_colunas ='*',condicoes ='', CONNECTION_STRING= CONNECTION_STRING):
#     """""Sumario

#     Parametros:
#     tabela_sql (list) : Nome da tabela origem que esta no SQL Server
#     string_colunas (int): Codigo que fica entre o Select e o From, pode ser listadas as colunas e incluidos tratamentos como cast,put, etc. Padrao é pegar a tabela inteira
#     condicoes (string) : condicoes do  tipo where ou having
#     CONNECTION_STRING(string): string para conectar no banco de dados SQL
#     Retorno:
#     Base SQL com as condicoes impostas
#     """
#     conn = pyodbc.connect(CONNECTION_STRING)
#     sql_query = pd.read_sql_query('SELECT '+string_colunas+' FROM ' +tabela_sql + condicoes,conn)
#     print("Leu a base " + tabela_sql)
#     return sql_query


def calcula_valuebet(np_odd_casa_dica,np_odd_casa_media):
    """""Sumario

    Parametros:
    np_odd_casa_dica (numpy array) : odds das casas escolhidas para dar dica
    np_odd_casa_media (numpy array) : odds das casas escolhidas para calcular a media 
    Retorno:
    3 numpy arrays -> Valuebet, Probabilidade das casas de dica, Probabilidade media 
    das casas de calculo de media
    """
    # Probabilidade das casas de dicas e de media
    npA_prob_casa_dicas = 100/np_odd_casa_dica
    npA_prob_casa_media = 100/np_odd_casa_media
    
    # Probabilidade media das casas de media
    npA_prob_media_casa_media = np.nanmean(npA_prob_casa_media, axis=1).reshape(len(npA_prob_casa_media),1)
    
    # Calcula valuebet
    npA_valuebet = npA_prob_media_casa_media - npA_prob_casa_dicas
    
    return npA_valuebet,npA_prob_casa_dicas,npA_prob_media_casa_media

def filtra_array_num_min_casas(lista_arr_original,arr_filtrador,corte_casa):
    """Sumario

    Parametros:
    lista_arr_original(lista): lista com numpy arrays dos dados a serem filtrados pelo numero 
    minimo de casas de calculo de media(esporte, casa, odd, etc)
    arr_filtrador(numpy array): array de odds das casas de calculo de media
    corte_casa (integer): Numero int para o corte minimo de casas para o calculo da media -> 
    N_Casas > corte_casa
    Retorno:
    Retorna uma lista contendo numpy arrays dos dados de entrada filtrados

   """
    lista_np_original = list()
    
    arr_filtro_nan = np.where(~np.isnan(arr_filtrador),1,0)
    arr_cont = np.sum(arr_filtro_nan,axis=1).reshape(arr_filtrador.shape[0],1)
    arr_cont = np.pad(arr_cont,pad_width=((0,0),(0,arr_filtro_nan.shape[1]-1)),mode='reflect', reflect_type='even')
    mask = (arr_cont > corte_casa)
    dim1 = np.any(mask, axis=1).sum()
    
    if dim1 == 0:
        return 0
    
    np_contador = arr_cont[mask].reshape(dim1, -1)
    
    for arr_original in lista_arr_original:
        if ((arr_original.shape[1] == 1) & (arr_filtrador.shape[1] > 1)):
            arr_original = np.pad(arr_original,pad_width=((0,0),(0,arr_filtrador.shape[1]-1)),mode='reflect', reflect_type='even')

        else:
            pass

        lista_np_original.append(arr_original[mask].reshape(dim1, -1))
        
    lista_np_original.append(np_contador)
    
    return lista_np_original


def filtra_array_valuebet(arr_original,arr_filtrador_odd,arr_filtrador_valuebet,corte_odd,corte_valuebet, corte_minimo_odd,tipo_processamento):
    """Sumario

    Parametros:
    arr_original(numpy array): numpy array dos dados a serem filtrados por valuebet e por odd 
    maxima permitida (esporte, casa, odd, etc)
    arr_filtrador_odd (numpy array): array de odds das casas de dicas para cortar a odd maxima permitida
    arr_filtrador_valuebet (numpy array): array de valuebets para cortar o valor minimo permitido
    corte_odd (float): Numero float para o corte maximo de odd permitida -> Odd < corte_odd
    corte__minimo_odd (float): Numero float para o corte minimo de odd permitida -> Odd > corte__minimo_odd
    corte_valuebet (float): Numero float para o corte minimo de valuebet permitido -> Valuebet > corte_valuebet
    tipo_processamento(int): se é pprocessamento de rotina ou simulacao
    Retorno:
    Retorna um numpy array dos dados de entrada filtrados

   """
    if ((arr_original.shape[1] == 1) & (arr_filtrador_odd.shape[1] > 1)):
        arr_original = np.pad(arr_original,pad_width=((0,0),(0,arr_filtrador_odd.shape[1]-1)),mode='reflect', reflect_type='even')
    
    else:
        pass
    
    arr_odd_max_aux = np.nanmax(arr_filtrador_odd,axis=1).reshape(len(arr_filtrador_odd),1)
    arr_odd_max = np.pad(arr_odd_max_aux,pad_width=((0,0),(0,arr_filtrador_odd.shape[1]-1)),mode='reflect', reflect_type='even')
    if tipo_processamento ==1:
        mask_odd = np.logical_and((arr_odd_max < corte_odd ), (arr_odd_max > corte_minimo_odd ))
    else:
        mask_odd = (arr_odd_max < corte_odd )
    dim_odd = np.any(mask_odd, axis=1).sum()
    
    if dim_odd == 0:
        return 0

    np_odd = arr_filtrador_odd[mask_odd].reshape(dim_odd, -1)
    
    arr_filtrador_valuebet = arr_filtrador_valuebet[mask_odd].reshape(dim_odd, -1)
    arr_original = arr_original[mask_odd].reshape(dim_odd, -1)
    
    arr_valuebet_max_aux = np.nanmax(arr_filtrador_valuebet,axis=1).reshape(len(arr_filtrador_valuebet),1)
    arr_valuebet_max = np.pad(arr_valuebet_max_aux,pad_width=((0,0),(0,arr_original.shape[1]-1)),mode='reflect', reflect_type='even')
    if tipo_processamento ==1:
        mask_valuebet = (arr_valuebet_max > corte_valuebet)
    else:
        mask_valuebet = (arr_valuebet_max > 0.)
    dim_valuebet = np.any(mask_valuebet, axis=1).sum()
    
    if dim_valuebet == 0:
        return 0

    np_original = arr_original[mask_valuebet].reshape(dim_valuebet, -1)
    np_valuebet = arr_filtrador_valuebet[mask_valuebet].reshape(dim_valuebet, -1)
    np_maxvaluebet = arr_valuebet_max[mask_valuebet].reshape(dim_valuebet, -1)
    linhas_ = np.arange(len(np_original))
    colunas_ = np.nanargmax(np.where((np_valuebet==np_maxvaluebet),np_valuebet,np.nan),axis=1)
    
    return np_original[linhas_,colunas_]


def dica_dataframe(np_esporte, np_jogo, np_casa, np_handicap, np_odd, lista_casas_media, 
                   lista_casas_dica, corte_casa, corte_odd, corte_valuebet, tipo, corte_minimo_odd, tipo_processamento):
    """Sumario

    Parametros:
    np_esporte(numpy array): numpy array dos esportes
    np_jogo(numpy array): numpy array dos jogos
    np_casa(numpy array): numpy array das casas
    np_handicap(numpy array): numpy array dos handicaps
    np_odd(numpy array): numpy array das odds
    lista_casas_media (list): lista das casas para para calculo de media
    lista_casas_dica (list): lista das casas para para gerar dica
    corte_casa (integer): Numero int para o corte minimo de casas para o calculo da media -> 
    N_Casas > corte_casa
    corte_odd (float): Numero float para o corte maximo de odd permitida -> Odd < corte_odd
    corte_valuebet (float): Numero float para o corte minimo de valuebet permitido -> Valuebet > corte_valuebet
    tipo (string): tipo de dica (ex: "1_home")
    corte__minimo_odd (float): Numero float para o corte minimo de odd permitida -> Odd > corte__minimo_odd
    tipo_processamento(int): se é simulacao ou rotina
    Retorno:
    Retorna um dataframe com todas as dicas a serem dadas para mercado em questao

   """
    
    colunas = ['sport_id','id_jogo','casa','Handicap','Odd','Odd_media','Prob','Prob_media','valuebet','Num_casas','Tipo','DICA']
    pd_final = pd.DataFrame()
    
    # Separando grupos de casas para dar dica e para calcular a media
    np_casa_media = np.where(np.isin(np_casa,np.array(lista_casas_media)),np_casa,0)
    np_casa_dica = np.where(np.isin(np_casa,np.array(lista_casas_dica)),np_casa,0)
    
    # Separando grupos de odds das casas para dar dica e para calcular a media
    np_odd_casa_media = np.where(np.isin(np_casa,np.array(lista_casas_media)),np_odd,np.nan)
    np_odd_casa_dica = np.where(np.isin(np_casa,np.array(lista_casas_dica)),np_odd,np.nan)
    
    # Calculando valuebet
    np_valuebet, np_prob, np_prob_media = calcula_valuebet(np_odd_casa_dica = np_odd_casa_dica,np_odd_casa_media = np_odd_casa_media)
    np_odd_media = np.nanmean(np_odd_casa_media, axis=1).reshape(len(np_odd),1)
    
    # Filtrando numero minimo de casas para calculo de media
    lista_np_para_filtrar = [np_esporte,np_jogo,np_casa,np_handicap,np_odd_casa_dica,np_odd_media,np_prob,np_prob_media,np_valuebet]    
    resultado1 = filtra_array_num_min_casas(lista_arr_original = lista_np_para_filtrar,arr_filtrador =  np_odd_casa_media,corte_casa =  corte_casa)
    if type(resultado1) == int:
        return pd_final
    
    # Filtrando valuebet maxima
    resultado = [filtra_array_valuebet(arr_original = item,arr_filtrador_odd = resultado1[4],arr_filtrador_valuebet = resultado1[8],corte_odd = corte_odd,corte_valuebet = corte_valuebet, corte_minimo_odd = corte_minimo_odd, tipo_processamento = tipo_processamento) for item in resultado1]
    
    if type(resultado[0]) == int:
        return pd_final
    
    for i in range(10):
        pd_final = pd.concat([pd_final,pd.DataFrame(data=resultado[i], columns=[colunas[i]])],
                             axis=1)

    pd_final = pd.concat([pd_final,pd.DataFrame(data=np.array([tipo[0]]*len(resultado[0])), columns=[colunas[10]])],
                         axis=1)
    pd_final = pd.concat([pd_final,pd.DataFrame(data=np.array([tipo]*len(resultado[0])), columns=[colunas[11]])],
                         axis=1)
    
    return pd_final


def roda_simulacao(lista_esporte, lista_jogo, lista_casa, lista_1, lista_2, lista_3,
                   lista_casas_media, lista_casas_dica, corte_casa, corte_odd, corte_valuebet, corte_minimo_odd,tipo_processamento):
    """Sumario

    Parametros:
    lista_esporte(list): lista com numpy arrays dos esportes para todos os mercados
    lista_jogo(list): lista com numpy arrays dos jogos para todos os mercados
    lista_casa(list): lista com numpy arrays das casas para todos os mercados
    lista_1(list): lista com numpy arrays das odds e handicap do mercado 1
    lista_2(list): lista com numpy arrays das odds e handicap do mercado 2
    lista_3(list): lista com numpy arrays das odds e handicap do mercado 3
    lista_casas_media (list): lista das casas para para calculo de media
    lista_casas_dica (list): lista das casas para para gerar dica
    corte_casa (integer): Numero int para o corte minimo de casas para o calculo da media -> 
    N_Casas > corte_casa
    corte_odd (float): Numero float para o corte maximo de odd permitida -> Odd < corte_odd
    corte_valuebet (float): Numero float para o corte minimo de valuebet permitido -> Valuebet > corte_valuebet
    corte__minimo_odd (float): Numero float para o corte minimo de odd permitida -> Odd > corte__minimo_odd
    tipo_processamento(int) se é rotina ou simulacao
    Retorno:
    Retorna um dataframe com todas as dicas a serem dadas (com tratamento de duplicidade de mercados, 
    ex: "1_home" e "1_away" nao sao permitidos)

   """


    # Definindo arrays completos que atendem ao primeiro corte de ter pelo menos 6 casas por jogo
    
    flag_1 = True
    flag_1_home = True
    flag_1_away = True
    flag_1_draw = True
    
    flag_2 = True
    flag_2_home = True
    flag_2_away = True
    
    flag_3 = True
    flag_3_over = True
    flag_3_under = True
    
    try:
        stack_npA_esporte_1 = np.stack(lista_esporte[0], axis=0)
        stack_npA_jogo_1 = np.stack(lista_jogo[0], axis=0)
        stack_npA_casa_1 = np.stack(lista_casa[0], axis=0)
        stack_npA_odd_1_handicap = np.stack(lista_1[3], axis=0)
        try:
            stack_npA_odd_1_home = np.stack(lista_1[0], axis=0)
        except:
            flag_1_home = False
        try:
            stack_npA_odd_1_away = np.stack(lista_1[1], axis=0)
        except:
            flag_1_away = False
        try:
            stack_npA_odd_1_draw = np.stack(lista_1[2], axis=0)
        except:
            flag_1_draw = False
        
    except:
        flag_1 = False
    
    try:
        stack_npA_esporte_2 = np.stack(lista_esporte[1], axis=0)
        stack_npA_jogo_2 = np.stack(lista_jogo[1], axis=0)
        stack_npA_casa_2 = np.stack(lista_casa[1], axis=0)
        stack_npA_odd_2_handicap = np.stack(lista_2[2], axis=0)
        try:
            stack_npA_odd_2_home = np.stack(lista_2[0], axis=0)
        except:
            flag_2_home = False
        try:
            stack_npA_odd_2_away = np.stack(lista_2[1], axis=0)
        except:
            flag_2_away = False
        
    except:
        flag_2 = False

    try:
        stack_npA_esporte_3 = np.stack(lista_esporte[2], axis=0)
        stack_npA_jogo_3 = np.stack(lista_jogo[2], axis=0)
        stack_npA_casa_3 = np.stack(lista_casa[2], axis=0)
        stack_npA_odd_3_handicap = np.stack(lista_3[2], axis=0)
        try:
            stack_npA_odd_3_over = np.stack(lista_3[0], axis=0)
        except:
            flag_3_over = False
        try:
            stack_npA_odd_3_under = np.stack(lista_3[1], axis=0)
        except:
            flag_3_under = False
        
    except:
        flag_3 = False

    # Gerando dataframe final com dicas
    df_final = pd.DataFrame()
    if flag_1:
        if flag_1_home:
            df_1_home = dica_dataframe(stack_npA_esporte_1, stack_npA_jogo_1, stack_npA_casa_1, stack_npA_odd_1_handicap,
                                       stack_npA_odd_1_home, lista_casas_media, lista_casas_dica, 
                                       corte_casa, corte_odd, corte_valuebet, tipo='1_home', corte_minimo_odd = corte_minimo_odd, tipo_processamento= tipo_processamento)
            df_final = df_final.append(df_1_home)
        if flag_1_away:
            df_1_away = dica_dataframe(stack_npA_esporte_1, stack_npA_jogo_1, stack_npA_casa_1, stack_npA_odd_1_handicap,
                                       stack_npA_odd_1_away, lista_casas_media, lista_casas_dica,
                                       corte_casa, corte_odd, corte_valuebet, tipo='1_away', corte_minimo_odd = corte_minimo_odd, tipo_processamento= tipo_processamento)
            df_final = df_final.append(df_1_away)
        if flag_1_draw:
            df_1_draw = dica_dataframe(stack_npA_esporte_1, stack_npA_jogo_1, stack_npA_casa_1, stack_npA_odd_1_handicap,
                                       stack_npA_odd_1_draw, lista_casas_media, lista_casas_dica,
                                       corte_casa, corte_odd, corte_valuebet, tipo='1_draw', corte_minimo_odd = corte_minimo_odd, tipo_processamento= tipo_processamento)
            df_final = df_final.append(df_1_draw)
    if flag_2:
        if flag_2_home:
            df_2_home = dica_dataframe(stack_npA_esporte_2, stack_npA_jogo_2, stack_npA_casa_2, stack_npA_odd_2_handicap,
                                       stack_npA_odd_2_home, lista_casas_media, lista_casas_dica,
                                       corte_casa, corte_odd, corte_valuebet, tipo='2_home', corte_minimo_odd = corte_minimo_odd, tipo_processamento= tipo_processamento)
            df_final = df_final.append(df_2_home)
        if flag_2_away:
            df_2_away = dica_dataframe(stack_npA_esporte_2, stack_npA_jogo_2, stack_npA_casa_2, stack_npA_odd_2_handicap,
                                       stack_npA_odd_2_away, lista_casas_media, lista_casas_dica,
                                       corte_casa, corte_odd, corte_valuebet, tipo='2_away', corte_minimo_odd = corte_minimo_odd, tipo_processamento= tipo_processamento)
            df_final = df_final.append(df_2_away)
    if flag_3:
        if flag_3_over:
            df_3_over = dica_dataframe(stack_npA_esporte_3, stack_npA_jogo_3, stack_npA_casa_3, stack_npA_odd_3_handicap,
                                       stack_npA_odd_3_over, lista_casas_media, lista_casas_dica,
                                       corte_casa, corte_odd, corte_valuebet, tipo='3_over', corte_minimo_odd = corte_minimo_odd, tipo_processamento= tipo_processamento)
            df_final = df_final.append(df_3_over)
        if flag_3_under:
            df_3_under = dica_dataframe(stack_npA_esporte_3, stack_npA_jogo_3, stack_npA_casa_3, stack_npA_odd_3_handicap,
                                       stack_npA_odd_3_under, lista_casas_media, lista_casas_dica,
                                       corte_casa, corte_odd, corte_valuebet, tipo='3_under', corte_minimo_odd = corte_minimo_odd, tipo_processamento= tipo_processamento)
            df_final = df_final.append(df_3_under)

    if df_final.shape[0] > 0 :
        df_final.sort_values(by=['id_jogo','valuebet'],ascending=False,inplace=True)
        df_final.drop_duplicates(subset=['id_jogo','Tipo','Handicap'],inplace=True)
        df_final.reset_index(drop=True,inplace=True)

        
        return df_final
    else:
        return df_final

#odes_input = retorna_base_sql_server(string_colunas = '*',tabela_sql =  'VW_ODES',CONNECTION_STRING = CONNECTION_STRING)

def calcula_dicas_vetorizado(odes_input,corte_casa = corte_casa, lista_casas_media = lista_casas_media, lista_casas_dica = lista_casas_dica,  corte_odd = corte_odd, corte_valuebet = corte_valuebet, corte_minimo_odd = corte_minimo_odd , tipo_processamento=1):
    # odes_input = pd.read_csv('amostra_final.csv')
    odes_input['id_jogo'] = odes_input['id_jogo'].astype(int)     
    odes_input[colunas_ods_total] = odes_input[colunas_ods_total].apply(pd.to_numeric, errors='coerce')
    odes_input['end_1_handicap'] = 0

    odes_input = odes_input.drop_duplicates(subset=['id_jogo','casa','esporte'])

    # Arrays a partir do Data Frame
    arr_ss = odes_input['end_1_ss'].values
    arr_ss = np.char.add(odes_input['end_1_ss'].values.astype(str),
                        odes_input['end_2_ss'].values.astype(str))
    arr_ss = np.char.add(arr_ss,
                        odes_input['end_3_ss'].values.astype(str))

    mask_ss = (arr_ss == 'nannannan')
    dim_ss = np.any(mask_ss).sum()

    arr_esporte = odes_input['esporte'].values
    arr_esporte = arr_esporte[mask_ss]

    arr_id_jogos = odes_input['id_jogo'].values
    arr_id_jogos = arr_id_jogos[mask_ss]

    arr_casa = odes_input['casa'].values
    arr_casa = arr_casa[mask_ss]

    arr_1_home_odd = odes_input['end_1_home_od'].values
    arr_1_home_odd[arr_1_home_odd == 0] = np.nan
    arr_1_home_odd = arr_1_home_odd[mask_ss]

    arr_1_away_odd = odes_input['end_1_away_od'].values
    arr_1_away_odd[arr_1_away_odd == 0] = np.nan
    arr_1_away_odd = arr_1_away_odd[mask_ss]
    arr_1_draw_odd = odes_input['end_1_draw_od'].values
    arr_1_draw_odd[arr_1_draw_odd == 0] = np.nan
    arr_1_draw_odd = arr_1_draw_odd[mask_ss]
    arr_1_handicap = odes_input['end_1_handicap'].values
    arr_1_handicap = arr_1_handicap[mask_ss]

    arr_2_home_odd = odes_input['end_2_home_od'].values
    arr_2_home_odd[arr_2_home_odd == 0] = np.nan
    arr_2_home_odd = arr_2_home_odd[mask_ss]
    arr_2_away_odd = odes_input['end_2_away_od'].values
    arr_2_away_odd[arr_2_away_odd == 0] = np.nan
    arr_2_away_odd = arr_2_away_odd[mask_ss]
    arr_2_handicap = odes_input['end_2_handicap'].values
    arr_2_handicap = arr_2_handicap[mask_ss]

    arr_3_over_odd = odes_input['end_3_over_od'].values
    arr_3_over_odd[arr_3_over_odd == 0] = np.nan
    arr_3_over_odd = arr_3_over_odd[mask_ss]
    arr_3_under_odd = odes_input['end_3_under_od'].values
    arr_3_under_odd[arr_3_under_odd == 0] = np.nan
    arr_3_under_odd = arr_3_under_odd[mask_ss]
    arr_3_handicap = odes_input['end_3_handicap'].values
    arr_3_handicap = arr_3_handicap[mask_ss]


    # Criação das listas para cada mercado
    lista_esporte_1 = list()
    lista_esporte_2 = list()
    lista_esporte_3 = list()
    lista_jogo_1 = list()
    lista_jogo_2 = list()
    lista_jogo_3 = list()
    lista_casa_1 = list()
    lista_casa_2 = list()
    lista_casa_3 = list()

    lista_1_home_odd = list()
    lista_1_away_odd = list()
    lista_1_draw_odd = list()
    lista_1_handicap = list()
    lista_2_home_odd = list()
    lista_2_away_odd = list()
    lista_2_handicap = list()
    lista_3_over_odd = list()
    lista_3_under_odd = list()
    lista_3_handicap = list()

    # Determinando o tamanho máximo para cada um dos 3 mercados (otimizar o tamanho) -> versao preliminar
    tam_maximo_1 = np.max(np.bincount(arr_id_jogos))

    mercado_2 = np.char.add(arr_id_jogos.astype(str),np.array([arr_2_handicap]).astype(str)).reshape(len(arr_2_handicap),)
    tam = np.unique(mercado_2,return_counts=True)[1]
    tam_maximo_2 = np.max(tam)

    mercado_3 = np.char.add(arr_id_jogos.astype(str),np.array([arr_3_handicap]).astype(str)).reshape(len(arr_3_handicap),)
    tam = np.unique(mercado_3,return_counts=True)[1]
    tam_maximo_3 = np.max(tam)


    # Loop para cada jogo -> Criando arrays de tamanhos iguais para cada mercado
    for jogo in np.unique(arr_id_jogos):
        if len(arr_id_jogos[arr_id_jogos == jogo]) > corte_casa: # Fazer corte de SS para tirar live
            lista_esporte_1.append(np.pad(arr_esporte[arr_id_jogos == jogo], (0,tam_maximo_1-len(arr_esporte[arr_id_jogos == jogo])), 'constant', constant_values=0))
            lista_jogo_1.append(np.pad(arr_id_jogos[arr_id_jogos == jogo], (0,tam_maximo_1-len(arr_id_jogos[arr_id_jogos == jogo])), 'constant', constant_values=0))
            lista_casa_1.append(np.pad(arr_casa[arr_id_jogos == jogo], (0,tam_maximo_1-len(arr_casa[arr_id_jogos == jogo])), 'constant', constant_values=0))
            lista_1_home_odd.append(np.pad(arr_1_home_odd[arr_id_jogos == jogo], (0,tam_maximo_1-len(arr_1_home_odd[arr_id_jogos == jogo])), 'constant', constant_values=np.nan))
            lista_1_away_odd.append(np.pad(arr_1_away_odd[arr_id_jogos == jogo], (0,tam_maximo_1-len(arr_1_away_odd[arr_id_jogos == jogo])), 'constant', constant_values=np.nan))
            lista_1_draw_odd.append(np.pad(arr_1_draw_odd[arr_id_jogos == jogo], (0,tam_maximo_1-len(arr_1_draw_odd[arr_id_jogos == jogo])), 'constant', constant_values=np.nan))
            lista_1_handicap.append(np.pad(arr_1_handicap[arr_id_jogos == jogo], (0,tam_maximo_1-len(arr_1_handicap[arr_id_jogos == jogo])), 'constant', constant_values=np.nan))

            un,tam = np.unique(mercado_2[arr_id_jogos == jogo],return_counts=True)
            for str_h in un[tam>=6]:
                lista_esporte_2.append(np.pad(arr_esporte[(mercado_2 == str_h)], (0,tam_maximo_2-len(arr_esporte[(mercado_2 == str_h)])), 'constant', constant_values=0))
                lista_jogo_2.append(np.pad(arr_id_jogos[(mercado_2 == str_h)], (0,tam_maximo_2-len(arr_id_jogos[(mercado_2 == str_h)])), 'constant', constant_values=0))
                lista_casa_2.append(np.pad(arr_casa[(mercado_2 == str_h)], (0,tam_maximo_2-len(arr_casa[(mercado_2 == str_h)])), 'constant', constant_values=0))
                lista_2_home_odd.append(np.pad(arr_2_home_odd[(mercado_2 == str_h)], (0,tam_maximo_2-len(arr_2_home_odd[(mercado_2 == str_h)])), 'constant', constant_values=np.nan))
                lista_2_away_odd.append(np.pad(arr_2_away_odd[(mercado_2 == str_h)], (0,tam_maximo_2-len(arr_2_away_odd[(mercado_2 == str_h)])), 'constant', constant_values=np.nan))
                lista_2_handicap.append(np.pad(arr_2_handicap[(mercado_2 == str_h)], (0,tam_maximo_2-len(arr_2_handicap[(mercado_2 == str_h)])), 'constant', constant_values=np.nan))
                
            un,tam = np.unique(mercado_3[arr_id_jogos == jogo],return_counts=True)
            for str_h in un[tam>=6]:
                lista_esporte_3.append(np.pad(arr_esporte[(mercado_3 == str_h)], (0,tam_maximo_3-len(arr_esporte[(mercado_3 == str_h)])), 'constant', constant_values=0))
                lista_jogo_3.append(np.pad(arr_id_jogos[(mercado_3 == str_h)], (0,tam_maximo_3-len(arr_id_jogos[(mercado_3 == str_h)])), 'constant', constant_values=0))
                lista_casa_3.append(np.pad(arr_casa[(mercado_3 == str_h)], (0,tam_maximo_3-len(arr_casa[(mercado_3 == str_h)])), 'constant', constant_values=0))
                lista_3_over_odd.append(np.pad(arr_3_over_odd[(mercado_3 == str_h)], (0,tam_maximo_3-len(arr_3_over_odd[(mercado_3 == str_h)])), 'constant', constant_values=np.nan))
                lista_3_under_odd.append(np.pad(arr_3_under_odd[(mercado_3 == str_h)], (0,tam_maximo_3-len(arr_3_under_odd[(mercado_3 == str_h)])), 'constant', constant_values=np.nan))
                lista_3_handicap.append(np.pad(arr_3_handicap[(mercado_3 == str_h)], (0,tam_maximo_3-len(arr_3_handicap[(mercado_3 == str_h)])), 'constant', constant_values=np.nan))
                
        else:
            pass



    lista_esporte = [lista_esporte_1,lista_esporte_2,lista_esporte_3]
    lista_jogo = [lista_jogo_1,lista_jogo_2,lista_jogo_3]
    lista_casa = [lista_casa_1,lista_casa_2,lista_casa_3]
    lista_1 = [lista_1_home_odd,lista_1_away_odd,lista_1_draw_odd,lista_1_handicap]
    lista_2 = [lista_2_home_odd,lista_2_away_odd,lista_2_handicap]
    lista_3 = [lista_3_over_odd,lista_3_under_odd,lista_3_handicap]





    df_dicas = roda_simulacao(lista_esporte = lista_esporte, lista_jogo = lista_jogo, lista_casa = lista_casa, lista_1 = lista_1, lista_2 =lista_2, lista_3 = lista_3,
                    lista_casas_media = lista_casas_media, lista_casas_dica = lista_casas_dica, corte_casa = corte_casa, corte_odd = corte_odd, corte_valuebet = corte_valuebet, corte_minimo_odd = corte_minimo_odd,tipo_processamento=tipo_processamento)
    return df_dicas

# def filtra_politica(x):
#     df_polit = df_Politica[(df_Politica['Esporte']==x['Esporte'])]
#     if x['Odd_int'] >= df_polit['Odd_min'].max():
#         if x['Valuebet'] >= df_polit['VB_min'].min():
#             return True
#         else:
#             return False
#     else:
#         if x['Valuebet'] >= df_polit[df_polit['Odd_min'] == x['Odd_int']]['VB_min'].values[0]:
#             return True
#         else:
#             return False

# obj_Politica = {
#     'Esporte':[1],
#     'Odd_min':[2],
#     'VB_min':[2],
# }

# df_Politica = pd.DataFrame(obj_Politica)

# df_dicas_filtrado = df_dicas
# df_dicas_filtrado['Odd_int'] = df_dicas_filtrado['Odd']//1
# df_dicas_filtrado['Check'] = df_dicas_filtrado[['Esporte','Valuebet','Odd_int']].apply(filtra_politica,axis=1)
# df_dicas_filtrado = df_dicas_filtrado[df_dicas_filtrado['Check']]
# df_dicas_filtrado.drop(columns=['Odd_int','Check'], inplace=True)
# df_dicas_filtrado
