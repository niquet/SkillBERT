import sys
sys.path.append("./")
import threading

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import quote
from webdriver_manager.chrome import ChromeDriverManager

from utils.config import ConfigParser
config_parser = ConfigParser()
CONFIG = config_parser.read_json("linkedin.config.json")
BASE_URL = CONFIG["base_url"]
SELECTORS = CONFIG["selectors"]

def setup_driver() -> webdriver:
    service = Service(
        ChromeDriverManager().install()
    )
    options = webdriver.ChromeOptions()
    options.add_experimental_option(
        'prefs', 
        {
            'intl.accept_languages': 'en, en_US'
        }
        )
    return webdriver.Chrome(
        service=service,
        chrome_options=options
    )

def safe_transform_url(url: str) -> str:
        return quote(url, safe="/:?=&")

def get_url(url: str, parameters: dict) -> str:
    url = f"{url}?"
    for parameter in parameters.keys():
        url += f"{parameter}={parameters[parameter]}&"
    return safe_transform_url(url[:-1])

def get_start_urls(url: str, parameters: dict) -> list:
    start_urls = []
    keywords = parameters["keywords"]
    for keyword in keywords:
        start_url = f"{url}?keywords={keyword}"
        for parameter in parameters.keys():
            if parameter == "keywords":
                continue
            start_url += f"{parameter}={parameters[parameter]}&"
        start_urls.append(safe_transform_url(start_url[:-1]))
    return start_urls

def remove_element(driver, by: By, value: str) -> None:
    element = driver.find_element(by=by, value=value)
    driver.execute_script("arguments[0].remove();", element)

def simulate_infinite_scroll(driver: webdriver):
    viewed_all = WebDriverWait(driver, 10).until(
        lambda driver: driver.find_element(by=By.CSS_SELECTOR, value=SELECTOR_VIEWED_ALL)
    )
    actions = ActionChains(driver)
    more_results = True
    while more_results:
        last_result = WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element(by=By.CSS_SELECTOR, value=SELECTOR_LAST_RESULT)
        )
        actions.move_to_element(last_result).perform()
        load_more = WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element(by=By.CSS_SELECTOR, value=SELECTOR_LOAD_MORE)
        )
        if load_more.is_displayed():
            load_more.click()
            print(f"Loaded more results")
        more_results = not viewed_all.is_displayed()

def retrieve_html_data(driver: webdriver):
    viewed_all = WebDriverWait(driver, 10).until(
        lambda driver: driver.find_element(by=By.CSS_SELECTOR, value=SELECTOR_VIEWED_ALL)
    )
    more_results = True
    while more_results:
        number_results = WebDriverWait(driver, 10).until(
            lambda driver: driver.execute_script(
                f"return document.querySelectorAll('{SELECTOR_ALL_RESULTS}').length;"
            )
        )
        print(f"Currently {number_results} results in total.")
        more_results = not viewed_all.is_displayed()

def main():

    driver = setup_driver()
    driver.maximize_window()
    driver.implicitly_wait(5)

    start_urls = get_start_urls(
        url=BASE_URL["url"],
        parameters=BASE_URL["parameters"]
    )

    for start_url in start_urls:

        driver.get(start_url)
        remove_element_by_css_selector(driver, SELECTOR_GLOBAL_ALERT)
        remove_element_by_css_selector(driver, SELECTOR_LOGIN_MODAL)

        total_result_count_text = WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element(by=By.CSS_SELECTOR, value=SELECTOR_RESULT_COUNT).get_attribute("innerText")
        )
        total_result_count = int(total_result_count_text.strip()[:-8].replace(",", ""))
        
        thread_one = threading.Thread(
            target=simulate_infinite_scroll,
            args=[driver]
        )
        thread_two = threading.Thread(
            target=retrieve_html_data,
            args=[driver]
        )
        
        thread_one.start()
        thread_two.start()
        thread_one.join()
        thread_two.join()

    driver.quit()

if __name__ == "__main__":
    main()
