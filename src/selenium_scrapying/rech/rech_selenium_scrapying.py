import os
from time import sleep
import datetime as dt
import pandas as pd
from pandas import DataFrame

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from ...helpers.tools.date_formatter import DateFormatter

from ...helpers.tools.get_credentials import get_credentials



class RechSeleniumScrapying:

    driver: WebDriver
    credentials: dict
    any_scraping_error: bool = False


    def __init__(self):
        # Inicia o acesso ao navegador
        self.driver = webdriver.Chrome()
        self.credentials = get_credentials('rech')

        
    def run(self) -> DataFrame | None:

        try:
            self.do_login()
            self.go_to_menu()

            self.set_filter()
            pending_num: int = self.get_pending_num()

            scraped_data = self.get_func_data(pending_num)
            df: DataFrame = pd.DataFrame(scraped_data)
            
            if df.empty:
                return None
            
            modelo_1_df = self.read_modelo_1()
            df['CPF'] = self.merge_df_with_modelo_1(df, modelo_1_df)['CPF']

            return df

        except Exception as e:
            import traceback
            traceback.print_exc()
            
            print(f"Ocorreu um erro: {e.with_traceback(e.__traceback__)}")
            self.any_scraping_error = True

        finally:
            self.driver.quit()
            print("Navegador fechado.")


    def some_scraping_error_occurred(self) -> bool:
        """Informa se algum erro ocorreu durante o scraping"""
        return self.any_scraping_error 
        

    def do_login(self) -> None:

        url: str = 'https://platform.senior.com.br/login/?redirectTo=https%3A%2F%2Fplatform.senior.com.br%2Fsenior-x%2F&tenant=nossa-gente.com.br'
        
        self.driver.get(url)

        username_input = self.driver.find_element(By.ID, 'username-input-field')
        for char in self.credentials['username']:
            username_input.send_keys(char)
            sleep(0.02)

        sleep(2)
        next_bttn = self.driver.find_element(By.ID, 'nextBtn')
        next_bttn.click()

        sleep(2)
        pw_input = self.driver.find_element(By.ID, 'password-input-field')
        for char in self.credentials['pw']:
            pw_input.send_keys(char)
            sleep(0.02)
        
        sleep(2)
        login_bttn = self.driver.find_element(By.ID, 'loginbtn')
        login_bttn.click()
        sleep(8)


    def go_to_menu(self) -> None:       

        wait = WebDriverWait(self.driver, 30)

        wait.until(EC.presence_of_element_located((By.ID, 'menu-item-Favoritos')))
        menu_favs_clickable = self.driver.find_element(By.ID, 'menu-item-Favoritos')
        menu_favs_clickable.click()
        sleep(3)

        wait.until(EC.presence_of_element_located((By.ID, 'menu-item-Favoritos')))
        menu_favs_clickable_2 = self.driver.find_element(By.ID, 'apps-menu-item-0')
        menu_favs_clickable_2.click()
        sleep(3)
        
        # while True: pass

        # wait.until(EC.presence_of_element_located((By.ID, 'menu-item-Favoritos')))
        # menu_favs_clickable_3 = self.driver.find_element(By.ID, 'apps-menu-item-0')
        # menu_favs_clickable_3.click()
        # sleep(3)

    
    def get_pending_num(self) -> int:

        self.driver.switch_to.default_content()

        wait = WebDriverWait(self.driver, 40)
        sleep(8)

        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "custom_iframe")))
        
        # Pega todos os spans com o número de registros em cada filtro
        # spans: list[WebElement] = self.driver.find_elements(By.CSS_SELECTOR, '.count.ng-star-inserted')
        # ui-g-12 ng-star-inserted active
        pendent_quick_selector: WebElement = self.driver.find_element(By.CSS_SELECTOR, '.ui-g-12.ng-star-inserted.active')
        
        # spans: list[WebElement] = self.driver.find_elements(By.CSS_SELECTOR, '.ui-g-12.ng-star-inserted')
        # spans: list[WebElement] = self.driver.find_elements(By.CSS_SELECTOR, '.count.ng-star-inserted')
        
        try:
            # Span da quantidade de pendentes
            pending_num_span: WebElement =  pendent_quick_selector.find_element(By.CSS_SELECTOR, '.count.ng-star-inserted')
            pending_num = int(pending_num_span.text)
        except NoSuchElementException:
            pending_num = 0
            
        self.driver.switch_to.default_content()

        return pending_num


    def set_filter(self) -> None:

        wait = WebDriverWait(self.driver, 40)

        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "custom_iframe")))


        filter_bttn = wait.until(EC.element_to_be_clickable((By.ID, "filterButton")))
        filter_bttn.click()
        sleep(6)

        date_formatter = DateFormatter(date_format='%Y-%m-%d')
        today = date_formatter.today()
        
        # Filtro por data inicial
        # period_initial_input = wait.until(EC.visibility_of_element_located((By.ID, 'periodInitial')))

        # script_js = f"arguments[0].value = '{data_formatada}';"
        # self.driver.execute_script(script_js, period_initial_input)

        # justificativas
        process_aimed = 'Justificativa de Ausências'

        input_process = self.driver.find_element(By.ID, 'process_task-autocomplete')
        input_process.send_keys(process_aimed)
        sleep(1)
        input_process.send_keys(Keys.TAB)
        sleep(1)

        apply_filters_bttn = self.driver.find_element(By.ID, 's-button-3')
        self.driver.execute_script("arguments[0].click();", apply_filters_bttn)
        sleep(1)

        # Try/cacth para fechar o modal de filtro, se já foi fechado caí na excessão
        try:
            close_filter_form_bttn = self.driver.find_element(By.CSS_SELECTOR, "span.close_btn.pi.pi-times")
            self.driver.execute_script("arguments[0].click();", close_filter_form_bttn)
        except NoSuchElementException:
            pass

        # Opcional: Volte para a página principal se precisar interagir com outros elementos


    def get_func_data(self, pending_num: int) -> list[list[dict]]:

        if pending_num == 0:
            print('Não há atestados pendentes...\n')
            return

        wait = WebDriverWait(self.driver, 10)

        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "custom_iframe")))


        last_items_in_box_qnt = 0
        while last_items_in_box_qnt != (pending_num + 1): 

            try:
                # while 1:...
                # ui-accordion-content
                # ui-accordiontab-0-content                
                # ui-accordiontab-2-content
                # ui-accordiontab-2
                # data_box_items: list[WebElement] = self.driver.find_element(By.ID, 'ui-accordiontab-0-content') \
                data_box_items: list[WebElement] = (
                    self.driver.find_element(
                        By.XPATH,
                        "//*[starts-with(@id, 'ui-accordiontab-') and contains(@id, '-content')]"
                    )
                    .find_element(By.TAG_NAME, 'div')
                    .find_elements(By.XPATH, "./*")
                )
                
                class_str = data_box_items[-2].get_attribute('class')
                class_list = class_str.split()

                if 'see-more' in class_list:
                    
                    # 1. Faz o iframe da Tracksale ignorar cliques e sumir da frente
                    self.driver.execute_script("""
                        var iframe = document.getElementById('tracksale-iframe');
                        if (iframe) {
                            iframe.style.pointerEvents = 'none';
                            iframe.style.display = 'none';
                            iframe.style.visibility = 'hidden';
                        }
                    """)
                    
                    data_box_items[-2].click()

                last_items_in_box_qnt = len(data_box_items)

            except NoSuchElementException as e:
                raise e
            

        people_list = []

        for i in range(len(data_box_items) - 1):

            data_box_items: list[WebElement] = (
                self.driver.find_element(
                    By.XPATH,
                    "//*[starts-with(@id, 'ui-accordiontab-') and contains(@id, '-content')]"
                )
                .find_element(By.TAG_NAME, 'div')
                .find_elements(By.XPATH, "./*")
            )

            item = data_box_items[i]
            
            sleep(0.5)

            clickable = item.find_element(By.ID, 'clickable panel')

            part_with_all_infos: list[WebElement] = clickable.find_elements(By.XPATH, "./*")
            
            ticket_id: str = part_with_all_infos[0].find_element(By.TAG_NAME, 'b').text.strip()[1:]
            # print(ticket_id)

            div_with_all_infos: WebElement = part_with_all_infos[1].find_element(By.TAG_NAME, "div") \
                                                                .find_elements(By.XPATH, "./*")[0]

            ticket_open_date: str = part_with_all_infos[-1].find_element(By.TAG_NAME, 'span').text
           
            title_content = div_with_all_infos.get_attribute('title')
            title_splited = title_content.split(', ')
            items_splited = [item.split(':') for item in title_splited]

            items_splited = []
            for item in title_splited:
                if ':' in item:
                    items_splited.append([item_splitted.strip() for item_splitted in item.split(':', 1)])

            items_splited.append(['data_abertura', ticket_open_date])
            items_splited.append(['ticket_id', ticket_id])
            items_dicted = dict(items_splited)

            people_list.append(items_dicted)        

        return people_list
    

    def reply_ticket(self, ticket_id: str): 

        wait = WebDriverWait(self.driver, 40)

        # input('Aguardando pra ler novo registro...')
        
        self.filter_by_ticket_id(ticket_id)

        # sleep(8)
        item_row_box: WebElement = wait.until(EC.visibility_of_element_located((By.ID, 'ui-accordiontab-1-content')))
        # item_row_box: WebElement = self.driver.find_element(By.ID, 'ui-accordiontab-1-content')
        item_row = item_row_box.find_element(By.TAG_NAME, 'div') \
                           .find_elements(By.XPATH, "./*")[0]
        
        clickable = item_row.find_element(By.ID, 'clickable panel')
        self.driver.execute_script("arguments[0].click();", clickable)
        sleep(4)

        # Página do registro
        self.driver.switch_to.default_content()
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "custom_iframe")))
        sleep(4)

        nav_tabs_ul = self.driver.find_element(By.CSS_SELECTOR, '.nav.nav-tabs')    
        nav_tab_li = nav_tabs_ul.find_element(By.CSS_SELECTOR, 'li[index="2"]')
        nav_tab_clickable = nav_tab_li.find_element(By.TAG_NAME, 'a')
        self.driver.execute_script("arguments[0].click();", nav_tab_clickable)
        sleep(4)
        
        # Volta pra página do menu de listagens 
        self.driver.back()
        sleep(2)


    def filter_by_ticket_id(self, ticket_id: str):

        wait = WebDriverWait(self.driver, 45)

        self.driver.switch_to.default_content()
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "custom_iframe")))

        sleep(3)
        filter_bttn = wait.until(EC.element_to_be_clickable((By.ID, "filterButton")))
        # filter_bttn = self.driver.find_element(By.ID, "filterButton")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", filter_bttn)
        self.driver.execute_script("arguments[0].click();", filter_bttn)
        sleep(5)

        # ticket_id_input = wait.until(EC.visibility_of_element_located((By.ID, 'processInstanceId_task')))
        ticket_id_input = self.driver.find_element(By.ID, 'processInstanceId_task')
        ticket_id_input.clear()
        ticket_id_input.send_keys(ticket_id)
        sleep(3)

        apply_filters_bttn = self.driver.find_element(By.ID, 's-button-3')
        self.driver.execute_script("arguments[0].click();", apply_filters_bttn)
        
    # Comentado pois usa o os.environ e tá dando bo no docker
    # def read_modelo_1(self) -> DataFrame:
    #     """_Retorna um Dataframe com todas as modelos 1 da Rech concatenadas_

    #     Returns:
    #         DataFrame: _Dataframe com todas as modelo 1 da Rech concatenadas_
    #     """
        
    #     sharepoint_path: str = os.path.join(os.environ['USERPROFILE'], 'EXPERT GESTAO OCUPACIONAL E PREVIDENCIARIA LTDA', 'Expert Ocupacional Externo - SmartReports')
    #     dir_path: str = os.path.join(sharepoint_path, 'Modelo I - Clientes com SOC', 'Grupo Rech')
    #     filenames: list[str] = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
        
    #     modelo_1_all_dfs: list[DataFrame] = [pd.read_excel(os.path.join(dir_path, f), skiprows=1) for f in filenames]
    #     modelo_1_df: DataFrame = pd.concat(modelo_1_all_dfs, ignore_index=True)
        
    #     return modelo_1_df
    
    
    def merge_df_with_modelo_1(self, df: DataFrame, modelo_1_df: DataFrame) -> DataFrame:

        df.set_index('Colaborador')
        modelo_1_df.set_index('Nome Funcionário')
        
        df_filled = df.combine_first(modelo_1_df).reset_index()
        
        return df_filled
        