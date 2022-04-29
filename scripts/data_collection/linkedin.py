import selenium

BASE_URL = "https://www.linkedin.com/jobs/search"
LOCATION = "United States of America"
TRK = "public_jobs_jobs-search-bar_search-submit"

CLASS_RESULT_LIST = "jobs-search__results-list"
CLASS_LOAD_RESULTS = "infinite-scroller__show-more-button infinite-scroller__show-more-button--visible"
CLASS_VIEWED_ALL = "px-1.5 flex inline-notification hidden text-color-signal-positive see-more-jobs__viewed-all"

JOB_TITLES = [
    "Computer Programmer",
    "Data Architect",
    "Data Engineer",
    "Machine Learning Engineer",
    "Software Developer",
    "Software Engineer"
]

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

def simulate_infinite_scroll(driver):
    pass

def retrieve_job_posting_url(driver):
    pass

def main():
    start_urls = [create_query_string(job_title) for job_title in JOB_TITLES]

    driver = selenium.webdriver.Chrome()
    driver.maximize_window()

    for url in start_urls:
        driver.get(url)
        simulate_infinite_scroll(driver)

if __name__ == "__main__":
    main()
