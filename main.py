import os
import sys
import requests as req
import pandas as pd; from pandas import DataFrame;
import json

from helpers.requests.filetypes_requests import FiletypesRequests
from helpers.treatment.dataframe_treatment import DataframeTreatment

from get_files_config import REQUESTS, CLIENTS_NAMES_LIST

from selenium_scrapying.rech.rech_selenium_scrapying import RechSeleniumScrapying
from selenium_scrapying.greif.greif_selenium_scrapying import GreifSeleniumScrapying


def main(**kwargs):

    empresa = kwargs["client_name"]

    if empresa not in CLIENTS_NAMES_LIST:
        raise ValueError(f"KWarg do nome do cliente não possuí valor válido: {empresa}\n\n" + \
                         f"Empresas disponíveis:\n {'\n'.join([f'{index + 1}. {client}' for index, client in enumerate(CLIENTS_NAMES_LIST)])}")

    if empresa == 'rech':
        scraper = RechSeleniumScrapying()
        data = scraper.run()

        df = pd.DataFrame(data)
        print(df.columns)

    elif empresa == 'greif':
        scraper = GreifSeleniumScrapying()
        data = scraper.run()

        df = pd.DataFrame(data)
        return

        # df = pd.read_json('./data/greif/temp/chamados_suporte_enduser_retorno_new (1).json')

    elif empresa in ['leroy', 'pluri']:
        request_items = REQUESTS[empresa]

        df = FiletypesRequests.csv_request(request_items=request_items)
        # df.to_excel('aa.xlsx')
        # print(df.columns)

    formated_df = DataframeTreatment.treat_columns(df, empresa)

    # print(formated_df)
    # formated_df = formated_df[formated_df['data_inicio'] > pd.Timestamp('18/08/2025')]
    # print(formated_df)

    try: 
        formated_df.to_excel(f'data/{empresa}/ATESTADOS_{empresa.upper()}_02-09-2025--teste.xlsx', index=False)

        # onedrive_path = os.path.join(os.environ['USERPROFILE'], 'OneDrive - EXPERT GESTAO OCUPACIONAL E PREVIDENCIARIA LTDA')
        # dir_path = os.path.join(onedrive_path, 'SmartReports', empresa.lower())
        # file_path = os.path.join(dir_path, f'ATESTADOS_{empresa.upper()}_03-09-2025--teste.xlsx')

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