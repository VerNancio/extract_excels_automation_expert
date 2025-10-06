from collections import Counter

import datetime as dt
from dateutil.relativedelta import relativedelta


class DateFormatter:

    sep: str
    date_format: str

    default_formats = {
        'iso': '%Y-%m-%d',
        'dmy': '%d/%m/%Y',
        'dmy-dashed': '%d-%m-%Y',
        'usa': '%m/%d/%Y' 
    }


    def __init__(self, default_format = 'dmy', sep: str = None, date_format: str = None):
        """
        Adiciona os separadores a um formato de data.

        Args:
            default_format: str: str de formato padrão, é necessário passar o nome de uma;
                                 definidas: 'iso', 'dmy', 'usa' etc
            sep (str): string que definira qual será o separador do formato; Ex: '-', '/', '.'
            date_format (str): str de formato de data customizado; passar separador como "?" 
                                 para ser substituído; ex: 'y?m?d', 'm?Y?d' etc
        """

        if default_format in self.default_formats.keys():
            self.default_format = default_format
            self.date_format = self.default_formats[default_format]

        else:
            self.sep = sep if sep is not None else '/'
            self.date_format = date_format if date_format is not None else '%d/%m/%Y'


    def set_new_format(self, default_format: str, custom_format: str) -> None:
        """
        Adiciona os separadores a um formato de data.

        Args:
            default_format: str: str de formato padrão, é necessário passar o nome de uma;
                                 ex: 'iso', 'dmy', 'usa' etc
            custom_format (str): str de formato de data customizado; passar separador como "?" 
                                 para ser substituído; ex: 'y?m?d', 'm?Y?d' etc
            sep (sep): separador a ser adicionado no lugar da "?" do formato
        """

        if default_format in self.default_formats.keys:
            self.date_format = self.default_formats[default_format]
            return

        custom_format = custom_format.strip()
        char_counter = Counter(custom_format)

        dt_chars_set: set = set('Y', 'y', 'm', 'd')

        if char_counter['?'] > 2:
            raise ValueError("Formato customizado inválido: máximo de dois separadores de data")
        elif dt_chars_set.issubset(char_counter.keys()):
            raise ValueError("Formato customizado inválido: caractéres de data inválidos")
        elif all(map(lambda c_qnt: c_qnt > 1, char_counter.values())) :
            raise ValueError("Formato customizado inválido: há caractéres de data repetidos")

        self.date_format = custom_format.replace(old='?', new=self.sep)
    

    def set_new_sep(self, sep: str) -> None:
        if type(sep) != str:
            raise ValueError("Separador inválido: necessário ser do tipo 'str'")
        if len(sep) != 1:
            raise ValueError("Separador inválido: separador deve ser uma 'str' de tamanho 1")
        
        self.set_new_sep


    def format_date(self, date: str, current_format: str = '%d/%m/%Y', new_format: str = None) -> str:
        """
        Altera o formato de uma data passada, utiliza um formato padrão pra interpretar
        o 'current_format' caso None e o formato instanciado na classe caso o 'new_format' seja None

        Args:
            date (str): data a ter seu formato alterado
            current_format (str): formato da data a ser passada; pode ser passado como 'iso', 'dmy', 'usa' etc
            new_format (str): formato de data de retorno; pode ser passado como 'iso', 'dmy', 'usa' etc
        Return:
            str: Retorna a data passado no novo formato
        """

        if current_format in self.default_formats:
            current_format = self.default_formats[current_format]

        if new_format in self.default_formats:
            new_format = self.default_formats[new_format]

            

        new_format = self.date_format if new_format is None else new_format

        dt_obj = dt.datetime.strptime(date, current_format)

        return dt_obj.strftime(new_format)


    def today(self, return_in_datetime: bool = False) -> str | dt.date:
        date = dt.date.today()
        if return_in_datetime: 
            return date
        else: 
            return date.strftime(self.date_format)
    

    def yesterday(self, return_in_datetime: bool = False) -> str | dt.date:
        date = self.today(return_in_datetime=True) - relativedelta(days=1)
        if return_in_datetime: 
            return date
        else: 
            return date.strftime(self.date_format)
    

    def tomorrow(self, return_in_datetime: bool = False) -> str | dt.date:
        date = self.today(return_in_datetime=True) + relativedelta(days=1)
        if return_in_datetime: 
            return date
        else: 
            return date.strftime(self.date_format)
    

    def days_ahead(self, days: int, return_in_datetime: bool = False) -> str | dt.date:
        date = self.today(return_in_datetime=True) + relativedelta(days=days)
        if return_in_datetime: 
            return date
        else: 
            return date.strftime(self.date_format)
        

    def days_ago(self, days: int, return_in_datetime: bool = False) -> str | dt.date:
        date = self.today(return_in_datetime=True) - relativedelta(days=days)
        if return_in_datetime: 
            return date
        else: 
            return date.strftime(self.date_format)


    def months_ahead(self, months: int, return_in_datetime: bool = False) -> str | dt.date:
        date = self.today(return_in_datetime=True) + relativedelta(months=months)
        if return_in_datetime: 
            return date
        else: 
            return date.strftime(self.date_format)
    
    
    def months_ago(self, months: int, return_in_datetime: bool = False) -> str | dt.date:
        date = self.today(return_in_datetime=True) - relativedelta(months=months)
        if return_in_datetime: 
            return date
        else: 
            return date.strftime(self.date_format)
        

    def current_month_first_day(self, return_in_datetime: bool = False)  -> str | dt.date:
        date: dt.date = self.today(return_in_datetime=True).replace(day=1)
        if return_in_datetime: 
            return date
        else: 
            return date.strftime(self.date_format)

        
    def current_month_last_day(self, return_in_datetime: bool = False)  -> str | dt.date:
        date: dt.date = self.next_month_first_day(return_in_datetime=True) - dt.timedelta(days=1)
        if return_in_datetime: 
            return date
        else: 
            return date.strftime(self.date_format)


    def last_month_first_day(self, return_in_datetime: bool = False)  -> str | dt.date:
        date: dt.date = self.months_ago(months=1, return_in_datetime=True).replace(day=1)
        if return_in_datetime: 
            return date
        else: 
            return date.strftime(self.date_format)


    def last_month_last_day(self, return_in_datetime: bool = False)  -> str | dt.date:
        date: dt.date = self.current_month_first_day(return_in_datetime=True) - dt.timedelta(days=1)
        if return_in_datetime: 
            return date
        else: 
            return date.strftime(self.date_format)


    def next_month_first_day(self, return_in_datetime: bool = False)  -> str | dt.date:
        date: dt.date = self.months_ahead(months=1, return_in_datetime=True).replace(day=1)
        if return_in_datetime: 
            return date
        else: 
            return date.strftime(self.date_format)
