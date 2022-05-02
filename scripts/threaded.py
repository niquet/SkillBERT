import sys
from time import sleep
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
        start_url = f"{url}?keywords={keyword}&"
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
        lambda driver: driver.find_element(by=By.CSS_SELECTOR, value=SELECTORS["status"]["viewed_all"])
    )
    actions = ActionChains(driver)
    more_results = True
    while more_results:
        last_result = WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element(by=By.CSS_SELECTOR, value=SELECTORS["job_results"]["list_items"]["last"])
        )
        actions.move_to_element(last_result).perform()
        sleep(3)
        load_more = WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element(by=By.CSS_SELECTOR, value=SELECTORS["buttons"]["load_more"])
        )
        if load_more.is_displayed():
            load_more.click()
        more_results = not viewed_all.is_displayed()

def retrieve_html_data(driver: webdriver):
    viewed_all = WebDriverWait(driver, 10).until(
        lambda driver: driver.find_element(by=By.CSS_SELECTOR, value=SELECTORS["status"]["viewed_all"])
    )
    more_results = True
    all_results = SELECTORS["job_results"]["list_items"]["all"]
    while more_results:
        current_search_result_count = WebDriverWait(driver, 10).until(
            lambda driver: driver.execute_script(
                f"return document.querySelectorAll('{all_results}').length;"
            )
        )
        print(f"Currently {current_search_result_count} results displayed.")
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

        remove_element(driver, by=By.CSS_SELECTOR, value=SELECTORS["popups"]["global_alert"])
        remove_element(driver, by=By.CSS_SELECTOR, value=SELECTORS["popups"]["login_modal"])
        
        search_result_count_string = WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element(by=By.CSS_SELECTOR, value=SELECTORS["status"]["result_count"]).get_attribute("innerText")
        )
        
        search_result_count = int(
            search_result_count_string.strip()[10:].replace(",", "")[:-1]
        )
        print(f"Found {search_result_count} results.")
        # simulate_infinite_scroll(driver)
        
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
