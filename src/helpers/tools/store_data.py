import os
from pandas import DataFrame
import pandas as pd
import numpy as np
import requests as req

from .date_formatter import DateFormatter

from typing import Literal

from src.constants import JESTOR_ABSENTEISM_TABLE_HASH
from src.constants import CLIENT_IDS_JESTOR


class StoreData:
    """
    Classe montada para abstrair código da main, serve para salvar os dados de atestados obtidos.

    As funções estáticas servem para salvar ou localmente o arquivo ou no Onedrive.
    """

    def storage_data(
        self,
        df: DataFrame, 
        client_name: str, 
        folder_name: str,
        date: str = None, 
        date_in_name: bool = False, 
        report_type: str = None,
        should_store_where: Literal['local', 'onedrive', 'both', 'jestor'] = 'local'
        ) -> bool:
        """
        Salva o arquivo excel com os atestados no diretório data/<client_name> e no Onedrive também

        Args:
            df (Dataframe): dataframe com os dados de obtidos
            client_name (str): nome do cliente dos quais os dados dos atestados pertencem
            date (str): string de data que será usada no nome do xlsx salvo 
            date_in_name (bool): booleano que define se a data no nome do arquivo deve ser a data
                                    da variável date ou não
            report_type (str): string de tipo de de dados, se são atestados de horas ou de dias
        """

        match (should_store_where):
            case 'onedrive':
                StoreData.store_in_onedrive(df=df, client_name=client_name,
                                        folder_name=folder_name,
                                        date=date, date_in_name=date_in_name, 
                                        report_type=report_type)
            case 'local':
                StoreData.store_in_local_dir(df=df, client_name=client_name,
                                        folder_name=folder_name,
                                        date=date, date_in_name=date_in_name, 
                                        report_type=report_type)
            case 'both':
                StoreData.store_in_both(df=df, client_name=client_name,
                                        folder_name=folder_name,
                                        date=date, date_in_name=date_in_name, 
                                        report_type=report_type)
            case 'jestor':
                StoreData.store_in_jestor(df=df, client_name=client_name,
                                        # folder_name=folder_name,
                                        # date=date, date_in_name=date_in_name, 
                                        report_type=report_type)

        return True


    @staticmethod
    def store_in_both(
        df: DataFrame, 
        client_name: str, 
        folder_name: str,
        date: str = None, 
        date_in_name: bool = False, 
        ) -> None:
        """
        Salva o arquivo excel com os atestados no diretório data/<client_name> e no Onedrive também

        Args:
            df (Dataframe): dataframe com os dados de obtidos
            client_name (str): nome do cliente dos quais os dados dos atestados pertencem
            date (str): string de data que será usada no nome do xlsx salvo 
            date_in_name (bool): booleano que define se a data no nome do arquivo deve ser a data
                                 a da variável date ou não
        """

        StoreData.store_in_onedrive(df=df, client_name=client_name,
                                      folder_name=folder_name,
                                      date=date, date_in_name=date_in_name, 
                                     )
        
        StoreData.store_in_onedrive(df=df, client_name=client_name,
                                      folder_name=folder_name,
                                      date=date, date_in_name=date_in_name, 
                                     )


    @staticmethod
    def store_in_local_dir(
        df: DataFrame, 
        client_name: str, 
        folder_name: str,
        date: str = None, 
        date_in_name: bool = False, 
        report_type: str = None
    ) -> None:
        """
        Salva o arquivo excel com os atestados no diretório data/<client_name>

        Args:
            df (Dataframe): dataframe com os dados de obtidos
            client_name (str): nome do cliente dos quais os dados dos atestados pertencem
            date (str): string de data que será usada no nome do xlsx salvo 
            date_in_name (bool): booleano que define se a data no nome do arquivo deve ser a data
                                 a da variável date ou não
            report_type (str): string de tipo de de dados, se são atestados de horas ou de dias
        """

        date_formatter = DateFormatter()
        if date_in_name:
            date_to_save = date_formatter.format_date(date, current_format='dmy', new_format='iso')
        else:
            date_to_save = DateFormatter(default_format='iso').today()
            

        filename = f'ATESTADOS_{client_name.upper()}_{f'HORAS_' if report_type == 'hour' else ''}{date_to_save} - rpa.xlsx'
        file_path = os.path.join('data', folder_name, filename)
                    
        df.to_excel(file_path, index=False, sheet_name='atestados')

        print(f'{date_to_save}: {df.shape[0]} registros salvos no diretório local do projeto...')


    @staticmethod
    def store_in_onedrive(
        df: DataFrame, 
        client_name: str, 
        folder_name: str,
        date: str = None, 
        date_in_name: bool = False, 
        report_type: str = None
    ) -> None:
        """
        Salva o arquivo excel com os atestados no Onedrive

        Args:
            df (Dataframe): dataframe com os dados de obtidos
            client_name (str): nome do cliente dos quais os dados dos atestados pertencem
            date (str): string de data que será usada no nome do xlsx salvo 
            date_in_name (bool): booleano que define se a data no nome do arquivo deve ser a data
                                 a da variável date ou não
            report_type (str): string de tipo de de dados, se são atestados de horas ou de dias
        """

        date_formatter = DateFormatter()
        if date_in_name:
            date_to_save = date_formatter.format_date(date, current_format='dmy', new_format='iso')
        else:
            date_to_save = DateFormatter(default_format='iso').today()

        # onedrive_path = os.path.join(os.environ['USERPROFILE'], 'OneDrive - EXPERT GESTAO OCUPACIONAL E PREVIDENCIARIA LTDA')
        # filename = f'ATESTADOS_{client_name.upper()}_{f'HORAS_' if report_type == 'hour' else ''}{date_to_save}.xlsx'

        file_path = os.path.join(dir_path, filename)
        print(file_path)
        df.to_excel(file_path, index=False, sheet_name='atestados')

        # dir_path = os.path.join(onedrive_path, 'SmartReports', client_name.lower())
        # filename = f'ATESTADOS_{client_name.upper()}_{f'HORAS_' if report_type == 'hour' else ''}{date_to_save}.xlsx'

        sharepoint_path = os.path.join(os.environ['USERPROFILE'], 'EXPERT GESTAO OCUPACIONAL E PREVIDENCIARIA LTDA', 'Expert Ocupacional Externo - SmartReports')
        dir_path = os.path.join(sharepoint_path, folder_name, 'Extração Automatizada')

        filename = f'ATESTADOS_{client_name.upper()}_{f'HORAS_' if report_type == 'hour' else ''}{date_to_save} - rpa.xlsx'

        file_path = os.path.join(dir_path, filename)
        df.to_excel(file_path, index=False, sheet_name='atestados')

        print(f'{date_to_save}: {df.shape[0]} registros salvos no diretório do Onedrive...')


    @staticmethod
    def store_in_jestor(
        df: DataFrame, 
        client_name: str, 
        table_hash: str = JESTOR_ABSENTEISM_TABLE_HASH,
        # folder_name: str,
        # date: str = None, 
        # date_in_name: bool = False, 
        report_type: str = None
    ) -> None:
        """
        Salva os dados de atestados no Onedrive, no Jestor por meio de requisições POST

        Args:
            df (Dataframe): dataframe com os dados de obtidos
            client_name (str): nome do cliente dos quais os dados dos atestados pertencem
            date (str): string de data que será usada no nome do xlsx salvo 
            date_in_name (bool): booleano que define se a data no nome do arquivo deve ser a data
                                 a da variável date ou não
            report_type (str): string de tipo de de dados, se são atestados de horas ou de dias
        """
        
        
        df = df.rename(columns={
            
            "local": "nome_unidade_colaborador",
            "criado_em": "criado_em",
            "data_inicio": "data_inicial",
            "data_retorno": "data_final",
            "cids": "cid_1",
            "identificador_prestador": "crm",
            "nome_prestador": "medico",
            "nome_funcionario": "nome_colaborador_1",
            "cpf": "cpf_1",
            "hora_inicio": "hora_inicio",
            "hora_fim": "hora_fim",
            "tipo": "tipo_de_atestado",
            "tipo_prestador": "conselho",
        })
        df = df.map(lambda x: x.upper() if isinstance(x, str) else x)
        df = df.replace({np.nan: None})
        df['clientes_expert'] = CLIENT_IDS_JESTOR[client_name]
        df['fase'] = 'Aprovado'
        
        # teste = True if os.environ.get('ENVIRONMENT') == 'TESTE' else False
        
        # Remover quando entrar em produção
        df['ambiente_teste'] = True
        
        # Remover quando entrar em produção - teste em escala menor
        df = df[:3]
        
        # return
        
        print(f'\nIniciando envio dos registros pra tabela "{table_hash}" (Jestor):\n')
        
        url = 'https://expertocupacional.api.jestor.com/object/create'
        
        for index, (_, row) in enumerate(df.iterrows()):
            
            print(f'Enviando registro do colaborador de cpf: "{row["cpf_1"]}" [{index + 1}/{df.shape[0]}]')
            
            for tentativa in range(1, 4):
                try:
                    payload = {
                        "object_type": table_hash,
                        "data": {
                            key: (None if pd.isna(value) else value)
                            for key, value in row.items()
                        }
                    }
                    
                    # print(f'Payload: {payload}\n')
                    
                    headers = {
                        "accept": "application/json",
                        "content-type": "application/json",
                        "Authorization": "Bearer YWM2Y2VmMzAyMmZjNWI39259c9190fMTc4MzEwMTE1MTA3ZjBj"
                    }
                    
                    response = req.post(url, json=payload, headers=headers)
                    
                    # id_e930f73a_ddac1f78__1k230gj1x6hfkgpfpbik
                    created_row_id = response.json().get('data', {}).get(f'id_{table_hash}', None)
                    
                    if created_row_id:
                        print(f'Registro criado com sucesso, id: {created_row_id}\n')
                        break  # Sai do loop de tentativas se a requisição for bem-sucedida
                    else:
                        print(f'Erro ao criar registro, status code: {response.status_code}, response: {response.text}\n')
                
                except Exception as e:
                    print(f'Erro na tentativa {tentativa} ao enviar registro: {e}')
                    if tentativa == 3:
                        print('Falha após 3 tentativas. Continuando para o próximo registro.\n')
            
            
            
            
            # payload = {
            #     "object_type": table_hash,
            #     "data": {
            #         key: (None if pd.isna(value) else value)
            #         for key, value in row.items()
            #     }
            # }
            
            # print(f'Payload: {payload}\n')
            
            # headers = {
            #     "accept": "application/json",
            #     "content-type": "application/json",
            #     "Authorization": "Bearer YWM2Y2VmMzAyMmZjNWI39259c9190fMTc4MzEwMTE1MTA3ZjBj"
            # }
            
            # response = req.post(url, json=payload, headers=headers)
            
            # # id_e930f73a_ddac1f78__1k230gj1x6hfkgpfpbik
            # created_row_id = response.json().get('data', {}).get(f'id_{table_hash}', None)
            
            # if created_row_id:
            #     print(f'Registro criado com sucesso, id: {created_row_id}\n')
            # else:
            #     print(f'Erro ao criar registro, status code: {response.status_code}, response: {response.text}\n')
