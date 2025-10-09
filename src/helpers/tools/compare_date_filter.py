import datetime as dt
import pandas as pd; from pandas import DataFrame


class CompareDateFilter:


    @staticmethod
    def is_equal(df: DataFrame, column_name: str, compare_date: str, date_sep='/') -> DataFrame:
        """_Compara datas de uma coluna com uma data específica (dd/mm/YYYY)
        e retorna o DataFrame filtrado._

        Args:
            df (DataFrame): _Dataframe a ser comparado e filtrado_
            column_name (str): _Nome da coluna alvo do filtro_
            compare_date (str): _Data para filtragem_
            date_sep (str, optional): _Separador da string de data_. Defaults to '/'.

        Returns:
            DataFrame: _Dataframe fitrado_
        """

        # Converte a data de comparação em date
        date_to_filter = dt.datetime.strptime(compare_date, f'%d{date_sep}%m{date_sep}%Y').date()

        # Converte a coluna para datetime, depois pega só a parte date
        mask = pd.to_datetime(df[column_name], dayfirst=True).dt.date == date_to_filter

        return df[mask]
    
    
    @staticmethod
    def is_beetween(df: DataFrame, column_name: str, start_date: dt.datetime, end_date: dt.datetime, date_sep='/') -> DataFrame:
        """_Compara datas de uma coluna com um intervalo de datas (dd/mm/YYYY) entre a "start_date"
        e a "end_date", para daí e retornr o DataFrame filtrado._

        Args:
            df (DataFrame): _Dataframe a ser comparado e filtrado_
            column_name (str): _Nome da coluna alvo do filtro_
            start_date (datetime): _Data de início do filtro em datetime_
            end_date (datetime): _Data de início do filtro em datetime_
            date_sep (str, optional): _Separador da string de data_. Defaults to '/'.

        Returns:
            DataFrame: _Dataframe fitrado_
        """
        
        # Mascára de filtro onde é verdadeiro  o período entre as duas datas
        mask = (start_date <= pd.to_datetime(df[column_name], dayfirst=True)) & \
               (pd.to_datetime(df[column_name], dayfirst=True) <= end_date)

        return df[mask]