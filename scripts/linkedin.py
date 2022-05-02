from multiprocessing import Process
import os
from random import randint, random
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import sqlite3
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "https://www.linkedin.com/jobs/search"
LOCATION = "United States of America"
TRK = "public_jobs_jobs-search-bar_search-submit"

SELECTOR_GLOBAL_ALERT = "#artdeco-global-alert-container"
SELECTOR_LOGIN_MODAL = "body > div.cta-modal.show"
SELECTOR_LAST_RESULT = "#main-content > section.two-pane-serp-page__results-list > ul > li:last-child"
SELECTOR_LAST_RESULT_LINK = "#main-content > section.two-pane-serp-page__results-list > ul > li:last-child > div > a"
SELECTOR_ALL_RESULTS = "#main-content > section.two-pane-serp-page__results-list > ul > li"
SELECTOR_ALL_RESULT_ANCHOR_TAGS = "#main-content > section.two-pane-serp-page__results-list > ul > li > div > a"
SELECTOR_LOAD_MORE = "#main-content > section.two-pane-serp-page__results-list > button"
SELECTOR_VIEWED_ALL = "#main-content > section.two-pane-serp-page__results-list > div.px-1\.5.flex.inline-notification.hidden.text-color-signal-positive.see-more-jobs__viewed-all > p"

JOB_TITLES = [
    "Applications Developer",
    "Computer Engineer",
    "Computer Programmer",
    "Data Architect",
    "Data Engineer",
    "Data Scientist",
    "Database Developer",
    "IT Support Specialist",
    "Junior Software Developer",
    "Machine Learning Engineer",
    "Mobile Applications Developer",
    "Programmer Analyst",
    "Software Developer",
    "Software Engineer",
    "Software Test Engineer",
    "Technology",
    "Web Developer"
]

DB_CONNECTION = "./data/linkedin.sqlite"

def setup_chrome_driver() -> webdriver:
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_experimental_option('prefs', {'intl.accept_languages': 'en, en_US'})
    return webdriver.Chrome(service=service, chrome_options=options)

def setup_sqlite_database(path: str) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    return connection

def transform_string_to_table_name(string: str) -> str:
    return string.lower().replace(" ", "_")
    
def setup_sqlite_table(connection: sqlite3.Connection, table_name: str):
    cursor = connection.cursor()
    query =f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'";
    result = cursor.execute(query)
    if result.rowcount >= 1:
        return
    query = f"""CREATE TABLE IF NOT EXISTS {table_name} (
                platform VARCHAR(255) NOT NULL,
                job_category VARCHAR(255) NOT NULL,
                base_url VARCHAR(255) NOT NULL,
                start_url VARCHAR(255) NOT NULL,
                job_title VARCHAR(255) NOT NULL,
                job_posting_html TEXT NOT NULL
            ); """
    cursor.execute(query)
    cursor.close()

def safe_transform_string(string: str) -> str:
    return string.replace(" ", "%20")

def create_query_string(job_title: str) -> str:
    keywords = safe_transform_string(job_title)
    location = safe_transform_string(LOCATION)
    query_string = f"{BASE_URL}?keywords={keywords}" \
        f"&location={location}" \
        f"&trk={TRK}" \
        f"&position=1" \
        f"&pageNum=0"
    return query_string

def remove_element_by_css_selector(driver: webdriver, value: str):
    element = WebDriverWait(driver, 10).until(
        lambda driver: driver.find_element(by=By.CSS_SELECTOR, value=value)
    )
    driver.execute_script("arguments[0].remove();", element)

def random_timeout(start: int=3, stop: int=10) -> float:
    return randint(start, stop) + random()

def main():
    connection = setup_sqlite_database(DB_CONNECTION)
    driver = setup_chrome_driver()
    driver.maximize_window()
    driver.implicitly_wait(5)

    start_urls = [create_query_string(title) for title in JOB_TITLES]

    for index, start_url in enumerate(start_urls):
        table_name = transform_string_to_table_name(JOB_TITLES[index])
        setup_sqlite_table(connection=connection, table_name=table_name)

        driver.get(start_url)
        remove_element_by_css_selector(driver, SELECTOR_GLOBAL_ALERT)
        remove_element_by_css_selector(driver, SELECTOR_LOGIN_MODAL)

        viewed_all = WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element(by=By.CSS_SELECTOR, value=SELECTOR_VIEWED_ALL)
        )

        actions = ActionChains(driver)
        [results_loaded, more_results] = [0, True]

        while more_results:
            number_results = WebDriverWait(driver, 10).until(
                lambda driver: driver.execute_script(
                    f"return document.querySelectorAll('{SELECTOR_ALL_RESULTS}').length;"
                )
            )

            anchor_tags = WebDriverWait(driver, 10).until(
                lambda driver: driver.find_elements(by=By.CSS_SELECTOR, value=SELECTOR_ALL_RESULT_ANCHOR_TAGS)
            )
            result_urls = [tag.get_attribute("baseURI") for tag in anchor_tags][results_loaded:]
            current_number_results = len(result_urls)
            print(f"Loaded {current_number_results} job postings. {number_results} in total.")

            cursor = connection.cursor()
            for result_index, result_url in enumerate(result_urls):
                response = requests.get(result_url)
                html = response.text
                
                sqlite_insert_query = f"""INSERT INTO {table_name}
                            (platform, job_category, base_url, start_url, job_title, job_posting_html)
                            VALUES
                            (?, ?, ?, ?, ?, ?);"""
                count = cursor.execute(sqlite_insert_query, ["LinkedIn", JOB_TITLES[index], BASE_URL, start_url, result_url, html])
                print(f"Record inserted successfully into {table_name} table {cursor.rowcount + result_index} of {current_number_results}")
                connection.commit()

                # sleep(random_timeout(1,5))
            cursor.close()
            print(f"Successfully loaded and stored {current_number_results} job postings. {number_results} in total.")
            results_loaded = number_results
            
            for round in range(40):
                if viewed_all.is_displayed():
                    continue
                last_result = WebDriverWait(driver, 10).until(
                    lambda driver: driver.find_element(by=By.CSS_SELECTOR, value=SELECTOR_LAST_RESULT)
                )
                actions.move_to_element(last_result).perform()
                load_more = WebDriverWait(driver, 10).until(
                    lambda driver: driver.find_element(by=By.CSS_SELECTOR, value=SELECTOR_LOAD_MORE)
                )
                if load_more.is_displayed():
                    load_more.click()
            more_results = not viewed_all.is_displayed()

    connection.close()
    driver.quit()

if __name__ == "__main__":
    main()
