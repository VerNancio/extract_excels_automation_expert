from ...constants import CLIENTS_NAMES_LIST, STORAGE_PLACES_XLSX


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
        # Nos casos em que se quiser salvar o arquivo com uma data especifica correspondente a data_to_filter
        save_with_date_in_name = self.kwargs.get('save_with_date_in_name', 'false')
        if save_with_date_in_name not in ['true', 'false']:
            raise ValueError('KWarg do lugar onde o arquivo deve ser armazenado não possuí valor válido: "save_with_date_in_name"\n' \
                            'Necessário passar como "true" ou "false", ou deixar como nulo (que tem valor padrão de "false")')

        return save_with_date_in_name
        