import os
from urllib.request import urlretrieve
import requests as req; from requests import Response
import datetime as dt
import shutil

from pandas import read_excel, DataFrame

from helpers.tools.date_formatter import DateFormatter


class MakeCloseRequests:

    
    @staticmethod
    def get_bearer_token(
        email: str = "vinicius.oliveira@expertocupacional.com.br", 
        pw: str = "Close@123"
        ) -> str:

        # Não sei o que é essa key de url, parece ser constante
        url_key = 'AIzaSyA6et-dSbyxh_jcy7Zf-fhqvD5tt6wPHzQ'

        res: Response = req.post(
                    url=f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={url_key}',
                    data={
                      "returnSecureToken":True,
                      "email": email,
                      "password": pw,
                      "clientType":"CLIENT_TYPE_WEB"
                    }
                )
        
        json: dict = res.json()
        token: str = json['idToken']  

        return token 
    

    def download_and_save_xlsx_file(url: str, client_name: str) -> DataFrame:
        dir_path = os.path.join(os.getcwd(), 'data', client_name, 'temp')
        filename = f"{client_name}_temp.xlsx"

        filename_wth_dir = os.path.join(dir_path, filename)

        # Deleta o diretorio que será salvo o excel se existir
        shutil.rmtree(dir_path, ignore_errors=True) 

        # Cria a pasta no caminho
        os.makedirs(dir_path, exist_ok=True)

        # Faz o download do arquivo e salva no diretório com o nome do arquivo
        urlretrieve(url, filename_wth_dir)

        return read_excel(filename_wth_dir)


    @staticmethod
    def request_data(client_name: str, start_date: str | None = None, end_date: str | None = None) -> DataFrame:

        if client_name not in ['coop', 'copa', 'bimbo']:
            raise ValueError("Client_name passado como parametro iválido")
        
        token: str = MakeCloseRequests.get_bearer_token()

        date_formatter = DateFormatter(default_format='iso')

        start_date = date_formatter.format_date(start_date) if start_date is not None else date_formatter.today()
        end_date = date_formatter.format_date(end_date) if end_date is not None else date_formatter.months_ahead(months=3)

        params: str = f'export=true&format=xlsx&start_date={start_date}&end_date={end_date}&sync_status=error&sync_status=success&sync_status=not_sync&field_date=updated_at&status=valid'

        headers = {
            "Authorization": f"Bearer {token}",
        }

        res: Response = req.get(
                    url=f'https://app.closecare.com.br/v4/companies/{client_name}/sick_notes?{params}',
                    headers=headers
                )

        json = res.json()
        url = json['file']['url']

        df: DataFrame = MakeCloseRequests.download_and_save_xlsx_file(url=url, client_name=client_name)

        return df



    

    



