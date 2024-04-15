
from Dominios import key_s3 as key, secret_s3 as secret
import s3fs
import io
import json
import pandas as pd
from datetime import  datetime
# HOJE_TEXTO = datetime.now().strftime("%Y%m%d")
# ano = HOJE_TEXTO[0:4]
# mes = HOJE_TEXTO[4:6]
# dia = HOJE_TEXTO[6:8]

def s3_upload_csv(df,path,file_name):
    """""Sumario

    Parametros:
    df(pandas DataFrame): tabela para subir no s3 como csv
    path (string) : caminho no s3
    file_name (string) : Nome do arquivo destino
    Retorno:
    Void
    """
    bytes_to_write = df.to_csv(None,index=False).encode()
    fs = s3fs.S3FileSystem(key=key, secret=secret)
    with fs.open(path + file_name, 'wb') as f:
        f.write(bytes_to_write)
        
def s3_upload_parquet(df,path,file_name):
    
    """""Sumario

    Parametros:
    df(pandas DataFrame): tabela para subir no s3 como parquet
    path (string) : caminho no s3
    file_name (string) : Nome do arquivo destino
    Retorno:
    Void
    """
    bytes_to_write = df.to_parquet(None,index=False,engine='fastparquet').encode()
    fs = s3fs.S3FileSystem(key=key, secret=secret)
    with fs.open(path + file_name, 'wb') as f:
        f.write(bytes_to_write)

def s3_upload_json(df,path,file_name):
    """""Sumario

    Parametros:
    df(pandas DataFrame): tabela para subir no s3 mo json
    path (string) : caminho no s3
    file_name (string) : Nome do arquivo destino
    Retorno:
    Void
    """
    bytes_to_write = df.to_json(orient='records').encode()
    fs = s3fs.S3FileSystem(key=key, secret=secret)
    with fs.open(path + file_name, 'wb') as f:
        f.write(bytes_to_write)

def s3_read_csv(path,file_name):
    """""Sumario

    Parametros:
    path (string) : caminho no s3
    file_name (string) : Nome do arquivo destino
    Retorno:
    Le o arquivo csv
    """
    fs = s3fs.S3FileSystem(key=key, secret=secret)
    with fs.open(path + file_name, 'rb') as f:
        data = f.read().decode()
    data = io.StringIO(data)
    return pd.read_csv(data, sep=",")

def s3_read_parquet(path,file_name):
    """""Sumario

    Parametros:
    path (string) : caminho no s3
    file_name (string) : Nome do arquivo destino
    Retorno:
    Le o arquivo parquet no s3
    """
    fs = s3fs.S3FileSystem(key=key, secret=secret)
    with fs.open(path + file_name, 'rb') as f:
        data = f.read().decode()
    data = io.StringIO(data)
    return pd.read_parquet(data, engine='fastparquet')

def s3_read_json(path,file_name):
    """""Sumario

    Parametros:
    path (string) : caminho no s3
    file_name (string) : Nome do arquivo destino
    Retorno:
    Le o arquivo json no s3
    """
    fs = s3fs.S3FileSystem(key=key, secret=secret)
    with fs.open(path + file_name, 'rb') as f:
        jsonObject = json.load(f)
        f.close()
    return jsonObject

def atualiza_bucket_s3(tabela_a_inserir, path, file_name):
    """""Sumario
    Parametros:
    tabela_a_inserir (pandas DataFrame) : Nome da tabela final que ficara no S3 bucket
    path (string) : Caminho da pasta do S3 bucket
    file_name (string) : Nome do Arquivo a ser atualizado no S3 bucket
    Retorno:
    Empilha sua base com a base do s3
    """

    df_atual = s3_read_csv(path,file_name)
    df_atual = df_atual.append(tabela_a_inserir).drop_duplicates(['id_jogo','away','home']).reset_index(drop= True)

    s3_upload_csv(df_atual,path,file_name)

def s3_list_files(path):
    """""Sumario

    Parametros:
    path (string) : caminho no s3
    Retorno:
    Lista os arquivos que estao no diretorio s3
    """
    fs = s3fs.S3FileSystem(key=key, secret=secret)
    lista = fs.ls(path)
    lista = [x.replace(path.replace('s3://',''),'') for x in lista]
    lista = [x.replace('.csv','') for x in lista]
    lista = [x.replace('.parquet','') for x in lista]
    lista = [x.replace('.json','') for x in lista]
    print(lista)
    lista= [i for i in lista if i != '']
    return lista
    
# def s3_list_files_full(path):
#     fs = s3fs.S3FileSystem(key=key, secret=secret)
#     lista = fs.ls(path)
#     return lista