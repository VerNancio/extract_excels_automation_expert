import datetime as dt
import time
from threading import Thread
from bs4 import BeautifulSoup # pyright: ignore[reportMissingImports]
import pandas as pd
from pandas import DataFrame
from io import StringIO
from time import sleep
from typing import Literal

import traceback

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from ...helpers.tools.date_formatter import DateFormatter
from ...helpers.tools.get_credentials import get_credentials

class MerckSeleniumScrapying:
    
    driver: WebDriver
    user: str
    pw: str
    credentials: dict
    report_type: Literal['hour', 'date']

    def __init__(self, report_type: Literal['hour', 'date']):
        
        options = Options()
        
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # service = Service('/usr/bin/chromedriver') # para rodar no container sem BO
        service = Service() # para rodar no container sem BO
        
        # Inicia o acesso ao navegador
        # self.driver = webdriver.Chrome(options=options)
        self.driver = webdriver.Chrome(options=options, service=service)
        self.credentials = get_credentials('merck')
        if report_type in ('hour', 'date'):
            self.report_type = report_type
        else:
            raise ValueError('Necessário passar "report_type" como "date" ou "hour"')
        
    def run(self, start_date: None = None, end_date: str = None) -> DataFrame | None:
        try:
            self.do_login()
            df: DataFrame = self.get_all_reports_in_df(start_date, end_date)
            df = self.pre_treat_df(df)
            
            return df
        
        except Exception as e:
            print(f"Ocorreu um erro: {e}, {e}")
            # while 1:...
            # raise e
        finally:
            self.driver.quit()
            print("Navegador fechado.")
            traceback.print_exc()


    def do_login(self) -> None:
        url: str = 'https://www.rhmed.com.br/evidamed/'
        self.driver.get(url)
        self.driver.maximize_window()
        script = """
        document.querySelector('input[name="login"]').value = arguments[0];
        document.querySelector('input[name="password"]').value = arguments[1];
        document.querySelector('button[type="submit"]').click();
        """
        self.driver.find_element(By.XPATH, "//input[@id='usuario']").send_keys("l.fsilva")
        self.driver.find_element(By.XPATH, "//input[@id='senha']").send_keys("LaraBeatriz010203.")
        self.driver.find_element(By.XPATH, "//button[normalize-space()='Entrar']").click()
        ##self.driver.execute_script(script, self.credentials['username'], self.credentials['pw'])
        time.sleep(0.5)


    def get_all_reports_in_df(self, start_date: str = None, end_date: str = None) -> DataFrame:
        
        # Redireciona pra página de menu de relatórios
        # self.driver.get('https://www.rhmed.com.br/evidamed/web/relatorio/Licenca%20Medica/LMPorData/frmLMPorData.asp')
        
        date_formatter = DateFormatter()
        
        start_date = start_date if start_date else date_formatter.last_month_first_day()
        start_date_iso = date_formatter.format_date(start_date, new_format='iso')

        end_date = end_date if end_date else date_formatter.last_month_last_day()
        end_date_iso = date_formatter.format_date(end_date, new_format='iso')
        
        # while 1:...
        
        
        # Sleep temporário que evita que a aplicação quebra ao fazer login (exp: rhmed ta gerando uma outra tela que está causando esse bo)
        # Redireciona pra página com todos os registros em html
        if self.report_type == 'date':
            url = f'https://www.rhmed.com.br/evidamed/web/relatorio/LicencaMedica/LMPorData/index.asp?datInicial={start_date_iso}&datTermino={end_date_iso}&formato=html&action=consultar'
            
        elif self.report_type == 'hour':
            url = f'https://www.rhmed.com.br/evidamed/web/Relatorio/LicencaMedica/LMporHora/index.asp?datInicial={start_date_iso}&datTermino={end_date_iso}&tipoPesquisaFuncionario=1&funcionario=&formato=html&action=consultar'
        
        self.driver.get(url)
        
        html = self.driver.page_source
        soup = BeautifulSoup(html, "lxml")
        
        # Verifica se há tabelas
        tables = soup.find_all("table")
        
        if not tables:
            print("Nenhuma tabela encontrada na página.")
            df = None
        else:
            tables_str = str(tables)
            df_list = pd.read_html(StringIO(tables_str))
            df = df_list[0][:-1]  # pega a primeira tabela e até a penúltima linha
        return df
    
    
    def pre_treat_df(self, df: DataFrame) -> DataFrame:
        """
        Pré tratamento que separa a coluna "CID" em "cids" e "cids_descricao",
        serve somente caso esteja se buscando atestados por datas, já que os de horas não possuem cids
        """
        # A primeiro string vazia ('') toma como pressuposto que cids sempre vão ter "-", ou, caso
        # não tenham, será passado como "Não informado" ou talvez nulo  
        

        if self.report_type == 'date':
            # df[['cids', 'cids_descricao']] = df['CID'].apply(
                # lambda x: pd.Series(x.split('-', 1)) if '-' in x else pd.Series(['', ''])
            # )
            # df['CPF'] = df['Nome.1']
            ...
            
        if self.report_type == 'hour':
            df['Data Início'] = df['Data']
            df['Data Término'] = df['Data']
            df.rename(columns={'Matricula': 'Matrícula'}, inplace=True)
            df['cids'] = ''
            df['cids_descricao'] = ''
        df.loc[df['Conselho'] == '-', 'Conselho'] = ''
        
        return df
 