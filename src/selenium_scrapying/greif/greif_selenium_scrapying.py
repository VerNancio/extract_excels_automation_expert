import os
import shutil
from time import sleep

import pandas as pd; from pandas import DataFrame, Series

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

from ...helpers.tools.get_credentials import get_credentials



class GreifSeleniumScrapying:

    driver: WebDriver
    credentials: dict
    menu_window_handler: str
    # filters: list[str] = ['Pendente', 'Responsável Redirecionado']  # nao funcional e provavelmente errado
    filters: list[str] = ['Pendente']
    

    def __init__(self):
        self.download_dir_path = "./data/greif/"
        self.download_temp_dir_path = os.path.join(self.download_dir_path, 'temp')

        os.makedirs(self.download_dir_path, exist_ok=True)
        # print(f"Pasta de downloads garantida em: {self.download_dir_path}")

        os.makedirs(self.download_temp_dir_path, exist_ok=True)
        print(f"Pasta de download temporária garantida em: {self.download_temp_dir_path}")
        
        chrome_options = Options()
        chrome_options.add_experimental_option(
            "prefs", {
                "download.default_directory": os.path.abspath(self.download_temp_dir_path),
                "download.prompt_for_download": False,
            }
        )
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.credentials = get_credentials('greif')


    def run(self, date_to_filter: str | None) -> DataFrame | None:

        # try:
            self.do_login()
            self.go_to_menu()

            any_register_to_return: bool = self.add_filters(date_to_filter=date_to_filter)
            if any_register_to_return is False:
                return None
            
            self.export_and_download_json()

            df: DataFrame = self.get_temp_json_df()
            df = self.normalize_temp_json(df)

            tickets_ids: Series = df.loc[:,'Número Chamado']
            self.download_others_infos_xlsx(tickets_ids)

            df = self.merge_infos_into_df(df)
            df = self.pre_treat(df) 

            return df

        # except Exception as e:
            print(f"Ocorreu um erro: {e}")

        # finally:
            self.driver.quit()
            print("Navegador fechado.")


    def do_login(self) -> None:

        url: str = 'https://app.plugbeneficios.com.br/dashboard_painel_RHlocal/?login=expert'
        
        self.driver.get(url)
        sleep(1)

        username_input = self.driver.find_element(By.ID, 'id_sc_field_login')
        username_input.clear()
        for char in self.credentials['username']:
            username_input.send_keys(char)
            sleep(0.02)

        sleep(1)
        pw_input = self.driver.find_element(By.ID, 'id_sc_field_pswd')
        for char in self.credentials['pw']:
            pw_input.send_keys(char)
            sleep(0.02)

        login_bttn = self.driver.find_element(By.CLASS_NAME, 'submit').find_element(By.TAG_NAME, 'input')
        login_bttn.click()
        sleep(2)


    def go_to_menu(self) -> None:

        first_menu_clickable = self.driver.find_element(By.CSS_SELECTOR, '.nav-item.Suporte.RH.webAPP')
        first_menu_clickable.click()
        sleep(2)

        second_menu_clickable = self.driver.find_element(By.CSS_SELECTOR,  '.nav-item.Suporte.RH.webAPP .sub-menu li')
        second_menu_clickable.click()
        sleep(1)


    def add_filters(self, date_to_filter: str | None) -> bool:
        """
        Aplica os filtros rápidos de busca;
        Caso não haja nenhum registros em dado status, não ira aparecer para ser selecionável
        E o retorno será False, caso haja registros em algum status buscado, retorna True
        """

        wait = WebDriverWait(self.driver, 15)

        sleep(2)
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "iframe_menu_administrador")))

        status_filters_tab = self.driver.find_element(By.ID, 'id_tab_status_link')
        all_status_filters_elemnt: list[WebElement] = status_filters_tab.find_elements(By.CLASS_NAME, 'scGridRefinedSearchCampo')
        apply_filters_bttn: WebElement = self.driver.find_element(By.ID, 'id_toolbar_status') \
                                                           .find_element(By.ID, 'app_int_search_status')
        
        any_necessary_filter: bool = False
        for elemnt in all_status_filters_elemnt:
            label_text = elemnt.find_element(By.CLASS_NAME, 'scGridRefinedSearchCampoFont')
            clickable_checkbox = elemnt.find_element(By.CLASS_NAME, 'scAppDivToolbarInput')

            text = label_text.get_attribute('textContent').strip().split('  ')[0]

            if text in self.filters:
                self.driver.execute_script("arguments[0].click();", clickable_checkbox)
                any_necessary_filter = True
                # sleep(1)

        if any_necessary_filter is False:
            print(f"0 registros encontrados com os status buscados:\n {'\n'.join(self.filters)} \n")
            return False

        sleep(2)
        self.driver.execute_script("arguments[0].click();", apply_filters_bttn)
        sleep(2)

        return True

        # Se tiver a data, filtra por registros com abertura nessa data
        # if date_to_filter is not None:

        #     select_search_elmnt = self.driver.find_element(By.ID, 'fast_search_f0_top')
        #     select_search = Select(select_search_elmnt)
        #     select_search.select_by_value('data_abertura')

        #     # Data só funciona se for no formato dd/mm/YYYY
        #     date_to_filter = '-'.join(date_to_filter.split('/')[::-1])

        #     sleep(1)
        #     search_input = self.driver.find_element(By.ID, 'SC_fast_search_top')
        #     search_input.clear()
        #     search_input.send_keys(date_to_filter)

        #     sleep(1)
        #     search_bttn = self.driver.find_element(By.ID, 'SC_fast_search_submit_top')
        #     self.driver.execute_script("arguments[0].click();", search_bttn)
        #     sleep(5)


    def export_and_download_json(self) -> None:

        csv_clickable_label = self.driver.find_element(By.CSS_SELECTOR, '#div_json_top > a')
        self.driver.execute_script("arguments[0].click();", csv_clickable_label)

        # self.driver.switch_to.default_content()
        # self.driver.switch_to.frame('iframe_menu_administrador')
        self.driver.switch_to.frame('TB_iframeContent')

        csv_create_bttn = self.driver.find_element(By.ID, 'bok')
        self.driver.execute_script("arguments[0].click();", csv_create_bttn)

        self.driver.switch_to.default_content()
        self.driver.switch_to.frame('iframe_menu_administrador')
        sleep(2)

        csv_download_bttn = self.driver.find_element(By.ID, 'idBtnDown')
        self.driver.execute_script("arguments[0].click();", csv_download_bttn)

        shutil.rmtree(self.download_temp_dir_path)
        csv_download_bttn.click()
    

    def get_temp_json_df(self) -> DataFrame:
        sleep(2)
        return pd.read_json('./data/greif/temp/chamados_suporte_enduser_retorno_new.json')
            
    
    def normalize_temp_json(self, df: DataFrame) -> DataFrame:

        df = df.join(pd.json_normalize(df['Status / Prazos']))
        df.drop(columns='Status / Prazos', inplace=True)

        df = df.join(pd.json_normalize(df['Protocolo - Funcionário - Matrícula ']))
        df.drop(columns='Protocolo - Funcionário - Matrícula ', inplace=True)

        df = df.join(pd.json_normalize(df['Assunto - Tópicos - Descrição']))
        df.drop(columns='Assunto - Tópicos - Descrição', inplace=True)

        df = df.join(pd.json_normalize(df['Redirecionamentos']))
        df.drop(columns='Redirecionamentos', inplace=True)

        df['Data Abertura'] = df['Data Abertura'].astype(str).str.strip()
        df[['Data Abertura', 'hora_inicio']] = df['Data Abertura'].str.strip().str.split(' ', n=1, expand=True)

        df.drop(columns=df.columns[0], inplace=True)
        
        return df
    

    def download_others_infos_xlsx(self, tickets_ids: Series) -> None:
        """
        Baixa os xlsx individualmente baseado no id de cada ticket/registro
        """
        wait = WebDriverWait(self.driver, 50)

        for i, ticket_id in enumerate(tickets_ids):

            print(f'{ticket_id}: Realizando de extrações adicionais do ticket Nº{i}')
            
            # Procura o ticket pelo id na barra de pesquisa
            select_search_elmnt = self.driver.find_element(By.ID, 'fast_search_f0_top')
            
            select_search = Select(select_search_elmnt)
            select_search.select_by_value('id_ticket')


            sleep(1)
            search_input = self.driver.find_element(By.ID, 'SC_fast_search_top')
            search_input.clear()
            search_input.send_keys(ticket_id)

            sleep(1)
            search_bttn = self.driver.find_element(By.ID, 'SC_fast_search_submit_top')
            self.driver.execute_script("arguments[0].click();", search_bttn)
            sleep(12)

            # # Pega a região pra eventualmente ser pego o responsável por ela
            # local_info: WebElement = self.driver.find_element(By.CLASS_NAME, 'scGridFieldOdd') \
            #                                     .find_elements(By.TAG_NAME, 'td')[13] \
            #                                     .find_element(By.TAG_NAME, 'span')
            # local_info_text: str = local_info.text

            # register_row: WebElement = self.driver.find_element(By.CLASS_NAME, 'scGridFieldOdd')
            register_row: WebElement = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'scGridFieldOdd')))
            edit_register_bttn = register_row.find_element(By.ID, 'bedit')
            self.driver.execute_script("arguments[0].click();", edit_register_bttn)

            # sleep(4)
            # status_select = self.driver.find_element(By.ID, 'id_sc_field_status')
            # select = Select(status_select)
            # select.select_by_visible_text("Redirecionar Responsável")

            # # Adiciona o responável da região
            # matched_manage_value: str = self.get_corresponding_manager_by_location(local_info_text)
            # sleep(2)

            # # matched_manage_value = 'Expert'
            # manager_select = self.driver.find_element(By.ID, 'id_sc_field_id_responsavel')
            # select = Select(manager_select)
            # select.select_by_value(matched_manage_value)
            # sleep(2)


            # # Adiciona a respota ao estado (atestado lançado, duplicado, etc)
            # self.driver.switch_to.frame('nmsc_iframe_liga_sub_form_db_suporte_historico')

            # add_response_bttn = self.driver.find_element(By.ID, 'sc_b_new_t')
            # self.driver.execute_script("arguments[0].click();", add_response_bttn)
            # sleep(2)

            # response_text_field = self.driver.find_element(By.ID, 'id_sc_field_resposta_1')
            # response_text_field.send_keys('Atestado lançado')
            # # sleep(2)

            # send_response_bttn = self.driver.find_element(By.ID, 'sc_ins_line_1')
            # self.driver.execute_script("arguments[0].click();", send_response_bttn)
            sleep(1)


            # Muda iframe e baixa o arquivo com as demais infos do usuário
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame('iframe_menu_administrador')
            xlsx_export_bttn = self.driver.find_element(By.ID, 'sc_export_top')
            self.driver.execute_script("arguments[0].click();", xlsx_export_bttn)

            self.driver.switch_to.frame('TB_iframeContent')

            sleep(1)
            xlsx_download_bttn = self.driver.find_element(By.ID, 'idBtnDown')
            self.driver.execute_script("arguments[0].click();", xlsx_download_bttn)

            sleep(1)
            xlsx_download_bttn = self.driver.find_element(By.ID, 'idBtnBack')
            self.driver.execute_script("arguments[0].click();", xlsx_download_bttn)

            self.driver.switch_to.default_content()
            self.driver.switch_to.frame('iframe_menu_administrador')
            sleep(1)

            # save_infos_bttn = self.driver.find_element(By.ID, 'sc_b_upd_t')
            # self.driver.execute_script("arguments[0].click();", save_infos_bttn)

            xlsx_download_bttn = self.driver.find_element(By.ID, 'sc_b_sai_t')
            self.driver.execute_script("arguments[0].click();", xlsx_download_bttn)
            sleep(1)


    def merge_infos_into_df(self, df: DataFrame) -> DataFrame:

        df['Funcionário'] = df['Funcionário'].str.strip()

        xlsx_temp_files = [
            f for f in os.listdir(self.download_temp_dir_path)
            if f.endswith('xlsx') and os.path.isfile(os.path.join(self.download_temp_dir_path, f))
        ]

        all_merged_dfs: list[DataFrame] = []
        for file in xlsx_temp_files:

            file_path: str = os.path.join(self.download_temp_dir_path, file)

            func_df: DataFrame = pd.read_excel(file_path)
            func_df['Cod Funcionario'] = func_df['Cod Funcionario'].str.strip()

            # df['Data Abertura'] = pd.to_datetime(df['Data Abertura']).dt.floor('D')
            # func_df['Atestado Data Inicio'] = pd.to_datetime(df['Atestado Data Inicio']).dt.floor('D')



            func_df['Quantidade de dias'] = (
                func_df['Quantidade de dias']
                .fillna('')            # substitui NaN
                .astype(str)           # força string
                .str.strip()           # tira espaços
                .str.split(' ').str[0] # pega só a primeira parte
            )

            print(df)
            
            # df[['Data Encerramento', 'hora_fim']] = df['Data Encerramento'].str.strip().str.split(' ', n=1, expand=True)
            # df['Data Encerramento'] = df['Data Abertura'] + pd.to_timedelta(func_df['Quantidade de dias'], unit='D') \
            #                           if ['Data Encerramento'] is None else df['Data Encerramento']
            # df['Data Encerramento'] = df['Data Encerramento'].astype(str).str.strip()

            all_merged_dfs.append(pd.merge(df, func_df, left_on='Funcionário', right_on='Cod Funcionario', how='inner'))

        merged_df = pd.concat(all_merged_dfs, ignore_index=True)

        return merged_df


    def get_corresponding_manager_by_location(self, local_name: str) -> str:

        # Definir dict com base no tópico 5. da greif
        manager_dict = {
            "aratu": "40", # Tatiana Leal
            "araucaria": "54", #: Michele Carolina Alves
            "esteio": "22", #: Thiago Nunes
            "londrina": "48", #: Simone Yoshitake 
            "manaus": "19", #: Andria Carvalho
            "sp": "164", #: Jennifer Santos (Greif SP)
            "rj": "27" # Thayrine Leite
        }
        
        for manager_local_name in manager_dict.keys():

            if manager_local_name in local_name.lower():
                return manager_dict[manager_local_name]
            

    def pre_treat(self, df: DataFrame) -> DataFrame:
        df.loc[df['Código(s) CID'].astype(str).str.strip() == 'Não informado', 'Código(s) CID'] = ''
        return df

