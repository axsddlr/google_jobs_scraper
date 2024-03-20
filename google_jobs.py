from playwright.async_api import async_playwright
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime


async def get_page_source(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        # Creating a new browser context with specified user agent and viewport
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            viewport={"width": 1280, "height": 720},
            java_script_enabled=True,
        )
        page = await context.new_page()
        await page.goto(url, wait_until="networkidle")
        html_content = await page.content()  # Get HTML content of the page
        await browser.close()
        return html_content


def parse_html_with_bs(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    job_list = []
    for div in soup.find_all(
        name="li", attrs={"class": "iFjolb gws-plugins-horizon-jobs__li-ed"}
    ):
        job_url = div.find("span", attrs={"class": "DaDV9e"})
        try:
            job_url = job_url.find("a").get("href")
        except:
            pass
        title = div.find("div", attrs={"class": "BjJfJf PUpOsf"}).text
        company_name = div.find("div", attrs={"class": "vNEEBe"}).text
        location = div.find("div", attrs={"class": "Qk80Jf"}).text
        location = location.split(",", 1)[0].strip()
        try:
            days_ago = div.find("span", attrs={"class": "LL4CDc"}).find("span").text
        except:
            days_ago = "N/A"
        now = datetime.now()
        current_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        job_list.append(
            [
                title,
                company_name,
                location,
                job_url,
                days_ago,
                "Google Jobs",
                current_time,
            ]
        )
    return job_list


async def main():
    url = "https://www.google.com/search?q=help+desk&sca_esv=913347e5f16b5bd8&biw=1912&bih=924&tbs=qdr:w&sxsrf=ACQVn0-XzptyZBbvMOQYfiSwA9QHMCsb5Q:1710901256124&ei=CEj6ZeWKB4Lt5NoPo9SG8Aw&uact=5&oq=jobs&gs_lp=Egxnd3Mtd2l6LXNlcnAiBGpvYnMyChAjGIAEGIoFGCcyCxAAGIAEGLEDGJIDMgsQABiABBiKBRiSAzIUEAAYgAQYigUYkQIYsQMYgwEYyQMyDRAAGIAEGIoFGEMYsQMyChAAGIAEGIoFGEMyChAAGIAEGIoFGEMyERAuGIAEGIoFGJECGMcBGNEDMgoQABiABBiKBRhDMgoQABiABBiKBRhDSJIYUABYwxZwAngAkAEAmAGpAaABmQaqAQMwLja4AQPIAQD4AQGYAgigArsGqAIRwgIXEC4YgAQYigUYkQIYsQMYgwEYxwEY0QPCAhAQLhhDGMcBGNEDGIAEGIoFwgILEAAYgAQYsQMYgwHCAg4QABiABBiKBRixAxiDAcICERAuGIAEGLEDGIMBGMcBGNEDwgIOEC4YgAQYsQMYxwEY0QPCAgQQIxgnwgIKEC4YgAQYigUYQ8ICFhAuGIAEGIoFGEMYsQMYgwEYxwEY0QPCAg4QLhiABBiKBRixAxiDAcICBxAjGOoCGCfCAhMQABiABBiKBRhDGOoCGLQC2AEBwgILEC4YgAQYsQMYgwHCAggQLhiABBixA8ICEBAuGIAEGIoFGEMYxwEYrwHCAggQABiABBiSA5gDB7oGBggBEAEYAZIHAzIuNqAHg4QB&sclient=gws-wiz-serp&ibp=htl;jobs&sa=X&ved=2ahUKEwi1_PTmnYOFAxVeGVkFHRCYB94QutcGKAF6BAgUEAU#fpstate=tldetail&htivrt=jobs&htichips=city:Owg_06VPwoli_nfhBo8LyA==&htischips=city;Owg_06VPwoli_nfhBo8LyA==:New York_comma_ NY"

    html_content = await get_page_source(url)
    job_list = parse_html_with_bs(html_content)
    for job in job_list:
        print(job)


asyncio.run(main())
