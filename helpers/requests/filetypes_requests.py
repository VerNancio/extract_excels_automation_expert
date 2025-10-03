import requests as req
import io
import pandas as pd; from pandas import DataFrame

from typing import Any

class FiletypesRequests:

    @staticmethod
    def save_file_content(filetype: str, filename: str, filepath: str, content: bytes | Any) -> None:

        filename = 'generic' if filename == '' else filename

        # Mudar o default eventualmente
        filepath = f"data/default" if filepath == '' else filepath

        path_with_file: str = f'{filepath}/{filename}.{filetype}'

        with open(path_with_file, 'wb') as f:
            f.write(content)

        print(f"Arquivo baixado com sucesso: {filename}.{filetype}")


    @staticmethod
    def file_request(request_items: dict[str, dict], 
                     filename: str, 
                     filepath: str,
                     return_content: bool = True, 
                     save_file: bool = False, 
                     filetype: str = 'csv') -> bytes | Any | None:
        try:
            req_i = request_items
            res = req.get(url=req_i['url'], params=req_i['params'], cookies=req_i['cookies'])
            res.raise_for_status()  # Levanta exceção para códigos de status de erro

            if save_file:
                FiletypesRequests.save_file_content(filetype='csv', filename=filename, 
                                                    filepath=filepath, content=res.content)

            if return_content:

                if res.content.decode("latin-1") == 'Período de datas maior que o permitido':
                    raise Exception('Período de datas maior que o permitido')

                return res.content 

        except req.exceptions.RequestException as e:
            print(f"Erro ao baixar o arquivo: {e}")


    @staticmethod
    def csv_request(request_items: dict[str, dict], filename: str = '', filepath: str = '', 
                    return_content: bool = True, save_file: bool = False) -> DataFrame | None:
    
        csv: bytes | Any = FiletypesRequests.file_request(request_items=request_items, return_content=return_content, filepath=filepath,
                                                          save_file=save_file, filename=filename, filetype='csv')

        if return_content:
            buffer = io.BytesIO(csv)
            data: DataFrame = pd.read_csv(buffer, encoding='latin-1', delimiter=';')
            return data
        
    
    @staticmethod
    def json_request(request_items: dict[str, dict], filename: str = '', filepath: str = '', 
                    return_content: bool = True, save_file: bool = False) -> DataFrame | None:
    
        json: bytes | Any = FiletypesRequests.file_request(request_items=request_items, return_content=return_content, filepath=filepath,
                                                          save_file=save_file, filename=filename, filetype='json')

        if return_content:
            buffer = io.BytesIO(json)
            data: DataFrame = pd.read_json(buffer)
            return data


    @staticmethod
    def xlsx_request(request_items: dict[str, dict], filename: str = '', filepath: str = '', 
                     return_content: bool = True, save_file: bool = False) -> DataFrame | None:
        xlsx: bytes | Any = FiletypesRequests.file_request(request_items=request_items, return_content=return_content, filepath=filepath,
                                                          save_file=save_file, filename=filename, filetype='xlsx')

        if return_content:
            buffer = io.BytesIO(xlsx)
            data: DataFrame = pd.read_excel(buffer)
            return data
