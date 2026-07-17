import os
from urllib.request import urlretrieve
import requests as req; from requests import Response
import datetime as dt
import shutil
import json

import pandas as pd; from pandas import DataFrame, Series

from ...helpers.tools.date_formatter import DateFormatter
from ...helpers.tools.get_credentials import get_credentials


class MakeSocRequests:
    
    def __init__(self, client_name: str):
        self.client_name = client_name

    
    def filter_by_dates(self, df: DataFrame, start_date: str, end_date: str) -> DataFrame:
        date_formatter = DateFormatter()
        
        start_date_dt = date_formatter.to_datetime(start_date)
        end_date_dt = date_formatter.to_datetime(end_date)
        
        # print(df.columns)
        
        filtered_df = df[
                (pd.to_datetime(df['DATADECRIACAO'], format='%d/%m/%Y') >= start_date_dt) & 
                (pd.to_datetime(df['DATADECRIACAO'], format='%d/%m/%Y') <= end_date_dt)
            ]
        
        return filtered_df
    
    
    def get_colabs_names_by_cpfs(self, client_id: str, cpfs: list) -> list:
        # https://ws1.soc.com.br/WebSoc/exportadados?parametro={"empresa": "388105", "codigo": "185170", "chave": "24920146325a31c7fa94", "tipoSaida": "json", "empresaTrabalho": "592279", "cpf": "00033834660", "parametroData": "", "dataInicio": "", "dataFim": ""}
        
        url = "https://ws1.soc.com.br/WebSoc/exportadados"
        
        print('Iniciando busca dos nomes dos colaboradores pelos CPFs:\n')
        
        colab_names: list = []
        for idx, cpf in enumerate(cpfs):
            print(f"Buscando dados do colaborador de cpf: {cpf} [{idx + 1}/{len(cpfs)}]")
            
            params = {
                "empresa": "388105", 
                "codigo": "185170", 
                "chave": "24920146325a31c7fa94", 
                "tipoSaida": "json",
                "empresaTrabalho": client_id,
                "cpf": cpf,
                "parametroData": "",
                "dataInicio": "", 
                "dataFim": ""
            }
        
            res = req.post(url=url, params={"parametro": json.dumps(params)})
            
            try:
                # print('\n\n' + res.text)
                res_jsoned = res.json()[0]
                colab_name = res_jsoned.get('NOME', '')
                colab_names.append(colab_name)
                
            except json.JSONDecodeError:
                print(f"Erro ao decodificar JSON para o CPF {cpf}")
                colab_names.append('')
                
        return colab_names


    def request_data(self, start_date: str, end_date: str) -> DataFrame | None:
        
        date_formatter = DateFormatter()

        end_date_filter = date_formatter.today()
        start_date_filter = date_formatter.days_ago(days=180)
        
        client_soc_ids: list[str]
        match self.client_name:
            case 'leroy': client_soc_ids = ['1223067']
            case 'pluri': client_soc_ids = ['592252']
            case 'viva': client_soc_ids = ['592278', '592279']

        url = "https://ws1.soc.com.br/WebSoc/exportadados"

        response_json_list: list[dict] = []
        for client_id in client_soc_ids:
            params = {
                "empresa": client_id,
                "codigo": "29348",
                "chave": "e0c5e1ec4799939504e6",
                "tipoSaida": "json",
                "dataInicial": start_date_filter,
                "dataFinal": end_date_filter,
            }
            
            res = req.post(url, params={"parametro": json.dumps(params)})
            # print('response status code:', res.text)
            # while 1:...
            
            try:
                response_json_list.append(res.json())
            except json.JSONDecodeError:
                print(f"Erro ao decodificar JSON para o cliente {client_id}")
                response_json_list.append({})
        
        if res.status_code == 200:
            print(f"Dados buscados com sucesso para do período de {start_date_filter} a {end_date_filter}\n")
        else:
            print(f"Erro ao buscar os dados do o período de {start_date_filter} a {end_date_filter}: {res.status_code}\n")
            
        df = pd.concat(
            [pd.DataFrame(res_json) for res_json in response_json_list],
            ignore_index=True
        )
        
        # Não é necessário, low-code de reinserir cpf já pega e setta os nomes automaticamente
        # if not df.empty:
        #    df['nome_funcionario'] = self.get_colabs_names_by_cpfs(client_id=client_id, cpfs=df['CPF'].tolist())
        
        # df.to_excel(f"{self.client_name}_soc_data.xlsx", index=False)
        
        df = self.filter_by_dates(df, start_date=start_date, end_date=end_date)

        return df

