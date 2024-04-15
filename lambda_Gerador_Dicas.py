# -*- coding: utf-8 -*-



def main(event, context):   
    from DicasPreMatch import gera_dica_final
    from datetime import datetime
    print("Comecou um ciclo em =", datetime.now().strftime("%H:%M:%S"))
    print("Esporte Basquete")
    gera_dica_final(esporte =[ 18] ,  lista_casas_dica=['BetVictor'] , tipo_processamento=1, quantidade_de_paginas = 2)
    print("Terminou um ciclo em =", datetime.now().strftime("%H:%M:%S"))
    return { 
        'message' : "Sucesso"
    }

if __name__ == "__main__":   
    main('', '')
    


