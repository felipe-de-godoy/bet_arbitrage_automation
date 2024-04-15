# -*- coding: utf-8 -*-
bet_token = '57659-nlPvoqXEFejq5s'
BOT_API_TOKEN ="1039119605:AAHsBoGKTMvAU7pCNVAAQrcshfYgoOC0qYI"

key_s3    = 'AKIATIFWM6O7LNNWBXW7'
secret_s3 = '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'

path_s3_historico      = 's3://magic-bet-raw/Resultados/' 
file_s3_historico_name = 'historico.csv'

timeout_api = 10.0
QUERY_POLITICA_DICAS = '(casa == "BetVictor" & Odd>=3 & Odd<5 & valuebet >= 3  & sport_id == 18)'
CONNECTION_STRING = 'Driver={ODBC Driver 17 for SQL Server};Server=tcp:magicbet.database.windows.net,1433;Database=MagicBet;Uid=mb;Pwd=Magicbet123*;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'

colunas_DICAS = ['DICA','Timestamp','Timestamp_DICA','away_name','casa','end_1_away_od','end_1_draw_od','end_1_handicap','end_1_home_od','end_2_away_od','end_2_handicap','end_2_home_od','end_3_handicap','end_3_over_od','end_3_under_od','handicap_valor','home_name','id_jogo','league_name','numero_casas','odd_media','odd_melhor','prob','prob_media','prob_melhor','sport_id','ss', 'valuebet','bet365_id','esporte']

colunas_ods_total = [ 'end_1_away_od', 'end_1_draw_od', 'end_1_home_od', 'end_2_away_od', 'end_2_home_od', 'end_3_over_od', 'end_3_under_od']

colunas_consulta_jogos = ['id_jogo'    ,   'sport_id'      ,    'time'          ,    'time_status'        ,    'league_id'     ,    'league_name'   ,    'league_cc'     ,    'home_id'       ,    'home_name'     ,    'home_image_id' ,    'home_cc'       ,    'away_id'       ,    'away_name'     ,    'away_image_id' ,    'away_cc'    ,'ss'  ,'bet365_id'  ]


momentos0 = ['start', 'kickoff', 'end']


momentos10 = ['id', 'home_od', 'draw_od', 'away_od', 'ss', 'time_str', 'add_time']  
momentos11 = ['id', 'home_od', 'handicap', 'away_od', 'ss', 'time_str', 'add_time']  
momentos12 = ['id', 'over_od', 'handicap', 'under_od', 'ss', 'time_str', 'add_time']

blacklist_paises = ['AUSTRALIA','CHINA','RUSSIA','KOREA','JAPAN','CAMBODIA','MYANMAR','NEW ZEALAND','KOREA','TAIWAN','TAJIKISTAN','THAILAND','VIETNAM','MALAYSIA']

tipos_aposta = ['_1', '_2', '_3']

colunas_ods_1 = ['end_1_away_od', 'end_1_draw_od','end_1_home_od']
colunas_ods_2 = ['end_2_away_od', 'end_2_home_od']
colunas_ods_3 = ['end_3_over_od', 'end_3_under_od']



ods_visitante = [ 'end_2_away_od']

colunas_hand = ['end_1_handicap','end_2_handicap', 'end_3_handicap']







colunas_nao_nulas = ['end_1_add_time', 'end_1_away_od', 'end_1_draw_od','end_1_home_od', 'end_1_id', 'end_1_ss', 'end_1_time_str','end_2_add_time', 'end_2_away_od', 'end_2_handicap','end_2_home_od', 'end_2_id', 'end_2_ss', 'end_2_time_str','end_3_add_time', 'end_3_handicap', 'end_3_id', 'end_3_over_od','end_3_ss', 'end_3_time_str', 'end_3_under_od']
colunas_base_odes=['casa','end_1_add_time','end_1_away_od','end_1_draw_od','end_1_home_od','end_1_id','end_1_ss','end_1_time_str','end_2_add_time','end_2_away_od','end_2_handicap','end_2_home_od','end_2_id','end_2_ss','end_2_time_str','end_3_add_time','end_3_handicap','end_3_id','end_3_over_od','end_3_ss','end_3_time_str','end_3_under_od','id_jogo','kickoff_1_add_time','kickoff_1_away_od','kickoff_1_draw_od','kickoff_1_home_od','kickoff_1_id','kickoff_1_ss','kickoff_1_time_str','kickoff_2_add_time','kickoff_2_away_od','kickoff_2_handicap','kickoff_2_home_od','kickoff_2_id','kickoff_2_ss','kickoff_2_time_str','kickoff_3_add_time','kickoff_3_handicap','kickoff_3_id','kickoff_3_over_od','kickoff_3_ss','kickoff_3_time_str','kickoff_3_under_od','start_1_add_time','start_1_away_od','start_1_draw_od','start_1_home_od','start_1_id','start_1_ss','start_1_time_str','start_2_add_time','start_2_away_od','start_2_handicap','start_2_home_od','start_2_id','start_2_ss','start_2_time_str','start_3_add_time','start_3_handicap','start_3_id','start_3_over_od','start_3_ss','start_3_time_str','start_3_under_od','esporte','matching_dir','odds_update_1','odds_update_2','odds_update_3']
jogos_colunas = ['Timestamp', 'away_cc', 'away_id', 'away_image_id', 'away_name','bet365_id', 'home_cc', 'home_id', 'home_image_id', 'home_name','id_jogo', 'league_cc', 'league_id', 'league_name', 'sport_id', 'ss','time', 'time_status']

colunas_API_ODES = ['start_1_id', 'start_1_home_od', 'start_1_draw_od', 'start_1_away_od', 'start_1_ss', 'start_1_time_str', 'start_1_add_time', 'start_2_id', 'start_2_home_od', 'start_2_handicap', 'start_2_away_od', 'start_2_ss', 'start_2_time_str', 'start_2_add_time', 'start_3_id', 'start_3_over_od', 'start_3_handicap', 'start_3_under_od', 'start_3_ss', 'start_3_time_str', 'start_3_add_time']
CONNECTION_STRING = 'Driver={ODBC Driver 17 for SQL Server};Server=tcp:magicbet.database.windows.net,1433;Database=MagicBet;Uid=mb;Pwd=Magicbet123*;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'

corte_minimo_odd = 2.
minimo_de_casas = 5
baseline_valuebet = 2.
ode_maxima_aceitavel = 20.
probabilidade = 0.05 #probabilidade de enviar no grupo free 5%
# casas_interesse = [ 'Bet365','BetVictor', 'WilliamHill', 'PinnacleSports', '188Bet']
casas_interesse = [ 'Bet365','BetVictor']

lista_casas_media = ['10Bet', '188Bet', '1XBet', '888Sport', 'Bet365', 'BetAtHome',
    'BetClic', 'BetFair', 'BetRegal', 'Betsson', 'BetVictor', 'Betway',
    'BWin', 'CashPoint', 'CloudBet', 'Coral', 'DafaBet', 'HG', 'HKJC',
    'Intertops', 'Interwetten', 'Ladbrokes', 'Macauslot', 'MansionBet',
    'Marathonbet', 'MarsBet', 'MelBet',  'NitrogenSports',
    'PaddyPower', 'PinnacleSports', 'PlanetWin365', 'SBOBET', 'SkyBet',
    'TitanBet', 'UniBet', 'WilliamHill', 'YSB88']
lista_casas_dica = ['1XBet', 'Bet365', 'BetFair', 'BetVictor', 'Betway',
    'BWin', 'Marathonbet', 'PinnacleSports', 'WilliamHill']
    







dict_de_para_paises = {'AFGHANISTAN': 'Afeganistão',
 'ALBANIA': 'Albânia',
 'ALGERIA': 'Argélia',
 'ANDORRA': 'Andorra',
 'ANGOLA': 'Angola',
 'ARGENTINA': 'Argentina',
 'ARMENIA': 'Armênia',
 'AUSTRALIA': 'Austrália',
 'AUSTRIA': 'Áustria',
 'AZERBAIJAN': 'Azerbaijão',
 'BAHAMAS': 'Bahamas',
 'BAHRAIN': 'Barém',
 'BANGLADESH': 'Bangladesh',
 'BARBADOS': 'Barbados',
 'BELARUS': 'Belarus',
 'BELGIUM': 'Bélgica',
 'BELIZE': 'Belize',
 'BENIN': 'Benin',
 'BHUTAN': 'Butão',
 'BOLIVIA': 'Bolívia',
 'BOSNIA-HERZEGOVINA': 'Bósnia e Herzegovina',
 'BOTSWANA': 'Botsuana',
 'BRAZIL': 'Brasil',
 'BRUNEI': 'Brunei',
 'BULGARIA': 'Bulgária',
 'BURKINA': 'Burkina',
 'BURMA': 'Birmânia',
 'BURUNDI': 'Burundi',
 'CAMBODIA': 'Camboja',
 'CAMEROON': 'Camarões',
 'CANADA': 'Canadá',
 'CAPE VERDE ISLANDS': 'Ilhas de Cabo Verde',
 'CHAD': 'Chade',
 'CHILE': 'Chile',
 'CHINA': 'China',
 'COLOMBIA': 'Colômbia',
 'CONGO': 'República do Congo',
 'COSTA RICA': 'Costa Rica',
 'CROATIA': 'Croácia',
 'CUBA': 'Cuba',
 'CYPRUS': 'Chipre',
 'CZECH REPUBLIC': 'República Checa',
 'DENMARK': 'Dinamarca',
 'DJIBOUTI': 'Djibuti',
 'DOMINICA': 'Dominica',
 'DOMINICAN REPUBLIC': 'República Dominicana',
 'ECUADOR': 'Equador',
 'EGYPT': 'Egito',
 'EL SALVADOR': 'El Salvador',
 'ENGLAND': 'Inglaterra',
 'ERITREA': 'Eritréia',
 'ESTONIA': 'Estônia',
 'ETHIOPIA': 'Etiópia',
 'FIJI': 'Fiji',
 'FINLAND': 'Finlândia',
 'FRANCE': 'França',
 'GABON': 'Gabão',
 'GAMBIA': 'Gâmbia',
 'GEORGIA': 'Georgia',
 'GERMANY': 'Alemanha',
 'GHANA': 'Gana',
 'GREAT BRITAIN': 'Grã Bretanha',
 'GREECE': 'Grécia',
 'GRENADA': 'Grenada',
 'GUATEMALA': 'Guatemala',
 'GUINEA': 'Guiné',
 'GUYANA': 'Guiana',
 'HAITI': 'Haiti',
 'HOLLAND': 'Holanda',
 'HONDURAS': 'Honduras',
 'HUNGARY': 'Hungria',
 'ICELAND': 'Islândia',
 'INDIA': 'Índia',
 'INDONESIA': 'Indonésia',
 'IRAN': 'Irã',
 'IRAQ': 'Iraque',
 'IRELAND': 'Irlanda',
 'ISRAEL': 'Israel',
 'ITALY': 'Itália',
 'JAPAN': 'Japão',
 'JORDAN': 'Jordânia',
 'KAZAKHSTAN': 'Cazaquistão',
 'KENYA': 'Quênia',
 'KOREA': 'Coréia',
 'KUWAIT': 'Kuwait',
 'LAOS': 'Laos',
 'LATVIA': 'Letônia',
 'LEBANON': 'Líbano',
 'LIBERIA': 'Libéria',
 'LIBYA': 'Líbia',
 'LIECHTENSTEIN': 'Liechtenstein',
 'LITHUANIA': 'Lituânia',
 'LUXENBOURG': 'Luxemburgo',
 'MACEDONIA': 'Macedônia',
 'MADASGASCAR': 'Madasgascar',
 'MALAWI': 'Malawi',
 'MALAYSIA': 'Malásia',
 'MALI': 'Mali',
 'MALTA': 'Malta',
 'MALDIVES': 'Ilhas Maldivas',
 'MAURITANIA': 'Mauritânia',
 'MAURITIUS': 'Maurício',
 'MEXICO': 'México',
 'MOLDOVA': 'Moldávia',
 'MONACO': 'Mônaco',
 'MONGOLIA': 'Mongólia',
 'MONTENEGRO': 'Montenegro',
 'MOROCCO': 'Marrocos',
 'MOZAMBIQUE': 'Moçambique',
 'NAMIBIA': 'Namíbia',
 'NEW ZEALAND': 'Nova Zelândia',
 'NICARAGUA': 'Nicarágua',
 'NIGER': 'Níger',
 'NIGERIA': 'Nigéria',
 'NORTH KOREA': 'Coreia do Norte',
 'NORWAY': 'Noruega',
 'OMAN': 'Omã',
 'PAKISTAN': 'Paquistão',
 'PANAMA': 'Panamá',
 'PAPUA NEW GUINEA': 'Papua Nova Guiné',
 'PARAGUAY': 'Paraguai',
 'PERU': 'Peru',
 'PHILIPPINES': 'Filipinas',
 'POLAND': 'Polônia',
 'PORTUGAL': 'Portugal',
 'PUERTO RICO': 'Porto Rico',
 'QATAR': 'Catar',
 'ROMANIA': 'Romênia',
 'RUSSIA': 'Rússia',
 'RWANDA': 'Ruanda',
 'SAUDI ARABIA': 'Arábia Saudita',
 'SCOTLAND': 'Escócia',
 'SENEGAL': 'Senegal',
 'SERBIA': 'Sérvia',
 'SEYCHELLES': 'Seychelles',
 'SIERRA LEONE': 'Serra Leoa',
 'SINGAPORE': 'Cingapura',
 'SLOVAKIA': 'Eslováquia',
 'SLOVENIA': 'Eslovênia',
 'SOLOMON ISLANDS': 'Ilhas Salomão',
 'SOMALIA': 'Somália',
 'SOUTH AFRICA': 'África do Sul',
 'SOUTH KOREA': 'Coréia do Sul',
 'SPAIN': 'Espanha',
 'SRI LANKA': 'Sri Lanka',
 'SUDAN': 'Sudão',
 'SURINAME': 'Suriname',
 'SWAZILAND': 'Suazilândia',
 'SWEDEN': 'Suécia',
 'SWITZERLAND': 'Suíça',
 'SYRIA': 'Síria',
 'TAIWAN': 'Taiwan',
 'TANZANIA': 'Tanzânia',
 'THAILAND': 'Tailândia',
 'TOGO': 'Togo',
 'TRINIDAD AND TOBAGO': 'Trindade e Tobago',
 'TUNISIA': 'Tunísia',
 'TURKEY': 'Turquia',
 'TURKMENISTAN': 'Turcomenistão',
 'TUVALU': 'Tuvalu',
 'UGANDA': 'Uganda',
 'UKRAINE': 'Ucrânia',
 'UNITED ARAB EMIRATES': 'Emirados Árabes Unidos',
 'UNITED KINGDOM (UK)': 'Reino Unido',
 'UNITED STATES OF AMERICA (USA)': 'Estados Unidos da América (EUA)',
 'URUGUAY': 'Uruguai',
 'UZBEKISTAN': 'Uzbequistão',
 'VANUATU': 'Vanuatu',
 'VATICAN': 'Vaticano',
 'VENEZUELA': 'Venezuela',
 'VIETNAM': 'Vietnã',
 'WESTERN SAMOA': 'Samoa Ocidental',
 'YEMEN': 'Iémen',
 'YUGOSLAVIA': 'Jugoslávia',
 'ZAIRE': 'Zaire',
 'ZAMBIA': 'Zâmbia',
 'ZIMBABWE': 'Zimbábue',
 'WOMEN': 'Feminino',
 'U14': '',
 'U15': '',
 'U16': '',
 'U17': '',
 'U18': '',
 'U19': '',
 'U20': '',
 'U21': '',
 'U22': '',
 'U23': '',
 'UNITED': '',
 'UTD': ''}

 