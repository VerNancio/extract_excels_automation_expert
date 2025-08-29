import os
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC



class GreifSeleniumScrapying:

    driver: WebDriver
    filters: list[str] = ['Pendente', 'Responsável Redirecionado']
    
    def __init__(self):
        self.download_dir = "./data/greif/"
        self.download_temp_dir = f'{self.download_dir}/temp/'
        
        os.makedirs(self.download_dir, exist_ok=True)
        # print(f"Pasta de downloads garantida em: {self.download_dir}")

        os.makedirs(self.download_temp_dir, exist_ok=True)
        print(f"Pasta de download temporária garantida em: {self.download_temp_dir}")
        
        chrome_options = Options()
        chrome_options.add_experimental_option(
            "prefs", {
                "download.default_directory": os.path.abspath(self.download_temp_dir),
                "download.prompt_for_download": False,
            }
        )
        
        self.driver = webdriver.Chrome(options=chrome_options)


    def run(self) -> list[list[dict]]:

        try:

            self.do_login()
            self.go_to_menu()
            self.add_filter()
            self.export_and_download_csv()

            # scraped_data = self.get_func_data()

            # return scraped_data

        except Exception as e:
            print(f"Ocorreu um erro: {e}")

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
        print(login_bttn.get_attribute('outerHTML'))
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

            print(f'{self.filters} - {text}')
            if text in self.filters:
                self.driver.execute_script("arguments[0].click();", clickable_checkbox)
                sleep(1)

        sleep(2)
        self.driver.execute_script("arguments[0].click();", apply_filters_bttn)

            
    def export_and_download_csv(self) -> None:

        csv_clickable_label = self.driver.find_element(By.CSS_SELECTOR, '#div_csv_top > a')
        self.driver.execute_script("arguments[0].click();", csv_clickable_label)

        self.driver.switch_to.default_content()
        self.driver.switch_to.frame('iframe_menu_administrador')
        self.driver.switch_to.frame('TB_iframeContent')

        csv_create_bttn = self.driver.find_element(By.ID, 'bok')
        self.driver.execute_script("arguments[0].click();", csv_create_bttn)

        self.driver.switch_to.default_content()
        self.driver.switch_to.frame('iframe_menu_administrador')
        sleep(2)

        csv_download_bttn = self.driver.find_element(By.ID, 'idBtnDown')
        self.driver.execute_script("arguments[0].click();", csv_download_bttn)
        csv_download_bttn.click()