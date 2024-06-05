from credentials import credential_dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())

chrome_options = Options()
options = [
    "--headless",
    "--disable-gpu",
    "--window-size=1920,1200",
    "--ignore-certificate-errors",
    "--disable-extensions",
    "--no-sandbox",
    "--disable-dev-shm-usage"
]
for option in options:
    chrome_options.add_argument(option)

def main():
    print("Iniciando o navegador")
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    driver.get('https://www.instagram.com/')
    print("Página do Instagram carregada")
    
    try:
        print("Procurando campo de nome de usuário")
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'username'))
        )
        username_field.send_keys(credential_dict.get('username'))
        print("Nome de usuário inserido")
        
        print("Procurando campo de senha")
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'password'))
        )
        password_field.send_keys(credential_dict.get('password'), Keys.ENTER)
        print("Senha inserida")
        
    except TimeoutException:
        print("Não foi possível encontrar os elementos de entrada.")
        driver.quit()
    
    driver.implicitly_wait(10)
    sleep(5)
    return driver

def find_page(driver):
    page_name = 'nasabrasil'
    url = f'https://www.instagram.com/{page_name}'
    driver.get(url)
    driver.implicitly_wait(10)
    
    print(f"Verificando se a página {page_name} está disponível")
    # Verificar se a página não está disponível
    try:
        driver.find_element(By.XPATH, '//span[text()="Sorry, this page isn\'t available."]')
    except NoSuchElementException:
        print(f"Página {page_name} está disponível")
        return True
    else:
        print(f"Página {page_name} não está disponível")
        return False

def follow_all(driver):
    try:
        print("Procurando botão de seguidores")
        followers_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/followers/')]"))
        )
        print("Botão de seguidores encontrado")
        followers_button.click()
        
        # Capturar a captura de tela após clicar no botão de seguidores
        driver.save_screenshot('screenshot_after_click_followers.png')
        print("Captura de tela salva: screenshot_after_click_followers.png")
        
        print("Procurando elementos de seguidores")
        followers_list = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']//ul"))
        )
        
        followers = []
        end_time = time.time() + 30  # espera de 30 segundos no total
        while time.time() < end_time:
            followers = driver.find_elements(By.XPATH, "//div[@role='dialog']//ul//div[contains(@class, '_ap3a _aaco _aacw _aad6 _aade')]")
            if followers:
                break
            sleep(1)
        
        if not followers:
            raise TimeoutException("Não foi possível encontrar elementos de seguidores")

        print("Elementos de seguidores encontrados")
        
        for follower in followers:
            try:
                follow_button = follower.find_element(By.XPATH, ".//div[contains(text(), 'Seguir')]")
                follow_button.click()
            except NoSuchElementException:
                print("Botão de seguir não encontrado para um dos seguidores")
        
        print('done')

    except TimeoutException:
        print("Não foi possível encontrar o botão de seguidores ou os seguidores.")
        driver.save_screenshot('screenshot_error.png')
        print("Captura de tela salva: screenshot_error.png")
        driver.quit()

if __name__ == "__main__":
    browser = main()
    valid_page = find_page(browser)
    if valid_page:
        follow_all(browser)
    else:
        print('enter valid page')
        find_page(browser)
