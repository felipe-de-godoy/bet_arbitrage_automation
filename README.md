# valuebets_api

Pasta dicas contem as funcoes de consumo de api de dados, do sql server, do telegram e funcoes geradoras de dicas e de tratamento

Para instalar no lambda basta instalar os pacotes necessarios do python num terminal linux, e então zipar a pasta
https://docs.aws.amazon.com/pt_br/lambda/latest/dg/python-package.html
Estou armazenando o historico de pacotes de implantação em s3://magic-bet-raw/PacotesImplantacao/

Requisitos para tudo funcionar corretamente:

Inicializar uma pasta e rodar: 

pip3 install --target ./package pandas==1.2.4  --upgrade
pip3 install --target ./package numpy==1.19.5 --upgrade
pip3 install --target ./package s3fs==2021.08.0  --upgrade
pip3 install --target ./package requests==2.25.1  --upgrade
pip3 install --target ./package pyTelegramBotAPI  --upgrade

cd package
cole os codigos da pasta dicas, e rode abaixo
zip -r ../Pacote_Magic_Bet_Lambda_V0.zip .
cd ..
zip -g Pacote_Magic_Bet_Lambda_V0.zip lambda_funcao.py
"# bet_arbitrage_automation" 
