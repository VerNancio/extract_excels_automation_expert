import os
import datetime as dt
from dateutil.relativedelta import relativedelta

import pandas as pd; from pandas import DataFrame, Timestamp;


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
        # df = CompareDateFilter.is_equal(df, column_name='data_abertura', compare_date=date_to_filter)

    elif client_name == 'greif':
        scraper = GreifSeleniumScrapying()
        df: DataFrame = scraper.run(date_to_filter=date_to_filter)

    elif client_name == 'merck':
        scraper = MerckSeleniumScrapying(report_type=report_type)
        df: DataFrame = scraper.run()

    elif client_name in ['coop', 'copa', 'bimbo']:
        print(start_date)
        df = MakeCloseRequests.request_data(client_name=client_name, start_date=start_date)
        print(df)

    elif client_name in ['workon', 'sulnorte', 'ofy', 'rip']:

        emails = {
            'workon': 'afastamento@workongroup.com.br', 
            'sulnorte': '', 
            'ofy': '', 
            'rip': ''
        }

        requester = MakeJestorRequests(client_name=client_name)
        df = requester.run(sender_email=emails[client_name], row_post_date=date_to_filter)

    elif client_name in ['leroy', 'pluri']:
        
        pass

        # request_items: dict[str, str]
        # print(date_to_filter)
        # print(date_to_filter_month_added)
        # match(client_name):
        #     case 'leroy':
        #         request_items = MakeRequests.make_leroy_request(start_date=date_to_filter, end_date=date_to_filter_month_added)
        #     case 'pluri':
        #         request_items = MakeRequests.make_pluri_request(start_date=date_to_filter, end_date=date_to_filter_month_added)

        # # request_items['url'] = 'https://ws1.soc.com.br/WebSoc/exportadados?parametro={"empresa":"388105","codigo":"208706","chave":"9c54b4e8660ab7cc0dc6","tipoSaida":"csv","empresaTrabalho":"592252","dataInicio":"02/09/2025","dataFim":"10/09/2025"}'
        # print(request_items)
        # df = FiletypesRequests.csv_request(request_items=request_items)
        # print(df)

        # print(df['DT_CRIACAO'])
        # df: DataFrame = CompareDateFilter.is_equal(df, column_name='DT_CRIACAO', compare_date=date_to_filter)

    # Se o df retornou como None ou com 0 linhas, finaliza a execução
    if df is None or df.shape[0] == 0:
        print("0 registros capitados, xlsx não criado...")
        return

    # Faz o tratamento do df, retorna já pronto pra ser salvo
    df_treated: DataFrame = DataframeTreatment.treat_df(df, client_name)
    
    try: 

        storager = StoreSheets()

        storager.storage_data(
            df=df_treated, 
            client_name=client_name,
            date=date_to_filter, 
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


# if __name__ == '__main__':

#     keys = [
#         'client_name', 'date_to_filter', 'save_with_date_in_name', 
#         'start_date', 'end_date', 'should_store_where', 'report_type'
#     ]

#     help_msg = "KWarg deve ser passado no formato para cada item desta forma: \n" \
#                     "--client_name:<nome da empresa>\n" \
#                     "--date_to_filter:<data pra filtrar: dd/mm/YYYY>\n" \
#                     "--start_date:<data pra filtrar: dd/mm/YYYY>\n" \
#                     "--end_date:<data pra filtrar: dd/mm/YYYY>\n" \
#                     "--should_store_where:<local/onedrive/both>\n" \
#                     "--report_type:<'hour'/'date'>\n" 

#     kwargs = sys.argv[1:]

#     if any(help_arg in kwarg for help_arg in ['-h', '--h', '-help', '--help'] for kwarg in kwargs):
#         print(help_msg)
        
#     else:

#         kwargs_from_cmd = {}
#         for arg in kwargs:
#             if ':' in arg:
#                 key_not_striped, value = arg.split(':', 1)
#                 key = key_not_striped.lstrip('--')

#                 kwargs_from_cmd[key] = value

#                 if key not in keys:
#                     err_msg: str = f"Chave enviada não é válida: {key}"
#                     raise ValueError(err_msg)
                
#             else:
#                 raise ValueError(help_msg)
            
#         if 'client_name' not in kwargs_from_cmd:
#             raise Exception('Kwarg obrigatório "client_name" não foi enviado ou está com escrita incorreta.')
            
#         main(**kwargs_from_cmd)

#     print('\nExecução finalizada.')
