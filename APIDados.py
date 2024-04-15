# -*- coding: utf-8 -*-
import json , requests
# bet_token_padrao = '57659-nlPvoqXEFejq5s'


from Dominios import bet_token as bet_token_padrao, timeout_api as timeout

def retorna_jogos(esporte, pagina = 1, bet_token = bet_token_padrao):
    """Sumario

    Parametros:
    esporte (int): id do esporte da consulta
    pagina (int): id da pagina da consulta
    bet_token (string) : token de conexao com API

    Retorno:
    JSON com jogos da api upcoming

   """
    print('CHAMA API DE JOGOS DO ESPORTE '+ str(esporte) +' PAGINA '+  str(pagina))
    try:
        api_jogos = requests.get("https://api.betsapi.com/v2/events/upcoming?sport_id="+str(esporte)+"&token=" + bet_token+"&page=" +str(pagina), timeout=timeout)
        resposta = json.loads(api_jogos.content.decode('utf-8'))
    except:
        resposta = {}
    return resposta 

def retorna_placar_dia(bet_token,esporte,dia,pag):
    """Sumario

    Parametros:
    bet_token (string) : token de conexao com API
    esporte (int): id do esporte da consulta
    dia (string) : dia a ser consultado
    pag (string) : numero da pagina  a ser consultada

    Retorno:
    JSON com placar do jogos da do dia e pagina consultados

   """
    link = "https://api.betsapi.com/v2/events/ended?" + "sport_id=" + str(esporte) + "&token=" + bet_token + "&day=" + dia + '&page=' + str(pag)
    api = requests.get(link)

    return json.loads(api.content.decode('utf-8'))

# def retorna_placar_dia_estatistica(token,link,event_id):
#     link = link + "&token=" + token + "&event_id=" + event_id
#     api = requests.get(link)

#     return json.loads(api.content.decode('utf-8'))

def retorna_placar(jogo, bet_token):
    """Sumario

    Parametros:
    jogo (int): id do jogo da consulta
    bet_token (string) : token de conexao com API

    Retorno:
    JSON com placar do jogos da api

   """
    print('CHAMA API DE PLACAR DO JOGO '+ str(jogo) )
    try:
        api_placar = requests.get('https://api.betsapi.com/v1/event/view?token=' + bet_token + '&event_id=' + str(jogo))
        resposta = json.loads(api_placar.content.decode('utf-8'))
    except:
        resposta = {}
    return resposta 
    
def retorna_odd(event_id, bet_token = bet_token_padrao):
    """Sumario

    Parametros:
    event_id (int): id do jogo da consulta
    bet_token (string) : token de conexao com API

    Retorno:
    JSON com odes do evento

   """
    # print('CHAMA API ODES')
    link = "http://api.betsapi.com/v2/event/odds/summary?token=" + str(bet_token) + "&event_id="+ event_id


    try:
        api_jogos = requests.get(link, timeout=timeout)
        api_odes_json = json.loads(api_jogos.content.decode('utf-8'))
    except:
        api_odes_json = {}

    # print('RETORNA JSON DAS ODES DO JOGO ' + event_id )
    
    return api_odes_json , event_id