import json
import datetime
import logging
import time
import random
import argparse
from playwright.sync_api import sync_playwright

GJOBS_URL = "https://www.google.com/search?q={}&ibp=htl;jobs"
GJOBS_URL_TODAY_SUBSTRING = (
    "#htivrt=jobs&htichips=date_posted:today&htischips=date_posted;today"
)
OUTPUT_FILE_DIR = "job_scrape_master.json"
THRESHOLD = 10
CAP = 50


class TimeKeeper:
    @property
    def now(self):
        """
        return the current correct date and time using the format specified
        """
        return f"{datetime.datetime.now():%d-%b-%Y T%I:%M}"


class css_selector:
    jobs_cards = "li"
    job_desc_card_visible = '[id="tl_ditc"]'
    job_full_desc_button = '[class="atHusc"]'
    job_desc_tag = "[class*=HBvzbc]"
    title_tag = "[class*=sH3zFd]"
    publisher_tag = "[class*=tJ9zfc]"
    result_title = '[class*="Fol1qc"]'
    publisher = "[class*=vNEEBe]"
    details = "[class*=I2Cbhb]"
    apply_link_cards = "[class*=DaDV9e]"


def scroll_element_into_view_and_click(element):
    # Ensure the element is visible in the viewport
    element.scroll_into_view_if_needed()
    # Click the element
    element.click()


def show_full_job_description(job_desc_card):
    try:
        full_desc_button = job_desc_card.query_selector(
            css_selector.job_full_desc_button
        )
        if full_desc_button:
            full_desc_button.click()
    except Exception:
        return


def create_browser_context():
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    context.set_default_timeout(10000)
    return context


def nap(secs=random.randint(0, 5)):
    """
    sleeps the bot for specified number of seconds
    """
    logging.info(f"Napping for {secs} seconds")
    print("nap for {} seconds".format(secs))
    time.sleep(secs)


def get_jobs(page):
    timekeeper = TimeKeeper()
    job_cards = page.query_selector_all(css_selector.jobs_cards)
    scraped_jobs = []

    if job_cards:
        count = 1
        while True:
            try:
                card = job_cards[count - 1]
                scroll_element_into_view_and_click(card)
            except IndexError:
                break

            job_desc_card = page.query_selector(css_selector.job_desc_card_visible)
            show_full_job_description(job_desc_card)
            job_data = scrape_job(timekeeper, job_desc_card)
            if job_data:
                scraped_jobs.append(job_data)

            if (count % THRESHOLD) == 0:
                nap(random.randint(1, 6))
                job_cards = page.query_selector_all(css_selector.jobs_cards)

            if count == len(job_cards):
                logging.info("\aNew data isn't coming in.")
                break

            if count == CAP:
                break

            count += 1

    with open(OUTPUT_FILE_DIR, "w") as outfile:
        json.dump(scraped_jobs, outfile, indent=4)


def unpack_details(details):
    # Initialize default values for time_posted, salary, and job_type
    time_posted = ""
    salary = ""
    job_type = ""

    if len(details) == 0:
        return time_posted, salary, job_type
    if len(details) == 1:
        time_posted = details[0].text_content()
    elif len(details) == 2:
        time_posted = details[0].text_content()
        salary = details[1].text_content()
    elif len(details) >= 3:
        time_posted = details[0].text_content()
        if details[1].text_content().endswith("mins"):
            job_type = details[2].text_content()
        else:
            salary = details[1].text_content()
            job_type = details[2].text_content()

    return time_posted, salary, job_type


def scrape_job(timekeeper, desc_card):
    scrape_time = timekeeper.now
    job_title = (
        desc_card.query_selector(css_selector.title_tag).text_content().split("\n")[0]
    )
    pbctry = desc_card.query_selector(css_selector.publisher_tag).text_content()
    publisher = pbctry.split("\n")[0]
    job_desc = desc_card.query_selector(css_selector.job_desc_tag).text_content()
    details_elements = desc_card.query_selector_all(css_selector.details)
    time_posted, salary, job_type = unpack_details(details_elements)

    apply_links_element = desc_card.query_selector(css_selector.apply_link_cards)
    if apply_links_element:
        application_link = [
            x.get_attribute("href")
            for x in apply_links_element.query_selector_all("a")
            if x.text_content().startswith("Apply on")
        ]
    else:
        application_link = []

    job_data = {
        "scrape_time": scrape_time,
        "job_title": job_title,
        "publisher": publisher,
        "time_posted": time_posted,
        "salary": salary,
        "job_type": job_type,
        "desc": job_desc,
        "application_link": application_link,
    }

    return job_data


parser = argparse.ArgumentParser()
parser.add_argument("--search_term", type=str, help="job term to search for")
parser.add_argument(
    "--limit", type=int, help="maximum number of jobs to scrape", default=200
)
parser.add_argument("--is_today", type=str, help="only scrape jobs posted today")
args = parser.parse_args()
CAP = args.limit

context = create_browser_context()
page = context.new_page()
search_term = "data engineer"
search_page_url = GJOBS_URL.format(args.search_term)
if args.is_today == "True":
    search_page_url += GJOBS_URL_TODAY_SUBSTRING
page.goto(search_page_url)
get_jobs(page)
context.close()
