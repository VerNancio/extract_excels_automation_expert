import os
from pandas import DataFrame

from helpers.tools.date_formatter import DateFormatter


class StoreSheets:
    """
    Classe montada para abstrair código da main, serve para salvar os dados de atestados obtidos.

    As funções estáticas servem para salvar ou localmente o arquivo ou no Onedrive.
    """

    @staticmethod
    def store_in_both(df: DataFrame, client_name: str, date: str = None, report_type: str = None) -> None:
        """
        Salva o arquivo excel com os atestados no diretório data/<client_name> e no Onedrive também

        Args:
            df (Dataframe): dataframe com os dados de obtidos
            client_name (str): nome do cliente dos quais os dados dos atestados pertencem
            date (str): string de data que será usada no nome do xlsx salvo 
            report_type (str): string de tipo de de dados, se são atestados de horas ou de dias
        """

        StoreSheets.store_in_local_dir(df, client_name, date, report_type)
        StoreSheets.store_in_onedrive(df, client_name, date, report_type)


    @staticmethod
    def store_in_local_dir(df: DataFrame, client_name: str, date: str = None, report_type: str = 'date') -> None:
        """
        Salva o arquivo excel com os atestados no diretório data/<client_name>

        Args:
            df (Dataframe): dataframe com os dados de obtidos
            client_name (str): nome do cliente dos quais os dados dos atestados pertencem
            date (str): string de data que será usada no nome do xlsx salvo 
            report_type (str): string de tipo de de dados, se são atestados de horas ou de dias
        """
        
        today = DateFormatter(default_format='iso').today()

        filename = f'ATESTADOS_{client_name.upper()}_{f'HORAS_' if report_type == 'hour' else ''}{date if date is False else today}.xlsx'
        file_path = os.path.join('data', client_name, filename)
            
        df.to_excel(file_path, index=False)

        print(f'{today}: {df.shape[0]} registros salvos no diretório do projeto...')


    @staticmethod
    def store_in_onedrive(df: DataFrame, client_name: str, date: str = None, report_type: str = 'date') -> None:
        """
        Salva o arquivo excel com os atestados no Onedrive

        Args:
            df (Dataframe): dataframe com os dados de obtidos
            client_name (str): nome do cliente dos quais os dados dos atestados pertencem
            date (str): string de data que será usada no nome do xlsx salvo 
            report_type (str): string de tipo de de dados, se são atestados de horas ou de dias
        """

        today = DateFormatter(default_format='iso').today()

        onedrive_path = os.path.join(os.environ['USERPROFILE'], 'OneDrive - EXPERT GESTAO OCUPACIONAL E PREVIDENCIARIA LTDA')
        dir_path = os.path.join(onedrive_path, 'SmartReports', client_name.lower())
        filename = f'ATESTADOS_{client_name.upper()}_{f'HORAS_' if report_type == 'hour' else ''}{date if date is False else today}.xlsx'

        file_path = os.path.join(dir_path, filename)
        df.to_excel(file_path, index=False)

        print(f'{today}: {df.shape[0]} registros salvos no diretório do Onedrive...')

    