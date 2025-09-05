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



class GreifSeleniumScrapying:

    driver: WebDriver
    filters: list[str] = ['Pendente', 'Responsável Redirecionado']  
    menu_window_handler: str
    
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


    def run(self) -> list[list[dict]]:

        try:

            self.do_login()
            self.go_to_menu()
            self.add_filter()
            self.export_and_download_json()

            df: DataFrame = self.get_temp_json_df()
            df = self.normalize_temp_json(df)

            tickets_ids: Series = df.loc[:,'Número Chamado']
            self.get_others_infos_by_tickets_ids(tickets_ids)

            df = self.merge_infos_into_df(df)

            return df

        except Exception as e:
            print(f"Ocorreu um erro: {e.with_traceback}")

        finally:
            self.driver.quit()
            print("Navegador fechado.")


    def do_login(self) -> None:

        url: str = 'https://app.plugbeneficios.com.br/dashboard_painel_RHlocal/?login=expert'
        
        self.driver.get(url)
        sleep(1)

        username_input = self.driver.find_element(By.ID, 'id_sc_field_login')
        username_input.clear()
        username_input.send_keys('Expert')
        sleep(1)

        pw_input = self.driver.find_element(By.ID, 'id_sc_field_pswd')
        pw_input.send_keys('expert24#')
        sleep(1)

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


    def add_filter(self) -> None:

        wait = WebDriverWait(self.driver, 15)

        sleep(5)
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "iframe_menu_administrador")))

        status_filters_tab = self.driver.find_element(By.ID, 'id_tab_status_link')
        all_status_filters_elemnt: list[WebElement] = status_filters_tab.find_elements(By.CLASS_NAME, 'scGridRefinedSearchCampo')
        apply_filters_bttn: WebElement = self.driver.find_element(By.ID, 'id_toolbar_status') \
                                                           .find_element(By.ID, 'app_int_search_status')

        for elemnt in all_status_filters_elemnt:
            label_text = elemnt.find_element(By.CLASS_NAME, 'scGridRefinedSearchCampoFont')
            clickable_checkbox = elemnt.find_element(By.CLASS_NAME, 'scAppDivToolbarInput')

            text = label_text.get_attribute('textContent').strip().split('  ')[0]

            if text in self.filters:
                self.driver.execute_script("arguments[0].click();", clickable_checkbox)
                sleep(1)

        sleep(2)
        self.driver.execute_script("arguments[0].click();", apply_filters_bttn)


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

        df['Prazo'] = df['Prazo'].str.strip().str.split(' ').str[0].astype('Int64')

        df['Data Abertura'] = pd.to_datetime(df['Data Abertura']).dt.floor('D')
        df['Data Encerramento'] = df['Data Abertura'] + pd.to_timedelta(df['Prazo'], unit='D')

        df.drop(columns=df.columns[0], inplace=True)
        
        return df
    

    def get_others_infos_by_tickets_ids(self, tickets_ids: Series) -> None:

        for ticket_id in tickets_ids:
            
            sleep(2)
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

            sleep(1)
            register_row: WebElement = self.driver.find_elements(By.CLASS_NAME, 'scGridFieldOdd')[0]

            edit_register_bttn = register_row.find_element(By.ID, 'bedit')
            self.driver.execute_script("arguments[0].click();", edit_register_bttn)

            sleep(8)
            xlsx_export_bttn = self.driver.find_element(By.ID, 'sc_export_top')
            self.driver.execute_script("arguments[0].click();", xlsx_export_bttn)

            # sleep(1)
            self.driver.switch_to.frame('TB_iframeContent')

            sleep(1)
            xlsx_download_bttn = self.driver.find_element(By.ID, 'idBtnDown')
            self.driver.execute_script("arguments[0].click();", xlsx_download_bttn)

            sleep(1)
            xlsx_download_bttn = self.driver.find_element(By.ID, 'idBtnBack')
            self.driver.execute_script("arguments[0].click();", xlsx_download_bttn)

            self.driver.switch_to.default_content()
            self.driver.switch_to.frame('iframe_menu_administrador')

            sleep(2)
            xlsx_download_bttn = self.driver.find_element(By.ID, 'sc_b_sai_t')
            self.driver.execute_script("arguments[0].click();", xlsx_download_bttn)


    def merge_infos_into_df(self, df: DataFrame) -> DataFrame:

        xlsx_temp_files = [
            f for f in os.listdir(self.download_temp_dir_path)
            if f.endswith('xlsx') and os.path.isfile(os.path.join(self.download_temp_dir_path, f))
        ]


        all_merged_dfs: list[DataFrame] = []

        for file in xlsx_temp_files:

            file_path: str = os.path.join(self.download_temp_dir_path, file)
            print(file_path)

            func_df: DataFrame = pd.read_excel(file_path)
            print(func_df)
            print(df)
            print(func_df.columns)

            all_merged_dfs.append(pd.merge(df, func_df, left_on='Funcionário', right_on='Cod Funcionario'))

        merged_df = pd.concat(all_merged_dfs, ignore_index=True)

        return merged_df


