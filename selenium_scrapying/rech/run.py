from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC

from time import sleep
import datetime




def app() -> list[list[dict]]:

    # 1. Inicia o navegador (o Selenium vai baixar o driver se necessário)
    driver = webdriver.Chrome() 
    all_windows = driver.window_handles

    try:

        do_login(driver=driver)
        go_to_menu(driver=driver)
        # add_filter(driver=driver)
        # get_pending(driver=driver)



        return get_func_data(driver=driver)
        

        while True:
            pass


    except Exception as e:
        print(f"Ocorreu um erro: {e}")

    finally:
        # 7. Fecha o navegador
        driver.quit()
        print("Navegador fechado.")


def do_login(driver: WebDriver):
    
    # 2. Navega para uma página
    driver.get("https://platform.senior.com.br/login/?redirectTo=https%3A%2F%2Fplatform.senior.com.br%2Fsenior-x%2F&tenant=nossa-gente.com.br")

    username_input = driver.find_element(By.ID, 'username-input-field')
    username_input.send_keys('Expert_Atestado')

    next_bttn = driver.find_element(By.ID, 'nextBtn')
    next_bttn.click()

    sleep(2)

    pw_input = driver.find_element(By.ID, 'password-input-field')
    pw_input.send_keys('123456@Senior')

    login_bttn = driver.find_element(By.ID, 'loginbtn')
    login_bttn.click()

    sleep(2)



def go_to_menu(driver: WebDriver):

    menu_favs_clickable = driver.find_element(By.ID, 'menu-item-Favoritos')
    menu_favs_clickable.click()

    sleep(2)

    menu_favs_clickable_2 = driver.find_element(By.ID, 'apps-menu-item-0')
    menu_favs_clickable_2.click()

    sleep(1)

    menu_favs_clickable_3 = driver.find_element(By.ID, 'apps-menu-item-0')
    menu_favs_clickable_3.click()


def add_filter(driver: WebDriver):

    # wait = WebDriverWait(driver, 15)

    # sleep(5)
    # wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "custom_iframe")))

    # filter_bttn = wait.until(EC.element_to_be_clickable((By.ID, "filterButton")))
    # filter_bttn.click()

    # hoje = datetime.date.today()
    # data_formatada = hoje.strftime("%d/%m/%Y")
    
    # print(f"Data de hoje: {data_formatada}")

    # period_initial_input = wait.until(EC.visibility_of_element_located((By.ID, 'periodInitial')))

    # script_js = f"arguments[0].value = '{data_formatada}';"
    # driver.execute_script(script_js, period_initial_input)


    # send_filters_bttn = driver.find_element(By.ID, 's-button-3')
    # wait.until(EC.element_to_be_clickable((By.ID, "filterButton")))
    # driver.execute_script('alert("aaa")')

    
    # Opcional: Volte para a página principal se precisar interagir com outros elementos
    driver.switch_to.default_content()


def get_func_data(driver: WebDriver) -> list[list[dict]]:

    wait = WebDriverWait(driver, 15)

    sleep(5)
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "custom_iframe")))


    for i in range(400):

        data_box_items: list[WebElement] = driver.find_element(By.ID, 'ui-accordiontab-0-content') \
                                                                .find_element(By.TAG_NAME, 'div') \
                                                                .find_elements(By.XPATH, "./*")
        # print(f'{i} -- {len(data_box_items)}')
        sleep(0.25)

        class_str = data_box_items[-2].get_attribute('class')
        class_list = class_str.split()

        if 'see-more' in class_list:
            # print(class_list)
            data_box_items[-2].click()

        elif last_items_in_box_qnt == len(data_box_items):
            break

        last_items_in_box_qnt = len(data_box_items)
        

    clients_items = data_box_items[:-1]

    people_list: list[list[dict]] = []

    for item in clients_items[:10]:

        clickable = item.find_element(By.ID, 'clickable panel')

        part_with_all_infos: list[WebElement] = clickable.find_elements(By.XPATH, "./*")

        div_with_all_infos: WebElement = part_with_all_infos[1].find_element(By.TAG_NAME, "div") \
                                                               .find_elements(By.XPATH, "./*")[0]

        title_content = div_with_all_infos.get_attribute('title')
        title_splited = title_content.split(', ')
        items_splited = [item.split(':') for item in title_splited]
        items_dicted = {key: item for key, item in items_splited}
        print(items_dicted)

        people_list.append(items_dicted)

    print(people_list)
    return people_list

        
def get_pending(driver: WebDriver):

    # css_selector_classes = ".ui-sm-12.ui-md-3.ui-lg-2.sidebar"

    # driver.switch_to.default_content()
    with open('./all.html', 'w') as f:
        f.write(driver.page_source)

    tried = driver.find_element(By.TAG_NAME, 'quick-filters')
    print(tried)