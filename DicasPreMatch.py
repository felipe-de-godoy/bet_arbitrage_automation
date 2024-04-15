# -*- coding: utf-8 -*-
# from API.Telegram import manda_mensagem_telegram, retorna_id_chat

# PACOTES
import pandas as pd
from datetime import datetime
import time
# FUNCOES
from S3Conexao import armazena_bases_dicasfull_s3, armazena_bases_jogos_s3, armazena_bases_odes_s3
from TratamentoDados import retorna_jogos_odes
from TratamentoVetorizado import calcula_dicas_vetorizado
from APITelegram import envia_dicas_telegram
from S3Conexao import manda_dica_para_s3
# CONSTANTES
from Dominios import colunas_base_odes, colunas_DICAS,jogos_colunas
from Dominios import minimo_de_casas
from Dominios import lista_casas_media
from Dominios import casas_interesse as lista_casas_dica
from Dominios import QUERY_POLITICA_DICAS
# from APITelegram import manda_mensagem_telegram, retorna_id_chat

# from Dominios import   lista_casas_dica



def gera_dica_final(esporte,  tipo_processamento=1, caminho_base_odes_input='', caminho_base_jogos_input='', id_cenario=0, tipo_salvamento=1, caminho_resultado='', lista_casas_media=lista_casas_media, lista_casas_dica=lista_casas_dica,  quantidade_de_paginas =1):
    """Sumario

    Parametros:
    esporte (int): id do esporte da consulta
    casas_interesse (list) : lista de casas que são elegiveis a gerar a dica
    valuebet_minima(int) : Percentual minimo aceitavel para valuebet
    tipo_processamento(int): 1  para processamento normal, 2 para consulta de jogos no sql, 3 para consulta a partir de um caminho inputado
    caminho_base_odes_input(string): Colocar o caminho do csv de odes que esta no seu computador
    caminho_base_jogos_input(string): Colocar o caminho do csv de jogos que esta no seu computador
    id_cenario(int): id do cenario da simulacao, para rastreio posterior
    quantidade_de_paginas (int): numeros de paginas para consultar na api

   """
    jogos_total_consulta = pd.DataFrame([], columns=jogos_colunas)
    odds_total_consulta = pd.DataFrame([], columns=colunas_base_odes)
    # Bloco de captura das informacoes
    
    print('CAPTURA INFORMAÇÕES')
    print(datetime.now())
    jogos_total_consulta, odds_total_consulta, jogos_atuais = retorna_jogos_odes(
        lista_esporte=esporte, tipo_processamento=tipo_processamento, caminho_base_odes_input=caminho_base_odes_input, caminho_base_jogos_input=caminho_base_jogos_input, quantidade_de_paginas = quantidade_de_paginas)

    print('CALCULA VALUEBET')
    print(datetime.now())
    if jogos_atuais.shape[0]>0 : 

        dicas_envio = calcula_dicas_vetorizado(odes_input=jogos_atuais, corte_casa=minimo_de_casas,
                                            lista_casas_media=lista_casas_media, lista_casas_dica=lista_casas_dica, corte_minimo_odd= 0.,corte_valuebet = 0.,
                                            tipo_processamento=tipo_processamento)
        dicas_envio['Timestamp'] = pd.to_datetime(time.time(), unit='s')
        dicas_envio=dicas_envio.query(QUERY_POLITICA_DICAS)
        print('Temos '+str(dicas_envio.shape[0])+' Dicas novas' )
        if dicas_envio.shape[0]>0:
            dicas_envio = pd.merge(dicas_envio, jogos_atuais[['away_name', 'home_name', 'id_jogo', 'league_name']], on='id_jogo', how='left').drop_duplicates()
            # dicas_envio = dicas_envio[~dicas_envio['league_name'].str.upper().str.contains('|'.join(blacklist_paises))]

            # Bloco de envio das dicas
            print('GUARDA VALUEBET')
            print(datetime.now())
            if tipo_processamento == 1:
                print(datetime.now())
                print('ENVIA DICA S3')
                manda_dica_para_s3(dicas_envio)
                    
                print('ENVIA DICA TELEGRAM')
                envia_dicas_telegram(dicas_para_envio=dicas_envio)


            armazena_bases_dicasfull_s3( base_dicas=dicas_envio, id_cenario=id_cenario,tipo_processamento=tipo_processamento, tipo_salvamento=tipo_salvamento, caminho_resultado=caminho_resultado)
    
        # Bloco de armazenamento das bases
        print('GUARDA JOGOS E ODES')
        if tipo_processamento == 1:
            armazena_bases_jogos_s3(jogos_total_consulta=jogos_total_consulta,  tipo_processamento=tipo_processamento)
            armazena_bases_odes_s3(odds_total_consulta=odds_total_consulta,  tipo_processamento=tipo_processamento)


