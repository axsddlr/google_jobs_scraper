# Google Jobs Scraper

This Python script automates the process of scraping job postings from Google Jobs based on specified search terms. It leverages the Playwright library to interact with web pages, parse job details, and extract application links.

## Features

- Scrapes job postings from Google Jobs.
- Extracts detailed information about each job posting, including title, publisher, description, and application links.
- Filters jobs posted today (optional).
- Customizable search term and job scraping limit.

## Prerequisites

- Python 3.6+
- pip (Python package manager)

## Installation

### 1. Clone the Repository

Start by cloning the repository to your local machine:

```bash
git clone https://github.com/axsddlr/google_jobs_scraper.git
cd google_jobs_scraper
```

Replace `https://github.com/axsddlr/google_jobs_scraper.git` with the actual URL of your repository and `google_jobs_scraper` with the name of the folder where you cloned the repository.

### 2. Create a Virtual Environment (Optional but Recommended)

It's a good practice to create a virtual environment for Python projects to manage dependencies effectively. Use the following commands to create and activate a virtual environment:

- For macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

- For Windows:

```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies

Install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

This command will install all the necessary Python packages listed in `requirements.txt`, including Playwright.

### 4. Install Playwright Browsers

After installing the Playwright package, run the following command to install the required browsers:

```bash
playwright install
```

## Usage

To run the script, use the following command:

```bash
python google_jobs.py --search_term="Your Search Term" --limit=Number of Jobs to Scrape --is_today=Boolean to Filter Jobs Posted Today
```

Replace:

- `Your Search Term` with the job title or keywords you're interested in (e.g., "software engineer").
- `Number of Jobs to Scrape` with the maximum number of jobs you want to scrape (e.g., `50`).
- `Boolean to Filter Jobs Posted Today` with `True` if you only want to scrape jobs posted today, otherwise `False`.

### Example

```bash
python google_jobs.py --search_term="data scientist" --limit=100 --is_today=False
```

This command scrapes up to 100 data scientist job postings from Google Jobs, including those posted before today.

## Output

The script saves the scraped job postings in a JSON file named `job_scrape_master.json` in the project directory.
