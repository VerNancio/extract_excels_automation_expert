import requests as req
import pandas as pd; from pandas import DataFrame;

from helpers.requests.filetypes_requests import FiletypesRequests
from helpers.treatment.dataframe_treatment import DataframeTreatment

from get_files_config import URLS


def main():

    empresa = 'leroy' 

    url = URLS[empresa]


    df: DataFrame = FiletypesRequests.csv_request(url=url, save_file=False)

    formated_df = DataframeTreatment.treat_columns(df, empresa)
    # print(formated_df)

    formated_df.to_excel(f'data/default/prototipo_{empresa}.xlsx', index=False)


if __name__ == '__main__':
    main()