# -*- coding: utf-8 -*-
import pandas as pd
from Dominios import dict_de_para_paises
import re
def retorna_nome_pontos(esporte):
    """Sumario

    Parametros:
    esporte (int): id do esporte da consulta

   """

    if esporte == 1:
        ponto = 'Gols'
    elif esporte == 13:
        ponto = "Games"
    else:
        ponto = "Pontos"
    return ponto
    
def gera_link_bet365(nome_time):
    """Sumario

    Parametros:
    nome_time (string) : Nome de um dos times para gerar o link

   """
    string = r'https://www.bet365.com/#/AX/K^'
    nome_time2 = ''.join(dict_de_para_paises[p.upper()] if p.upper() in dict_de_para_paises else p for p in re.split(r'(\W+)', nome_time))
    nome_time3 = nome_time2.replace(" ", "%20")

    return string +nome_time3 + '/'

def retorna_mensagem_handicap(coluna_tipo_dica,esporte):
    """Sumario

    Parametros:
    coluna_tipo_dica : tipo de ode que a dica é enviada
    esporte (int): id do esporte da consulta

   """
    
    # colunas_hand = ['end_1_handicap','end_2_handicap', 'end_3_handicap']
    # ['3_over', '1_away', '1_home', '3_under', '1_draw', '2_away',
    #    '2_home'],
    # colunas_hand = ['end_1_handicap','end_2_handicap', 'end_3_handicap']
    if coluna_tipo_dica[0] =='1':
        # col_hand = colunas_hand[0]
        mensagem_tipo = ''
    elif coluna_tipo_dica[0] =='2':
        # col_hand = colunas_hand[1]
        mensagem_tipo = '\n<b>Handicap : </b>'
    elif coluna_tipo_dica[0] =='3':
        # col_hand = colunas_hand[2]
        ponto =retorna_nome_pontos(esporte = esporte)
        mensagem_tipo = '\n<b>Total de '+ponto+': </b>' 
    return mensagem_tipo
    # return col_hand, mensagem_tipo


def retorna_text_handicap(coluna_od,handicap_base,esporte):
    """Sumario

    Parametros:
    coluna_od : tipo de ode que a dica é enviada
    handicap_base (int): valor do handicap  para tratamento
    esporte (int): id do esporte da consulta

   """
    ods_visitante = [ '2_away']
    colunas_hand = ['end_1_handicap','end_2_handicap', 'end_3_handicap']
    col_hand= 'Handicap' 
    mensagem_tipo = retorna_mensagem_handicap(coluna_tipo_dica = coluna_od, esporte = esporte)
    if coluna_od in ods_visitante:
        handicap_base = -handicap_base
    if coluna_od[0] == '1':
        handicap_valor = ""
    elif (4*handicap_base)%2 == 1:
        handicap_valor = str(handicap_base-0.25)+ '/'+ str(handicap_base+0.25)
    else:
        handicap_valor = str(handicap_base)
    return handicap_valor


def gera_mensagem_final(series):
    """Sumario

    Parametros:
    series (pandas series): Linha que sera usada para envio de dica

   """
    
    # valor_ode = '{:.3f}'.format(series[coluna_od])

    series = series.astype('unicode')
    coluna_od = series['DICA']
    esporte = int(series.sport_id)
    valor_ode = str(round(float(series['Odd']),3))

    col_hand= 'Handicap' 
    mensagem_tipo = retorna_mensagem_handicap(coluna_tipo_dica = coluna_od, esporte = esporte)
    handicap_valor = retorna_text_handicap(coluna_od = coluna_od,handicap_base = float(series['Handicap']), esporte = esporte)
    if coluna_od[0] =='1':
        handicap_valor = ""
    if series['casa'] =='Bet365':
        
        link_casa = gera_link_bet365(series.home_name)
        texto_link =  "\n<b>Link : </b><a href ='"+ link_casa +"'>Clique Aqui</a> "
    else :
        texto_link =''

    # string = '<b>Casa de apostas : </b>'+ series['casa']+'\n<b>Tipo : </b> Pre-Match'+'\n<b>Esporte : </b>'+ trata_nome_esporte(esporte = series.sport_id)  +'\n<b>Campeonato : </b>'+series.league_name+'\n<b>Jogo : </b>'+ series.home_name +" X "+ series.away_name +'\n<b>Dica : </b>'+ trata_nome_dica(dica = str(coluna_od), esporte = esporte) +mensagem_tipo + handicap_valor     +'\n<b>Odd : </b>' + valor_ode + texto_link
    string = '<b>Campeonato : </b>'+series.league_name+'\n<b>Jogo : </b>'+ series.home_name +" X "+ series.away_name +'\n<b>Dica : </b>'+ trata_nome_dica(dica = str(coluna_od), esporte = esporte) +mensagem_tipo + handicap_valor     +'\n<b>Odd : </b>' + valor_ode +'\n<b>Valuebet : </b>' +  str(round(float(series['valuebet']),3))
    
    return string

def trata_handcap(base,coluna):
    """Sumario

    Parametros:
    base (pandas dataframe): base que recebera tratamento
    coluna (string): coluna que sera tratada

   """
    base[coluna] = base[coluna].astype('unicode')


    base[coluna] = base[coluna].str.replace('./.50','/.5', regex=True).str.replace('1-1','1/1').str.replace('2-2','2/2').str.replace('3-3','3/3').str.replace('4-4','4/4').str.replace('5-5','5/5').str.replace('6-6','6/6').str.replace('7-7','7/7').str.replace('8-8','8/8').str.replace('9-9','9/9').str.replace('0-0','0/0').str.replace('5-1','5/1').str.replace('5-2','5/2').str.replace('5-3','5/3').str.replace('5-4','5/4').str.replace('5-5','5/5').str.replace('5-6','5/6').str.replace('5-7','5/7').str.replace('5-8','5/8').str.replace('5-9','5/9').str.replace('5-0','5/10')
    base['SINAL_POSITIVO'] = [-1  if i in [['-'], ['-', '-']] else 1 for i in base[coluna].str.findall('-')]
    base[coluna] = base[coluna].apply(lambda x: str(x).replace('0,5','0.5').replace('2,5','2.5').replace(' ','').replace("+","").replace("-","").replace(",","/").replace(".000",".00").replace(".00",".0").replace(".0","").replace("500","50").replace("50","5"))
    base[coluna] = base[coluna].str.replace('0.5/1','0.75').str.replace('0/0.5','0.25').str.replace('1/1.5','1.25').str.replace('1.5/2','1.75').str.replace('2/2.5','2.25').str.replace('2.5/3','2.75').str.replace('3/3.5','3.25').str.replace('3.5/4','3.75').str.replace('4/4.5','4.25').str.replace('4.5/5','4.75').str.replace('5/5.5','5.25').str.replace('5.5/6','5.75').str.replace('6/6.5','6.25').str.replace('6.5/7','6.75').str.replace('0/0','0').str.replace('1/1','1').str.replace('02','2')
    base[coluna] = base['SINAL_POSITIVO']*pd.to_numeric(base[coluna], downcast="float", errors  = 'coerce') 
    base = base.drop(['SINAL_POSITIVO'], axis = 1)

    return base
 # Transforma handcap num valor do nosso dominio (multiplos de 0.25)

def trata_nome_esporte(esporte):
    """Sumario

    Parametros:
    esporte (int): id do esporte da consulta

   """
    global resposta
    esporte=str(esporte)
    if esporte =='1':
        resposta = 'Futebol'
    elif esporte =='13':
        resposta = 'Tennis'
    elif esporte =='78':
        resposta = 'Handball'
    elif esporte =='17':
        resposta = 'Hockey no Gelo'
    elif esporte =='12':
        resposta = 'Futebol Americano'
    elif esporte =='83':
        resposta = 'Futsal'
    elif esporte =='92':
        resposta = 'Tennis de Mesa'
    elif esporte =='8':
        resposta = 'Rugby'
    elif esporte =='36':
        resposta = 'Futebol Australiano'
    elif esporte =='9':
        resposta = 'Box/UFC'
    elif esporte =='90':
        resposta = 'Floorball'
    elif esporte =='110':
        resposta = 'Polo Aquatico'
    elif esporte =='151':
        resposta = 'E-sports'
    elif esporte =='18':
        resposta = 'Basketball'
    elif esporte =='91':
        resposta = 'Volleyball'
    elif esporte =='16':
        resposta = 'Baseball'
    elif esporte =='14':
        resposta = 'Snooker'
    elif esporte =='3':
        resposta = 'Cricket'
    elif esporte =='15':
        resposta = 'Dardos'
    elif esporte =='94':
        resposta = 'Badminton'
    elif esporte =='19':
        resposta = 'Rugby League'
    elif esporte =='66':
        resposta = 'Boliche'
    elif esporte =='75':
        resposta = 'Futebol gaelico'
    elif esporte =='95':
        resposta = 'Volley de Praia'
    elif esporte =='107':
        resposta = 'Squash'
    else:
        resposta = ''

    return resposta


def trata_nome_dica(dica,esporte):
    """Sumario

    Parametros:
    dica(string): Tipo de ode que esta sendo olhada ['end_1_away_od','end_1_draw_od','end_1_home_od','end_2_away_od','end_2_home_od','end_3_over_od','end_3_under_od']
    esporte (int): id do esporte da consulta

   """
    todos_tipos_aposta = ['end_1_away_od','end_1_draw_od','end_1_home_od','end_2_away_od','end_2_home_od','end_3_over_od','end_3_under_od']
    todos_tipos_aposta = ['1_away','1_draw','1_home','2_away','2_home','3_over','3_under']
    # global retorno
    ponto =retorna_nome_pontos(esporte = esporte)
    if dica == todos_tipos_aposta[0]:
        retorno = 'A favor do Visitante'
    if dica == todos_tipos_aposta[1]:
        retorno = 'Empate'
    if dica == todos_tipos_aposta[2]:
        retorno = 'A favor do Time da Casa'
    if dica == todos_tipos_aposta[3]:
        retorno = 'Handicap para o Visitante'
    if dica == todos_tipos_aposta[4]:
        retorno = 'Handicap para o Time da Casa'
    if dica == todos_tipos_aposta[5]:
        retorno = 'Total de '+ponto+' Acima'
    if dica == todos_tipos_aposta[6]:
        retorno = 'Total de '+ponto+' Abaixo'
    return retorno


