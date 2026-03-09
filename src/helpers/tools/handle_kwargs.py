from ...constants import CLIENTS_NAMES_LIST, STORAGE_PLACES_XLSX
from ..tools.date_formatter import DateFormatter

class HandleKWargs:

    kwargs: dict[str, str]


    def __init__(self, kwargs):
        self.kwargs = kwargs
    
    def handle_non_existents_clients(self) -> str:
        client_name = self.kwargs.get('client_name')
        if client_name not in CLIENTS_NAMES_LIST:
            raise ValueError(f"KWarg do nome do cliente não possuí valor válido: '{client_name}'\n\n" + \
                            f"Empresas disponíveis:\n{'\n'.join([f'{index + 1}. {client}' for index, client in enumerate(CLIENTS_NAMES_LIST)])}")

        return client_name


    def handle_non_existents_storage_places(self) -> str:
        # Espera valores como 'local', 'onedrive', 'both', para referência de onde deve ser salvo
        should_store_where = self.kwargs.get('should_store_where', 'local')
        if should_store_where not in STORAGE_PLACES_XLSX:
            raise ValueError(f"KWarg do lugar onde o arquivo deve ser armazenado não possuí valor válido: {should_store_where}\n\n" + \
                            f"Empresas disponíveis:\n{'\n'.join([f'{index + 1}. {PLACE}' for index, PLACE in enumerate(STORAGE_PLACES_XLSX)])}")

        return should_store_where
    

    def handle_non_existents_report_types(self) -> str:
        # Nos casos em que a extração dos atestados de dias e horas é diferente, há o KWarg de report_type pra isso
        report_type = self.kwargs.get('report_type', 'date')
        if report_type not in ['hour', 'date']:
            raise ValueError('KWarg do lugar onde o arquivo deve ser armazenado não possuí valor válido: "report_type"\n' \
                            'Necessário passar como "date" ou "hour", ou deixar como nulo (que tem valor padrão de "date")')

        return report_type
    
    
    def handle_save_with_date_in_name(self) -> bool:
        # Nos casos em que se quiser salvar o arquivo buscando com uma data especifica correspondente a data_to_filter
        save_with_date_in_name = self.kwargs.get('save_with_date_in_name', 'false')
        if save_with_date_in_name not in ['true', 'false']:
            raise ValueError('KWarg do lugar onde o arquivo deve ser armazenado não possuí valor válido: "save_with_date_in_name"\n' \
                            'Necessário passar como "true" ou "false", ou deixar como nulo (que tem valor padrão de "false")')

        return save_with_date_in_name
    
    
    def handle_date_to_filter(self) -> bool:
        # Nos casos em que se quiser salvar o arquivo com uma data especifica correspondente a date_to_save
        date_to_filter_kw = self.kwargs.get('date_to_filter', 'ultimo_dia_util')
        
        date_to_filter: str
        date_formatter = DateFormatter()

        match date_to_filter_kw:
            case 'hoje':
                date_to_filter = date_formatter.today()
            case 'ontem':
                date_to_filter = date_formatter.yesterday()
            case 'ultimo_dia_util':
                date_to_filter = date_formatter.last_working_day()
            case 'ultimo_dia_ultimo_mes':
                date_to_filter = date_formatter.last_month_last_day()
            case _:
                if date_formatter.is_valid_date(date_to_filter_kw):
                    return date_to_filter_kw
                
                raise ValueError('KWarg do lugar onde o arquivo deve ser armazenado não possuí valor válido: "date_to_filter"\n' \
                                'Necessário passar como uma data válida, "hoje", "ontem", "ultimo_dia_util", "ultimo_dia_ultimo_mes", ou deixar como nulo (que tem valor padrão de "ultimo_dia_util")')
                
        return date_to_filter
        
    
    def handle_date_to_save(self) -> bool:
        # Nos casos em que se quiser salvar o arquivo com uma data especifica correspondente a date_to_save
        date_to_save_kw = self.kwargs.get('date_to_save', 'ultimo_dia_util')
        
        date_to_save: str
        date_formatter = DateFormatter()
            
        match date_to_save_kw:
            case 'hoje':
                date_to_save = date_formatter.today()
            case 'ontem':
                date_to_save = date_formatter.yesterday()
            case 'ultimo_dia_util':
                date_to_save = date_formatter.last_working_day()
            case 'ultimo_dia_ultimo_mes':
                date_to_save = date_formatter.last_month_last_day()
            case _:
                if date_formatter.is_valid_date(date_to_save_kw):
                    return date_to_save_kw
        
                raise ValueError('KWarg do lugar onde o arquivo deve ser armazenado não possuí valor válido: "date_to_save"\n' \
                                'Necessário passar como uma data válida, "hoje", "ontem", "ultimo_dia_util", "ultimo_dia_ultimo_mes", ou deixar como nulo (que tem valor padrão de "ultimo_dia_util")')
                
        return date_to_save
        