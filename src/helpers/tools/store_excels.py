import os
from pandas import DataFrame

from .date_formatter import DateFormatter


class StoreSheets:
    """
    Classe montada para abstrair código da main, serve para salvar os dados de atestados obtidos.

    As funções estáticas servem para salvar ou localmente o arquivo ou no Onedrive.
    """

    def storage_data(
        self,
        df: DataFrame, 
        client_name: str, 
        date: str = None, 
        date_in_name: bool = False, 
        report_type: str = None,
        should_store_where: str = 'local'
        ) -> bool:
        """
        Salva o arquivo excel com os atestados no diretório data/<client_name> e no Onedrive também

        Args:
            df (Dataframe): dataframe com os dados de obtidos
            client_name (str): nome do cliente dos quais os dados dos atestados pertencem
            date (str): string de data que será usada no nome do xlsx salvo 
            date_in_name (bool): booleano que define se a data no nome do arquivo deve ser a data
                                    da variável date ou não
            report_type (str): string de tipo de de dados, se são atestados de horas ou de dias
        """

        match (should_store_where):
            case 'onedrive':
                StoreSheets.store_in_onedrive(df=df, client_name=client_name,
                                        date=date, date_in_name=date_in_name, 
                                        report_type=report_type)

            case 'local':
                StoreSheets.store_in_local_dir(df=df, client_name=client_name,
                                        date=date, date_in_name=date_in_name, 
                                        report_type=report_type)
            case 'both':
                StoreSheets.store_in_both(df=df, client_name=client_name,
                                        date=date, date_in_name=date_in_name, 
                                        report_type=report_type)

        return True


    @staticmethod
    def store_in_both(
        df: DataFrame, 
        client_name: str, 
        date: str = None, 
        date_in_name: bool = False, 
        ) -> None:
        """
        Salva o arquivo excel com os atestados no diretório data/<client_name> e no Onedrive também

        Args:
            df (Dataframe): dataframe com os dados de obtidos
            client_name (str): nome do cliente dos quais os dados dos atestados pertencem
            date (str): string de data que será usada no nome do xlsx salvo 
            date_in_name (bool): booleano que define se a data no nome do arquivo deve ser a data
                                 a da variável date ou não
        """

        StoreSheets.store_in_onedrive(df=df, client_name=client_name,
                                      date=date, date_in_name=date_in_name, 
                                     )
        
        StoreSheets.store_in_onedrive(df=df, client_name=client_name,
                                      date=date, date_in_name=date_in_name, 
                                     )


    @staticmethod
    def store_in_local_dir(
        df: DataFrame, 
        client_name: str, 
        date: str = None, 
        date_in_name: bool = False, 
        report_type: str = None
    ) -> None:
        """
        Salva o arquivo excel com os atestados no diretório data/<client_name>

        Args:
            df (Dataframe): dataframe com os dados de obtidos
            client_name (str): nome do cliente dos quais os dados dos atestados pertencem
            date (str): string de data que será usada no nome do xlsx salvo 
            date_in_name (bool): booleano que define se a data no nome do arquivo deve ser a data
                                 a da variável date ou não
            report_type (str): string de tipo de de dados, se são atestados de horas ou de dias
        """

        date_formatter = DateFormatter()
        if date_in_name:
            date_to_save = date_formatter.format_date(date, current_format='dmy', new_format='iso')
        else:
            date_to_save = DateFormatter(default_format='iso').today()
            

        filename = f'ATESTADOS_{client_name.upper()}_{f'HORAS_' if report_type == 'hour' else ''}{date_to_save}.xlsx'
        file_path = os.path.join('data', client_name, filename)
                    
        df.to_excel(file_path, index=False)

        print(f'{date_to_save}: {df.shape[0]} registros salvos no diretório local do projeto...')


    @staticmethod
    def store_in_onedrive(
        df: DataFrame, 
        client_name: str, 
        date: str = None, 
        date_in_name: bool = False, 
        report_type: str = None
    ) -> None:
        """
        Salva o arquivo excel com os atestados no Onedrive

        Args:
            df (Dataframe): dataframe com os dados de obtidos
            client_name (str): nome do cliente dos quais os dados dos atestados pertencem
            date (str): string de data que será usada no nome do xlsx salvo 
            date_in_name (bool): booleano que define se a data no nome do arquivo deve ser a data
                                 a da variável date ou não
            report_type (str): string de tipo de de dados, se são atestados de horas ou de dias
        """

        date_formatter = DateFormatter()
        if date_in_name:
            date_to_save = date_formatter.format_date(date, current_format='dmy', new_format='iso')
        else:
            date_to_save = DateFormatter(default_format='iso').today()
        # C:\Users\Expert149\EXPERT GESTAO OCUPACIONAL E PREVIDENCIARIA LTDA\Expert Ocupacional Externo - SmartReports\Bimbo\Extração Automatizada
        # onedrive_path = os.path.join(os.environ['USERPROFILE'], 'OneDrive - EXPERT GESTAO OCUPACIONAL E PREVIDENCIARIA LTDA')
        # filename = f'ATESTADOS_{client_name.upper()}_{f'HORAS_' if report_type == 'hour' else ''}{date_to_save}.xlsx'

        sharepoint_path = os.path.join(os.environ['USERPROFILE'], 'EXPERT GESTAO OCUPACIONAL E PREVIDENCIARIA LTDA', 'Expert Ocupacional Externo - SmartReports')
        dir_path = os.path.join(sharepoint_path, client_name.lower(), 'Extração Automatizada')
        filename = f'ATESTADOS_{client_name.upper()}_{f'HORAS_' if report_type == 'hour' else ''}{date_to_save}.xlsx'

        file_path = os.path.join(dir_path, filename)
        df.to_excel(file_path, index=False)

        print(f'{date_to_save}: {df.shape[0]} registros salvos no diretório do Onedrive...')

    