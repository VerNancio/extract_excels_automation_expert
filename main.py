import requests as req
import pandas as pd; from pandas import DataFrame;
# import urllib

from helpers.requests.filetypes_requests import FiletypesRequests
from helpers.treatment.dataframe_treatment import DataframeTreatment

from get_files_config import URLS

from selenium_scrapying.rech.run import app


def main():

    res = app()
    df = pd.DataFrame(res)
    df.to_excel('./teste.xlsx')
    print(df)

    empresa = 'greif' 

    request_items = URLS[empresa]

    # df = pd.read_json('./a.json')
    # print(df['Protocolo - Funcionário - Matrícula '])


    return




    df: DataFrame = FiletypesRequests.csv_request(request_items=request_items, save_file=True, return_content=False)

    formated_df = DataframeTreatment.treat_columns(df, empresa)

    try: 
        formated_df.to_excel(f'data/{empresa}/prototipo_{empresa}.xlsx', index=False)

    except PermissionError as e:
        print(f'Arquivo excel aberto, por favor faça a exclusão pra poder salvar o novo: {e}')


if __name__ == '__main__':
    main()