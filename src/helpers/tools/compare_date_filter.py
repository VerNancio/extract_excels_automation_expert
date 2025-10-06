import datetime as dt
import pandas as pd; from pandas import DataFrame


class CompareDateFilter:


    @staticmethod
    def is_equal(df: DataFrame, column_name: str, compare_date: str, date_sep='/') -> DataFrame:
        """
        Compara datas de uma coluna com uma data específica (dd/mm/YYYY)
        e retorna o DataFrame filtrado.
        """

        # Converte a data de comparação em date
        date_to_filter = dt.datetime.strptime(compare_date, f'%d{date_sep}%m{date_sep}%Y').date()

        # Converte a coluna para datetime, depois pega só a parte date
        mask = pd.to_datetime(df[column_name], dayfirst=True).dt.date == date_to_filter

        return df[mask]
