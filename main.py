import os
import sys
import requests as req
import pandas as pd; from pandas import DataFrame, Timestamp;
import datetime as dt
import json

from helpers.requests.filetypes_requests import FiletypesRequests
from helpers.treatment.dataframe_treatment import DataframeTreatment

from get_files_config import REQUESTS, CLIENTS_NAMES_LIST

from selenium_scrapying.rech.rech_selenium_scrapying import RechSeleniumScrapying
from selenium_scrapying.greif.greif_selenium_scrapying import GreifSeleniumScrapying


def main(**kwargs):

    client_name = kwargs["client_name"]

    start_date_to_filter = kwargs['start_date'] if 'start_date' in kwargs.keys() else None


    if client_name not in CLIENTS_NAMES_LIST:
        raise ValueError(f"KWarg do nome do cliente não possuí valor válido: {client_name}\n\n" + \
                         f"Empresas disponíveis:\n {'\n'.join([f'{index + 1}. {client}' for index, client in enumerate(CLIENTS_NAMES_LIST)])}")


    start_date_to_filter: Timestamp | None 

    if client_name == 'rech':
        scraper = RechSeleniumScrapying()
        data = scraper.run()

        df = pd.DataFrame(data)

    elif client_name == 'greif':
        scraper = GreifSeleniumScrapying()
        data = scraper.run()

        df = pd.DataFrame(data)
        df.to_excel('./aa.xlsx')

    elif client_name in ['leroy', 'pluri']:
        request_items = REQUESTS[client_name]

        df = FiletypesRequests.csv_request(request_items=request_items)


    formated_df = DataframeTreatment.treat_columns(df, client_name)

    if start_date_to_filter:
        start_date_to_filter = dt.datetime.strptime(start_date_to_filter, '%d/%m/%Y')
        formated_df = formated_df.loc[
            pd.to_datetime(formated_df['data_inicio'], format='%d/%m/%Y', errors='coerce') >= start_date_to_filter
        ]

    try: 
        today = dt.date.today().strftime('%d_%m_%Y')

        formated_df.to_excel(f'data/{client_name}/ATESTADOS_{client_name.upper()}_{today}.xlsx', index=False)

        # onedrive_path = os.path.join(os.environ['USERPROFILE'], 'OneDrive - EXPERT GESTAO OCUPACIONAL E PREVIDENCIARIA LTDA')
        # dir_path = os.path.join(onedrive_path, 'SmartReports', client_name.lower())
        # file_path = os.path.join(dir_path, f'ATESTADOS_{client_name.upper()}_{today}.xlsx')

        # formated_df.to_excel(file_path, index=False)

    except PermissionError as e:
        print(f'Arquivo excel aberto, por favor faça a exclusão pra poder salvar o novo: {e}')


if __name__ == '__main__':

    kwargs_from_cmd = {}
    for arg in sys.argv[1:]:
        if ':' in arg:
            key, value = arg.split(':', 1)
            kwargs_from_cmd[key.lstrip('--')] = value
        else:
            raise ValueError("KWarg deve ser passado no formato: --client_name:<nome_da_empresa>")

    main(**kwargs_from_cmd)