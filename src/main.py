import os
import datetime as dt

import pandas as pd; from pandas import DataFrame;


from .constants import CLIENTS_NAMES_LIST, STORAGE_PLACES_XLSX
# from .requesters.make_requests.MakeRequests import CLIENTS_NAMES_LIST


from .helpers.tools.handle_kwargs import HandleKWargs

from .helpers.tools.date_formatter import DateFormatter
# from .helpers.tools.compare_date_filter import CompareDateFilter

# from .requesters.filetypes_requests import FiletypesRequests
from .helpers.treatment.dataframe_treatment import DataframeTreatment
from .helpers.tools.store_excels import StoreSheets

from .requesters.make_requests.MakeCloseRequests import MakeCloseRequests
from .requesters.make_requests.MakeJestorRequests import MakeJestorRequests

from .selenium_scrapying.rech.rech_selenium_scrapying import RechSeleniumScrapying
from .selenium_scrapying.greif.greif_selenium_scrapying import GreifSeleniumScrapying
from .selenium_scrapying.merck.merck_selenium_scrapying import MerckSeleniumScrapying



def main(**kwargs):

    handler = HandleKWargs(kwargs)

    client_name: str = handler.handle_non_existents_clients()
    should_store_where: str = handler.handle_non_existents_storage_places()
    report_type: str = handler.handle_non_existents_report_types()
    save_with_date_in_name: bool = handler.handle_non_existents_report_types()


    date_formatter = DateFormatter()
    date_to_filter: str = kwargs.get('date_to_filter', date_formatter.yesterday())
    start_date: str = kwargs.get('start_date', date_formatter.yesterday())
    end_date: str = kwargs.get('end_date', date_formatter.yesterday())


    if client_name == 'rech':
        scraper = RechSeleniumScrapying()
        df: DataFrame = scraper.run()

    elif client_name == 'greif':
        scraper = GreifSeleniumScrapying()
        df: DataFrame = scraper.run(date_to_filter=date_to_filter)

    elif client_name == 'merck':
        scraper = MerckSeleniumScrapying(report_type=report_type)

        # Nao é necessario indicar a data porque pega do mes passado inteiro automaticamente
        df: DataFrame = scraper.run()

    elif client_name in ['coop', 'copa', 'bimbo']:
        df: DataFrame = MakeCloseRequests.request_data(client_name=client_name, start_date=start_date, end_date=end_date)

    elif client_name in ['workon', 'sulnorte', 'ofy', 'rip']:
        requester = MakeJestorRequests(client_name=client_name)
        df = requester.run(row_post_date=date_to_filter)

    elif client_name in ['leroy', 'pluri']:
        
        pass
        
        # request_items: dict[str, str]
        # match(client_name):
        #     case 'leroy': request_items = MakeRequests.make_leroy_request(start_date=date_to_filter, end_date=date_to_filter_month_added)
        #     case 'pluri': request_items = MakeRequests.make_pluri_request(start_date=date_to_filter, end_date=date_to_filter_month_added)

        # # request_items['url'] = 'https://ws1.soc.com.br/WebSoc/exportadados?parametro={"empresa":"388105","codigo":"208706","chave":"9c54b4e8660ab7cc0dc6","tipoSaida":"csv","empresaTrabalho":"592252","dataInicio":"02/09/2025","dataFim":"10/09/2025"}'
        # df = FiletypesRequests.csv_request(request_items=request_items)


    # Se o df retornou como None ou com 0 linhas, finaliza a execução
    if df is None or df.shape[0] == 0:
        print("0 registros capitados, xlsx não criado...")
        return

    # Faz o tratamento do df, retorna já pronto pra ser salvo
    df_treated: DataFrame = DataframeTreatment.treat_df(df, client_name)
    
    try: 

        date_to_save: str = kwargs.get('date_to_filter', date_formatter.today())

        storager = StoreSheets()

        storager.storage_data(
            df=df_treated, 
            client_name=client_name,
            date=date_to_save, 
            date_in_name=save_with_date_in_name, 
            report_type=report_type,
            should_store_where=should_store_where
        )

        # if should_store_where == 'onedrive':
        #     StoreSheets.store_in_onedrive(df=df_treated, client_name=client_name,
        #                               date=date_to_filter, date_in_name=date_in_name, 
        #                               report_typFe=report_type)

        # elif should_store_where == 'local':
        #     StoreSheets.store_in_local_dir(df=df_treated, client_name=client_name,
        #                               date=date_to_filter, date_in_name=date_in_name, 
        #                               report_type=report_type)

        # elif should_store_where == 'both':
        #     StoreSheets.store_in_both(df=df_treated, client_name=client_name,
        #                               date=date_to_filter, date_in_name=date_in_name, 
        #                               report_type=report_type)
            
    except PermissionError as e:
        print(f'Arquivo excel aberto, por favor faça a exclusão pra poder salvar o novo: {e}')
    
    except Exception as e:
        print(f'Erro: {e}')
