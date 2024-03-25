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
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"

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
    publisher_tag = ".nJlQNd.sMzDkb"
    result_title = '[class*="Fol1qc"]'
    publisher = "[class*=vNEEBe]"
    details = "div.I2Cbhb"
    apply_link_cards = "span > a.pMhGee.Co68jc.j0vryd"


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
    context = browser.new_context(
        user_agent=user_agent, viewport={"width": 1920, "height": 1080}
    )
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

    output_data = {"search_page_url": search_page_url, "jobs": scraped_jobs}
    with open(OUTPUT_FILE_DIR, "w") as outfile:
        json.dump(output_data, outfile, indent=4)


def unpack_details(details_elements):
    # Initialize default values
    time_posted = "Not specified"
    salary = "Not specified"
    job_type = "Not specified"
    benefits = []

    for detail in details_elements:
        # Using the direct text content since aria-hidden does not contain the descriptive text
        text_content = detail.text_content().strip()

        # Identifying the type of detail based on known keywords
        if "ago" in text_content or "Posted" in text_content:
            time_posted = text_content
        elif any(keyword in text_content for keyword in ["K a year", "an hour"]):
            salary = text_content
        elif any(
            keyword in text_content
            for keyword in ["Full-time", "Part-time", "Contractor"]
        ):
            job_type = text_content
        else:
            benefits.append(text_content)  # Assume other texts might relate to benefits

    return time_posted, salary, job_type, benefits


def scrape_job(timekeeper, desc_card):
    scrape_time = timekeeper.now
    job_title_element = desc_card.query_selector("h2.KLsYvd")
    job_title = (
        job_title_element.text_content().strip()
        if job_title_element
        else "Title not found"
    )
    publisher = (
        desc_card.query_selector(css_selector.publisher_tag).text_content().strip()
    )
    job_desc = (
        desc_card.query_selector(css_selector.job_desc_tag).text_content().strip()
    )
    details_elements = desc_card.query_selector_all(css_selector.details)

    application_links = []
    apply_link_elements = desc_card.query_selector_all(css_selector.apply_link_cards)
    for link_element in apply_link_elements:
        href = link_element.get_attribute("href")
        platform_name = (
            link_element.text_content().split("Apply on ")[-1].strip()
            if "Apply on " in link_element.text_content()
            else "Unknown Platform"
        )
        application_links.append({"url": href, "platform": platform_name})

    time_posted, salary, job_type, benefits = unpack_details(details_elements)

    job_data = {
        "scrape_time": scrape_time,
        "job_title": job_title,
        "publisher": publisher,
        "time_posted": time_posted,
        "salary": salary.replace("\u2013", "-"),
        "benefits": benefits,  # Include benefits in job_data
        "job_type": job_type,
        "desc": job_desc,
        "application_links": application_links,
    }

    return job_data


def format_city_state(city_state):
    if city_state:
        city, state = city_state.split(",")
        city = city.strip().replace(" ", "+")
        state = state.strip().replace(" ", "+")
        return f"&htichips=city;{city}_comma_%20{state}"
    return ""


parser = argparse.ArgumentParser()
parser.add_argument(
    "--search_term", type=str, help="job term to search for", required=True
)
parser.add_argument(
    "--limit", type=int, help="maximum number of jobs to scrape", default=50
)
parser.add_argument(
    "--is_today",
    action="store_true",
    help="Set this flag to only scrape jobs posted today",
)
parser.add_argument(
    "--city_state",
    type=str,
    help="City and state for job search, formatted as 'City,State' (e.g., 'New York,NY')",
)


args = parser.parse_args()
CAP = args.limit

context = create_browser_context()
page = context.new_page()
search_term = args.search_term
search_page_url = GJOBS_URL.format(search_term)
if args.is_today:
    search_page_url += GJOBS_URL_TODAY_SUBSTRING
if args.city_state:
    city_state_substring = format_city_state(args.city_state)
    search_page_url += city_state_substring
page.goto(search_page_url)
get_jobs(page)
context.close()
