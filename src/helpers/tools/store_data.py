import os
from pandas import DataFrame
import pandas as pd
import numpy as np
import requests as req

from .date_formatter import DateFormatter
from src.helpers.tools.scrape_all_rows_jestor import scrape_all_rows_jestor

from typing import Literal

from src.constants import (
    JESTOR_ABSENTEISM_TABLE_HASH,
    CLIENT_IDS_JESTOR,
    # ONEDRIVE_PATH 
)


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
        should_store_where: Literal['local', 'onedrive', 'both', 'jestor'] = 'local',
        auth_token: str = None,
        ) -> tuple[int, bool]:
        """
        Salva o arquivo excel com os atestados no diretório data/<client_name> e no Onedrive também

        Args:
            df (Dataframe): dataframe com os dados de obtidos
            client_name (str): nome do cliente dos quais os dados dos atestados pertencem
            date (str): string de data que será usada no nome do xlsx salvo 
            date_in_name (bool): booleano que define se a data no nome do arquivo deve ser a data
                                    da variável date ou não
            report_type (str): string de tipo de de dados, se são atestados de horas ou de dias
            
        Returns:
            tuple[int, bool]: _Total de registros salvos (int) e se todos os registros foram salvos ou não (bool)_
        """
        
        result: int
        match (should_store_where):
            case 'onedrive':
                total_rows_created, all_rows_were_stored = StoreData.store_in_onedrive(df=df, client_name=client_name,
                                        folder_name=folder_name,
                                        date=date, date_in_name=date_in_name, 
                                        report_type=report_type)
            case 'local':
                total_rows_created, all_rows_were_stored = StoreData.store_in_local_dir(df=df, client_name=client_name,
                                        folder_name=folder_name,
                                        date=date, date_in_name=date_in_name, 
                                        report_type=report_type)
            case 'jestor':
                total_rows_created, all_rows_were_stored = StoreData.store_in_jestor(df=df, client_name=client_name,
                                        # folder_name=folder_name,
                                        # date=date, date_in_name=date_in_name, 
                                        # report_type=report_type, 
                                        auth_token=auth_token)
                
            # case 'both':
            #     StoreData.store_in_both(df=df, client_name=client_name,
            #                             folder_name=folder_name,
            #                             date=date, date_in_name=date_in_name, 
            #                             report_type=report_type)
            
            
            
        return total_rows_created, all_rows_were_stored


    # @staticmethod
    # def store_in_both(
    #     df: DataFrame, 
    #     client_name: str, 
    #     folder_name: str,
    #     date: str = None, 
    #     date_in_name: bool = False, 
    #     ) -> None:
    #     """
    #     Salva o arquivo excel com os atestados no diretório data/<client_name> e no Onedrive também

    #     Args:
    #         df (Dataframe): dataframe com os dados de obtidos
    #         client_name (str): nome do cliente dos quais os dados dos atestados pertencem
    #         date (str): string de data que será usada no nome do xlsx salvo 
    #         date_in_name (bool): booleano que define se a data no nome do arquivo deve ser a data
    #                              a da variável date ou não
    #     """

    #     StoreData.store_in_onedrive(df=df, client_name=client_name,
    #                                   folder_name=folder_name,
    #                                   date=date, date_in_name=date_in_name, 
    #                                  )
        
    #     StoreData.store_in_onedrive(df=df, client_name=client_name,
    #                                   folder_name=folder_name,
    #                                   date=date, date_in_name=date_in_name, 
    #                                  )


    @staticmethod
    def store_in_local_dir(
        df: DataFrame, 
        client_name: str, 
        folder_name: str,
        date: str = None, 
        date_in_name: bool = False, 
        report_type: str = None
    ) -> tuple[int, bool]:
        """
        Salva o arquivo excel com os atestados no diretório data/<client_name>

        Args:
            df (Dataframe): dataframe com os dados de obtidos
            client_name (str): nome do cliente dos quais os dados dos atestados pertencem
            date (str): string de data que será usada no nome do xlsx salvo 
            date_in_name (bool): booleano que define se a data no nome do arquivo deve ser a data
                                 a da variável date ou não
            report_type (str): string de tipo de de dados, se são atestados de horas ou de dias
            
        Returns:
            int: _Total de registros salvos_
        """
        
        len_df: int = len(df)

        date_formatter = DateFormatter()
        if date_in_name:
            date_to_save = date_formatter.format_date(date, current_format='dmy', new_format='iso')
        else:
            date_to_save = DateFormatter(default_format='iso').today()

        filename = f'ATESTADOS_{client_name.upper()}_{f'HORAS_' if report_type == 'hour' else ''}{date_to_save} - rpa.xlsx'
        file_path = os.path.join('data', folder_name, filename)
                    
        df.to_excel(file_path, index=False, sheet_name='atestados')
        
        total_rows_created: int = len_df
        all_rows_were_stored: bool = True
        
        return total_rows_created, all_rows_were_stored


    @staticmethod
    def store_in_onedrive(
        df: DataFrame, 
        client_name: str, 
        folder_name: str,
        date: str = None, 
        date_in_name: bool = False, 
        report_type: str = None
    ) -> tuple[int, bool]:
        """
        Salva o arquivo excel com os atestados no Onedrive

        Args:
            df (Dataframe): dataframe com os dados de obtidos
            client_name (str): nome do cliente dos quais os dados dos atestados pertencem
            date (str): string de data que será usada no nome do xlsx salvo 
            date_in_name (bool): booleano que define se a data no nome do arquivo deve ser a data
                                 a da variável date ou não
            report_type (str): string de tipo de de dados, se são atestados de horas ou de dias
            
        Returns:
            int: _Total de registros salvos_
        """
        
        len_df: int = len(df)

        date_formatter = DateFormatter()
        if date_in_name:
            date_to_save = date_formatter.format_date(date, current_format='dmy', new_format='iso')
        else:
            date_to_save = DateFormatter(default_format='iso').today()

        # sharepoint_path = os.path.join(os.environ['USERPROFIE'], 'EXPERT GESTAO OCUPACIONAL E PREVIDENCIARIA LTDA', 'Expert Ocupacional Externo - SmartReports')
        dir_path = os.path.join(ONEDRIVE_PATH, folder_name, 'Extração Automatizada')
        filename = f'ATESTADOS_{client_name.upper()}_{f'HORAS_' if report_type == 'hour' else ''}{date_to_save} - rpa.xlsx'
        file_path = os.path.join(dir_path, filename)
        
        df.to_excel(file_path, index=False, sheet_name='atestados')
        
        total_rows_created: int = len_df
        all_rows_were_stored: bool = True
                
        return total_rows_created, all_rows_were_stored


    @staticmethod
    def store_in_jestor(
        df: DataFrame,
        client_name: str,
        table_hash: str = JESTOR_ABSENTEISM_TABLE_HASH,
        auth_token: str = None
    ) -> tuple[int, bool]:
        """_summary_

        Args:
            df (DataFrame): _DataFrame com todos os registros extraídos_
            client_name (str): _Nome da empresa cliente_
            table_hash (str, optional): _Hash da tabela do Jestor onde os dados serão salvos_. Default: JESTOR_ABSENTEISM_TABLE_HASH.
            auth_token (str, optional): _Token de autenticação de envio ao Jestor_. Defaults: None.

        Returns:
            int: _Total de registros salvos_
        """
        
        client_id: str = CLIENT_IDS_JESTOR[client_name]

        # ======================================================
        # BUSCAR REGISTROS JÁ EXISTENTES
        # ======================================================
        all_rows_clients_list = scrape_all_rows_jestor(
            table_hash=table_hash,
            token=auth_token,
            filters=[
                {
                    "field": "clientes_expert",
                    "operator": "in",
                    "value": client_id
                }
            ],
            select=[],
            page_size=1000
        )

        df_all_rows_clients = pd.DataFrame(all_rows_clients_list)

        if not df_all_rows_clients.empty:
            df_all_rows_clients["data_inicial"] = (
                pd.to_datetime(
                    df_all_rows_clients["data_inicial"],
                    format="%Y-%m-%d"
                )
                .dt.strftime("%d/%m/%Y")
            )

        # ======================================================
        # PADRONIZAÇÃO DOS DADOS
        # ======================================================
        rename_map = {
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
        }
        
        
        df_renamed = df.rename(columns=rename_map)
        print(df_renamed.columns)
        print(df_all_rows_clients.columns)

        # Se não houver linhas no Jestor, retorna igual, pois não tem como haver duplicadas
        if df_all_rows_clients.empty:
            df_without_dups = df_renamed
        
        else:
            df_merged = (
                df_renamed
                .merge(
                    df_all_rows_clients[["cpf_1", "data_inicial"]],
                    on=["cpf_1", "data_inicial"],
                    how="left",
                    indicator=True
                ).copy()
            )
            
            df_without_dups = df_merged[df_merged["_merge"] == "left_only"].drop(columns="_merge")
        
        
        total_rows_extracted: int = len(df)
        total_rows_to_save: int = len(df_without_dups)
        total_rows_already_saved: int = total_rows_extracted - total_rows_to_save
        
        # Mantém apenas registros ainda não existentes
        df_treated = (
            df_without_dups
            .map(lambda x: x.upper() if isinstance(x, str) else x)
            .replace({np.nan: None})
        )
        
        print(f'Quantidade dos registros que já estão armazenados: [{total_rows_already_saved}/{total_rows_extracted}]')
        print(f'Quantidade de registros que ainda não estão armazenados: [{total_rows_to_save}/{total_rows_extracted}]\n')
        
        if total_rows_to_save == 0:
            print("Nenhum novo registro encontrado para envio.")
            return total_rows_to_save, True

        # ======================================================
        # CAMPOS ADICIONAIS
        # ======================================================
        df_treated["clientes_expert"] = client_id
        df_treated["fase"] = "Aprovado"
        
        # Redução do DF pra testar com poucos registros, caso seja necessário
        df_treated = df_treated.head(2)

        # ======================================================
        # CONFIGURAÇÃO DA API
        # ======================================================
        url = "https://expertocupacional.api.jestor.com/object/create"

        headers: dict = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {auth_token}",
        }

        print(f'\nIniciando envio de {total_rows_to_save} registros para a tabela "{table_hash}" (Jestor).\n')

        # ======================================================
        # ENVIO DOS REGISTROS
        # ======================================================
        
        total_rows_created = 0
        for index, (_, row) in enumerate(df_treated.iterrows(), start=1):

            cpf = row["cpf_1"]

            print(f'Enviando registro do colaborador de CPF "{cpf}" [{index}/{total_rows_to_save}]')

            payload = {
                "object_type": table_hash,
                "data": {
                    key: None if pd.isna(value) else value
                    for key, value in row.items()
                }
            }

            for tentativa in range(1, 4):
                try:
                    response = req.post(url,json=payload,headers=headers)
                    created_row_id = response.json().get("data", {}).get(f"id_{table_hash}")

                    if response.ok and created_row_id:
                        print(f"Registro criado com sucesso. ID: {created_row_id}\n")
                        total_rows_created += 1
                        break

                    print(f"Erro ao criar registro (tentativa {tentativa}/3)\nStatus: {response.status_code}\nResposta: {response.text}\n")

                except Exception as e:
                    print(f"Erro na tentativa {tentativa}/3 para CPF {cpf}: {e}")

                    if tentativa == 3:
                        print("Falha após 3 tentativas. Prosseguindo para o próximo registro.\n")
            
        # Variável que informa se todas as linhas foram salvas com sucesso no Jestor 
        all_rows_were_stored: bool
        if total_rows_created < len(df_treated):
            all_rows_were_stored = False
        else:
            all_rows_were_stored = True
            
        return total_rows_created, all_rows_were_stored