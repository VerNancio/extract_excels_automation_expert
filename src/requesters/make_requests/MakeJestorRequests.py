import os
import msoffcrypto
import io
import shutil
import datetime as dt

import pandas as pd; from pandas import DataFrame, Series
import requests as req; from requests import Response
import json

from typing import Any

from ...helpers.tools.get_credentials import get_credentials



class MakeJestorRequests:

    client_name: str
    sender_email: str
    list_size: int = 500

    TABLE_HASH: str = 'q2ie0_wclkdcxb10ih77n'
    AUTH_TOKEN: dict
    HEADERS: dict


    def __init__(self, client_name: str):

        # if client_name not in ['workon', 'sulnorte', 'ofy', 'rip', 'fabitos']:
            # raise ValueError('Parâmetro "client_name" não informado corretamente')
        
        self.client_name = client_name
            
        self.download_dir_path = f"./data/{client_name}/"
        self.download_temp_dir_path = os.path.join(self.download_dir_path, 'temp')

        os.makedirs(self.download_dir_path, exist_ok=True)
        print(f"Pasta de downloads garantida em: {self.download_dir_path}")


        self.AUTH_TOKEN = get_credentials('jestor')['auth_token']

        self.HEADERS = {
            "Authorization": f"Bearer {self.AUTH_TOKEN}",
            "accept": "application/json",
            "content-type": "application/json"
        }

        # os.makedirs(self.download_temp_dir_path, exist_ok=True)
        # print(f"Pasta de download temporária garantida em: {self.download_temp_dir_path}")


    def run(
            self,
            row_post_date: str = dt.date.today().strftime('%Y-%m-%d')
            # list_size: int = 300,
            ) -> DataFrame | None:
        
        if self.client_name == 'fabitos':
            df = self.table_get_request()
            print('---------------', len(df))
            # if df is not None:
                # self.fabito_check_request(df['name'].copy().to_list())
                # df.to_excel('a.xlsx')
            # else:
                # return None
            
        else:
            emails: dict[str, str] = {
                'workon': 'afastamento@workongroup.com.br', 
                'sulnorte': '', 
                'ofy': '', 
                'rip': ''
            }
            
            self.sender_email = emails[self.client_name]
            self.row_post_date = row_post_date
        
            df = self.download_and_save_xlsx_file() 

        return df


    def assure_temp_diretory_exists_empty(self) -> None:

        # Deleta tudo que está no diretório de arquivos temporários
        shutil.rmtree(self.download_temp_dir_path, ignore_errors=True) 

        # Cria a pasta no caminho
        os.makedirs(self.download_temp_dir_path, exist_ok=True)

        print(f"Pasta de download temporária garantida em: {self.download_temp_dir_path}")
        
    
    def table_get_request(self) -> DataFrame | None:
        """_Recolhe da tabela dos atestados da Fabitos todos os registros \
            aprovados e que não foram coletados ainda_

        Returns:
            DataFrame | None: _Dataframe com todos os registros da tabela necessários_
        """
        
        last_path = 'list'
        URL = f"https://expertocupacional.api.jestor.com/object/{last_path}"

        payload = {
            "object_type":"e930f73a_ddac1f78__1k230gj1x6hfkgpfpbik",
            "size": self.list_size,
            "nested_type": "onlyrefs",
            "filters": [
                    {"field": "fase","type":"list", "operator":"in", "value":"Aprovado"},
                    {"field": "ja_feita_a_coleta", "type":"boolean", "value":"0"},

                    # 220 == cod. da fabitos -> ter que fazer um dict p/ clientes da tabela
                    {"field": "clientes_expert","type":"list", "operator": "in", "value":"220"}
            ],
            "token":"cc0da72ab3741491dec8f2daf2a95bba"
        }


        res: Response = req.post(URL, headers=self.HEADERS, json=payload)
        
        # Se houver algum erro na requisição
        if res.status_code != 200:
            print(f"\nErro na requisição: {res.status_code}")
            return res.text
        
        res_json: dict = res.json()
        data = res_json['data']

        all_rows: list[dict] = data['items']
        df: DataFrame = pd.json_normalize(all_rows)
        
        print(df.columns)        
        print(df)
        
        if df.empty:
            return None

        return df
        
        
    def fabito_check_request(self, ids_list: list[str]) -> None:
        """_Atualiza os registros que foram coletados no Jestor pra constarem como tal_

        Args:
            ids (Series[str]): _ids dos registros coletados da tabela_
        """
        
        
        URL = 'https://expertocupacional.api.jestor.com/object/update'

        print(f'Número total de registros que foram coletados e que vão ser sinalizados como tal: {len(ids_list)}\n')
        
        for i, id in enumerate(ids_list):
            print('id: ', id)
            
            
            AUTH_TOKEN = 'MTkxNDdmOTMzMzE4MzY16d87e0a03cMTczODYzMTI3MTg3ZGI5'
            HEADERS = {
                    "Authorization": f"Bearer {AUTH_TOKEN}",
                    "accept": "application/json",
                    "content-type": "application/json"
            }
            PAYLOAD = {
                "object_type": 'e930f73a_ddac1f78__1k230gj1x6hfkgpfpbik',
                "data": {
                    f'id_e930f73a_ddac1f78__1k230gj1x6hfkgpfpbik': id,
                    'ja_feita_a_coleta': True
                },
            }

            res = req.post(URL, headers=HEADERS, json=PAYLOAD)
            res_json = res.json()
        
            print(f'Realizado update Nº{i + 1} do registro de ID {id}')
            

    def decrypt_xlsx(self, file_pw: str, content: bytes | Any):

        file_like = io.BytesIO(content)

        try:
            office_file = msoffcrypto.OfficeFile(file_like)
            office_file.load_key(password=file_pw)

            decrypted = io.BytesIO()
            office_file.decrypt(decrypted)

            decrypted_file = io.BytesIO()
            office_file.decrypt(decrypted_file)

            decrypted_file.seek(0)
            
            return decrypted_file
        
        except msoffcrypto.exceptions.DecryptionError:
            print(f"Arquivo não está criptografado...")
            file_like.seek(0)
            return file_like


    def download_and_save_xlsx_file(self) -> DataFrame | None:
        
        last_path = 'list'
        URL = f"https://expertocupacional.api.jestor.com/object/{last_path}"

        filters = [
            {"field":"email_solicitante", "type":"string", "operator":"Exatamente igual", "value": self.sender_email},
            {"field":"jestor_is_draft", "type":"list", "operator":"in", "value":"0,1"}
        ]


        payload = {
            "object_type": self.TABLE_HASH,
            "size": self.list_size,
            "select": [
                "anexos",
                "senhacodigochave_de_arquivo",
                "data_de_criacao",
                "classificacao"
            ],
            "filters": {
                "filters": filters
            }
        }


        res: Response = req.post(URL, headers=self.HEADERS, json=payload)

        # Se houver algum erro na requisição
        if res.status_code != 200:
            print(f"\nErro na requisição: {res.status_code}")
            return res.text
        
        res_json: dict = res.json()
        data = res_json['data']

        all_rows: list[dict] = data['items']

        self.assure_temp_diretory_exists_empty()

        df: DataFrame = None 
        for row in all_rows[:]:

            file_pw: str = row['senhacodigochave_de_arquivo']
            row_attachments_dict: dict = json.loads(row['anexos'])[0]

            row_send_datetime: dt.datetime = dt.datetime.strptime(row['data_de_criacao'][:10], '%Y-%m-%d')
            row_send_date: str = row_send_datetime.strftime('%d/%m/%Y')

            category: str = row.get('classificacao')
            

            # Temporario pra filtrar excluindo as modelos I
            # print(category, category == 'Modelo I')
            if category == 'Modelo I':
                continue

            # Temporario pra filtrar pela data buscada
            if row_send_date != self.row_post_date:
                continue

            print(row['data_de_criacao'])
            xlsx_url_path: str = row_attachments_dict['file']
            download_xlsx_url = f'https://files.jestor.com/expertocupacional/{xlsx_url_path}'

            response: Response = req.get(download_xlsx_url, allow_redirects=True)

            if response.status_code == 200:

                decrypted_file: io.BytesIO = self.decrypt_xlsx(file_pw=file_pw, content=response.content)

                df: DataFrame = pd.read_excel(decrypted_file, engine="openpyxl")
                # print(df)

                file_path: str = os.path.join(self.download_temp_dir_path, f"{row_attachments_dict['name']} ... {row_send_date.replace('/', '-')}")
                open(f'{file_path}.xlsx','wb').write(response.content)
                df.to_excel(f'{file_path}.xlsx')

        if df is None:
            print("\nAtenção: Nenhum registro foi encontrado com as datas ou demais características procuradas.\n")
            return None
        
        return df


