import os
from time import sleep
import datetime as dt
import pandas as pd
from pandas import DataFrame
import regex as re
import zipfile

import requests as req

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, SessionNotCreatedException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

from ...helpers.tools.date_formatter import DateFormatter
from ...helpers.tools.get_credentials import get_credentials


class SocSeleniumScrapying:

    driver: WebDriver
    credentials: dict
    
    start_date: str
    end_date: str


    def __init__(self, client_name: str):
        
        self.download_dir_path = os.path.join(os.getcwd(),'data','soc')
        self.download_temp_dir_path = os.path.join(self.download_dir_path, 'temp')

        os.makedirs(self.download_dir_path, exist_ok=True)
        print(f"Pasta de downloads garantida em: {self.download_dir_path}")

        os.makedirs(self.download_temp_dir_path, exist_ok=True)
        print(f"Pasta de download temporária garantida em: {self.download_temp_dir_path}")
       
        # Deleta todos os arquivos da pasta temporária se houver algum 
        if os.path.exists(self.download_temp_dir_path):
            for file in os.listdir(self.download_temp_dir_path):
                path_file = os.path.join(self.download_temp_dir_path, file)
                # if os.path.isfile(path_file):
                os.remove(path_file)
                # elif os.path.
        
        chrome_options = Options()
        chrome_options.add_experimental_option(
            "prefs", {
                "download.default_directory": os.path.abspath(self.download_temp_dir_path),
                "download.prompt_for_download": False,
            }
        )
        
        # Inicia o acesso ao navegador
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()

        self.client_name = client_name
        self.credentials = get_credentials('soc')


    def run(self, start_date: str, end_date: str) -> DataFrame | None:
        
        self.start_date = start_date
        self.end_date = end_date

        try:
            self.do_login()
            self.go_to_menu()
            self.set_filters()
            
            self.request_and_download_xlsx()
            self.unzip_file()
            
            df: DataFrame = self.relatory_df()
            return df
        
        except FileNotFoundError as e:
            print("Nenhum arquivo necessário foi baixado ou encontrado...")
            return None
    
        except Exception as e:
            print(f"Ocorreu um erro: {e}")

        finally:
            self.driver.quit()
            print("Navegador fechado.")


    def do_login(self) -> None:

        url: str = 'https://sistema.soc.com.br/WebSoc/'
        
        self.driver.get(url)

        username_input = self.driver.find_element(By.ID, 'usu')
        for char in self.credentials['login_email']:
            username_input.send_keys(char)
            sleep(0.02)

        pw_input = self.driver.find_element(By.ID, 'senha')
        for char in self.credentials['login_pw']:
            pw_input.send_keys(char)
            sleep(0.02)
        
        pw_input: WebElement = self.driver.find_element(By.ID, 'empsoc')
        self.driver.execute_script(f"arguments[0].value = '{self.credentials['login_id']}';", pw_input)
        
        login_bttn = self.driver.find_element(By.ID, 'bt_entrar')
        login_bttn.click()
        sleep(4)
        
        any_alerts_items: WebElement = self.driver.find_elements(By.CLASS_NAME, 'modalAlerta')
        if len(any_alerts_items) > 0:
            raise SessionNotCreatedException('Falha ao realizar login no SOC')
        

    def go_to_menu(self) -> None:       
        
        wait = WebDriverWait(self.driver, 40)
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "socframe")))
        
        client_code: str
        match self.client_name:
            case 'pluri':
                client_code = '592252'
            case 'leroy':
                client_code = '560416'
            case 'viva':
                client_code = '592279'
            case _:
                raise ValueError('Erro de parametro: "client_name" é inválido, favor passar como ou "pluri", "leroy" ou "viva"')
            
        client_code_input: WebElement = self.driver.find_element(By.ID, 'cproemp')
        client_code_input.send_keys(client_code)
        sleep(2)
        
        search_client_code_bttn: WebElement = self.driver.find_element(By.ID, 'procuraModalBtn')
        search_client_code_bttn.click()
        sleep(2)
        
        box_lista_emop: WebElement = self.driver.find_element(By.ID, 'listaemop')
        client_reference_row: WebElement = box_lista_emop.find_elements(By.TAG_NAME, 'tr')[0]
        client_reference: WebElement = client_reference_row.find_elements(By.TAG_NAME, 'a')[0]
        client_reference.click()
        sleep(2)
        
        self.driver.switch_to.default_content()
        menu_bttn: WebElement = self.driver.find_element(By.ID, 'botao')
        menu_bttn.click()
        
        medic_license_sub_menu_bttn: WebElement = self.driver.find_element(By.XPATH, '//tr[@bgcolor="#ffffff" and .//span[contains(text(), "Absenteísmo") or contains(text(), "Absenteismo")]]')
        onclick_code = medic_license_sub_menu_bttn.get_attribute("onclick")
        self.driver.execute_script(onclick_code)


    def set_filters(self) -> None:

        wait = WebDriverWait(self.driver, 40)

        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "socframe")))

        date_creation_bttn: WebElement = self.driver.find_element(By.XPATH, '//li[@data-valor="dataCriacao"]')
        date_creation_bttn.click()
        
        date_creation_input: WebElement = self.driver.find_element(By.ID, 'ipt-data-periodo')
        if self.start_date == self.end_date:
            self.driver.execute_script(f"arguments[0].value = '{self.start_date}';", date_creation_input)
        else:
            self.driver.execute_script(f"arguments[0].value = '{self.start_date} - {self.end_date}';", date_creation_input)
        
        classification_dropdown: WebElement = self.driver.find_element(By.ID, 'ipt-text-campo-lista-classificacao')
        classification_dropdown.click()
        
        classification_dropdown_options: WebElement = self.driver.find_element(By.ID, 'lista-classificacao')
        list_classification_option: WebElement = classification_dropdown_options.find_element(By.XPATH, '//li[@data-valor="6"]')
        list_classification_option.click()
        # self.driver.execute_script("arguments[0].value = 'Listagem';", classification_dropdown)
        
        # input('.............')
        all_situations_clickable: WebElement = self.driver.find_element(By.ID, 'spn-checkbox-lista-check-tipo-exame-ipt-check-rel007form-filtrarfuncionario-0')
        all_situations_clickable.click()
        
        show_name_checkbox: WebElement = self.driver.find_element(By.XPATH, '//input[@name="rel007Form.aparecerNomeFuncionario"]')
        self.driver.execute_script("arguments[0].click();", show_name_checkbox)
        
        # input('...')
        
        
    def request_and_download_xlsx(self) -> None:
        
        generate_xlsx_bttn: WebElement = self.driver.find_element(By.ID, 'btn-gerar-excel')
        generate_xlsx_bttn.click()
        sleep(2)
        
        toast_elmnt: WebElement = self.driver.find_element(By.ID, 'toast-container')
        relatory_process_html = toast_elmnt.find_element(By.XPATH, '//div[contains(@class, "toast") and contains(., "Em processamento cód.")]')
        relatory_process_code = re.search(r'cód\.\s*(\d+)', relatory_process_html.text).group(1)
        
        consult_process_bttn = toast_elmnt.find_element(By.TAG_NAME, 'button')
        consult_process_bttn.click()
        sleep(4)
        
        relatory_row: WebElement = self.driver.find_element(By.XPATH, f'//tr[@data-codigo="{relatory_process_code}"]')
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", relatory_row)
        sleep(60)
        
        # relatory_link: WebElement = relatory_row.find_element(By.XPATH, '//td[@class="center-align"]')
        # WebDriverWait(self.driver, 10).until(
        #     EC.visibility_of_element_located((By.XPATH, '//td[@class="center-align"]'))
        # )
        
        relatory_process_status_elmnt: WebElement = relatory_row.find_element(By.CLASS_NAME, 'situacao')
        download_clickable = relatory_process_status_elmnt.find_element(By.XPATH, '//a[@data-programa-download="pr043"]')
        self.driver.execute_script("arguments[0].click();", download_clickable)
        
        # sleep(10)
        # location = download_clickable.location
        # size = download_clickable.size
        
        # window_position = self.driver.get_window_position()
        # window_x = window_position['x']
        # window_y = window_position['y']
        # print(size)

        # # coordenadas absolutas na tela
        # screen_x = window_x + location['x'] + size['width']/2
        # screen_y = window_y + location['y'] + size['height']/2
        
        # import pyautogui
        # pyautogui.click(screen_x, screen_y)
        
        sleep(2)
        

    def unzip_file(self) -> None:
        
        dir_path = self.download_temp_dir_path
        files = os.listdir(dir_path)
        zip_files = [f for f in files if f.endswith(".zip")]

        if not zip_files:
            raise FileNotFoundError("Nenhum arquivo .zip encontrado em " + dir_path)

        file_path = os.path.join(dir_path, zip_files[0])
        print("Extraindo:", file_path)

        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(dir_path)

        print("Extração concluída.")
                
    
    def relatory_df(self) -> DataFrame | None:
        
        dir_path = self.download_temp_dir_path
        files = os.listdir(dir_path)
        xls_files = [f for f in files if f.endswith(".xls")]

        if not xls_files:
            raise FileNotFoundError("Nenhum arquivo .xls encontrado em " + dir_path)

        file_path = os.path.join(dir_path, xls_files[0])

        df = pd.read_excel(file_path, skiprows=3)
        
        return df        