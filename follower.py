from credentials import credential_dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, UnexpectedAlertPresentException, NoAlertPresentException

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
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

    driver.get('https://www.instagram.com/')
    username_field = driver.find_element(By.NAME, value='username').send_keys(credential_dict.get('username'))
    password_field = driver.find_element(By.NAME, value='password').send_keys(credential_dict.get('password'), Keys.ENTER)
    driver.implicitly_wait(10)
    sleep(5)
    return driver

def find_page(driver):
    page_name = 'nasabrasil'

    url = f'https://www.instagram.com/{page_name}'
    driver.get(url)
    driver.implicitly_wait(10)
    #check to see if inputted page is real
    try:
        driver.find_element(By.XPATH, value='//span[text()="Sorry, this page isn\'t available."]')
    except NoSuchElementException:
        return True
    else:
        return False

def follow_all(driver):
    followers_button = driver.find_element(By.XPATH, value="//a[contains(@href, 'followers')]").click()
    followers = driver.find_elements(By.XPATH, value="//div[contains(@class, 'x1dm5mii')]")
    for follower in followers:
        button = follower.find_element(By.TAG_NAME, value='button').click()
    print('done')


if  __name__ == "__main__":
    browser = main()
    valid_page = find_page(browser)
    if  valid_page:
        follow_all(browser)
    else:
        print('enter valid page')
        find_page(browser)
