import os
import datetime as dt

import pandas as pd; from pandas import DataFrame;

from .helpers.tools.handle_kwargs import HandleKWargs

from .helpers.tools.date_formatter import DateFormatter
from .helpers.tools.compare_date_filter import CompareDateFilter    

from .requesters.filetypes_requests import FiletypesRequests
from .helpers.treatment.dataframe_treatment import DataframeTreatment
from .helpers.tools.store_data import StoreData

from .requesters.make_requests.MakeCloseRequests import MakeCloseRequests
from .requesters.make_requests.MakeJestorRequests import MakeJestorRequests
from .requesters.make_requests.MakeSocRequests import MakeSocRequests

from .selenium_scrapying.rech.rech_selenium_scrapying import RechSeleniumScrapying
from .selenium_scrapying.greif.greif_selenium_scrapying import GreifSeleniumScrapying
from .selenium_scrapying.merck.merck_selenium_scrapying import MerckSeleniumScrapying
from .selenium_scrapying.soc.soc_selenium_scrapying import SocSeleniumScrapying

from src.helpers.tools.get_credentials import get_credentials
from src.constants import CLIENTS_NAMES_LIST, STORAGE_PLACES_XLSX


def main(**kwargs) -> tuple[int, bool] | bool:
    
    # Por padrão começa False
    exec_succeded: bool = True    

    handler = HandleKWargs(kwargs)

    client_name: str = handler.handle_non_existents_clients()
    should_store_where: str = handler.handle_non_existents_storage_places()
    report_type: str = handler.handle_non_existents_report_types()
    save_with_date_in_name: bool = handler.handle_non_existents_report_types()
    
    date_to_save: str = handler.handle_date_to_save()
    date_to_filter: str = handler.handle_date_to_filter()

    date_formatter = DateFormatter()
    
    # Caso seja necessário filtrar por datas de forma diferente, faz a comparação e retorna a data de início e fim
    # if client_name in ['merck']:
        # start_date, end_date = handler.handle_start_end_dates('month')
    # elif client_name in ('leroy', 'pluri', 'viva'):
        # start_date, end_date = handler.handle_start_end_dates('range_days_ago', since_days_ago=180)
    # else:
        # start_date, end_date = handler.handle_start_end_dates('day')
    
    start_date, end_date = handler.handle_start_end_dates('day')
    
    # Se a data de inicio for maior que a da de fim de busca
    if date_formatter.to_datetime(start_date) > date_formatter.to_datetime(end_date):
        raise ValueError("Data de início de busca maior que a final")
        
    print(f'Iniciando extração dos dados do client: "{client_name.capitalize()}"\n') 

 
    any_scraping_error: bool = False
    if client_name == 'rech':
        scraper = RechSeleniumScrapying()
        df: DataFrame = scraper.run()
        any_scraping_error = scraper.some_scraping_error_occurred()

    elif client_name == 'greif':
        scraper = GreifSeleniumScrapying()
        df: DataFrame = scraper.run(date_to_filter=date_to_filter)
        any_scraping_error = scraper.some_scraping_error_occurred()

    elif client_name == 'merck':    
        scraper = MerckSeleniumScrapying(report_type=report_type)

        # Nao é necessario indicar a data porque pega do mes passado inteiro automaticamente
        df: DataFrame = scraper.run(start_date=start_date, end_date=end_date)
        any_scraping_error = scraper.some_scraping_error_occurred()

    elif client_name in ('coop', 'copa', 'bimbo'):
        df: DataFrame = MakeCloseRequests.request_data(client_name=client_name, start_date=start_date, end_date=end_date)

    elif client_name in ('workon', 'sulnorte', 'ofy', 'rip', 'fabitos', 'pergoletta'):
        requester = MakeJestorRequests(client_name=client_name)
        df = requester.run(row_post_date=date_to_filter)

    elif client_name in ('leroy', 'pluri', 'viva'):
        # scraper = SocSeleniumScrapying(client_name=client_name)
        requester = MakeSocRequests(client_name=client_name)
        df: DataFrame = requester.request_data(start_date=start_date, end_date=end_date)

    # !!!!!!! melhorar esse if depois, tá mal explicado e sem retorno de variaveis, só valores esperados
    # Se o df retornou como None ou com 0 linhas, finaliza a execução
    if (df is None or df.shape[0] == 0) and not any_scraping_error:
        print("\n0 registros capitados, dados não foram salvos...")
        return 0, True

    # Faz o tratamento do df, retorna já pronto pra ser salvo
    df_treated: DataFrame = DataframeTreatment.treat_df(df, client_name)
    total_extracted_rows = len(df_treated)
    
    print(f'Extração finalizada com sucesso. Total de registros extraídos: {total_extracted_rows}')
    
    try: 
        folder_name: str
        match client_name:
            case 'copa': folder_name = 'copaenergia'
            case _: folder_name = client_name

        auth_token: str | None = None
        if should_store_where == 'jestor':
            auth_token: str = get_credentials('jestor')['auth_token']
        
        rows_saved: int
        all_rows_were_stored: bool

        storager = StoreData()
        rows_saved, all_rows_were_stored = storager.storage_data(
            df=df_treated, 
            client_name=client_name,
            folder_name=folder_name,
            date=date_to_save, 
            date_in_name=save_with_date_in_name, 
            report_type=report_type,
            should_store_where=should_store_where,
            auth_token=auth_token
        )
        
        if rows_saved > 0:
            print(f'Total de {rows_saved} registros salvos com sucesso em: "{should_store_where}"')
        else:
            print(f'Nenhum registro foi salvo em: "{should_store_where}"')
            
    except PermissionError as e:
        print(f'Arquivo excel aberto, por favor faça a exclusão pra poder salvar o novo: {e}')
    
    except Exception as e:
        print(f'Erro: {e}')
        exec_succeded = False
        
    if not exec_succeded or any_scraping_error:
        return exec_succeded
    
    # Retorna a quantidade de linhas salvas e se todas elas foram salvas
    return rows_saved, all_rows_were_stored 
    