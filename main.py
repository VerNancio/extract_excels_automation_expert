import requests as req
import pandas as pd; from pandas import DataFrame;

from helpers.requests.filetypes_requests import FiletypesRequests
from helpers.treatment.dataframe_treatment import DataframeTreatment

from get_files_config import URLS

from selenium_scrapying.rech.rech_selenium_scrapying import RechSeleniumScrapying
from selenium_scrapying.greif.greif_selenium_scrapying import GreifSeleniumScrapying


def main():

    scraper = RechSeleniumScrapying()
    scraper = GreifSeleniumScrapying()

    data = scraper.run()

    df = pd.DataFrame(data)

    # return

    empresa = 'rech'

    request_items = URLS[empresa]


    formated_df = DataframeTreatment.treat_columns(df, empresa)

    try: 
        formated_df.to_excel(f'data/{empresa}/prototipo_{empresa}.xlsx', index=False)

    except PermissionError as e:
        print(f'Arquivo excel aberto, por favor faça a exclusão pra poder salvar o novo: {e}')


if __name__ == '__main__':
    main()