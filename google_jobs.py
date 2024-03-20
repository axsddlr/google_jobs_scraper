from playwright.async_api import async_playwright
import asyncio
from bs4 import BeautifulSoup


async def get_page_source(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            viewport={"width": 1280, "height": 720},
            java_script_enabled=True,
        )
        page = await context.new_page()
        await page.goto(url, wait_until="networkidle")

        # Function to scroll within a specific <div>
        async def scroll_within_div(selector, scrollHeight):
            await page.evaluate(f"""
            const div = document.querySelector('{selector}');
            if (div) {{
                div.scrollTop += {scrollHeight};
            }}
            """)

        # Example usage: Scroll within a div with class "zxU94d gws-plugins-horizon-jobs__tl-lvc"
        # Adjust the number of scrolls and scrollHeight as needed
        for _ in range(15):  # Number of times to scroll
            await scroll_within_div(
                ".zxU94d.gws-plugins-horizon-jobs__tl-lvc", 500
            )  # Scroll down 500 pixels each time
            await page.wait_for_timeout(2000)  # Wait for 2 seconds for content to load

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
        except AttributeError:
            pass
        title = div.find("div", attrs={"class": "BjJfJf PUpOsf"}).text
        company_name = div.find("div", attrs={"class": "vNEEBe"}).text
        location = div.find("div", attrs={"class": "Qk80Jf"}).text
        location = location.split(",", 1)[0].strip()

        salary_div = div.find("div", class_="I2Cbhb bSuYSc")
        salary = None  # Initialize salary as None to check later
        if salary_div:
            salary_info = salary_div.find("span", class_="LL4CDc")
            if salary_info:
                salary = "$" + salary_info.text.strip()

        try:
            days_ago = div.find("span", attrs={"class": "LL4CDc"}).find("span").text
        except AttributeError:
            days_ago = "N/A"

        # Construct the job list entry
        job_entry = [title, company_name, location, job_url, days_ago, "Google Jobs"]
        if salary:
            job_entry.insert(4, salary)  # Insert salary before 'days_ago' if it exists

        job_list.append(job_entry)
    return job_list


async def main():
    word = "help desk"
    url = f"https://www.google.com/search?q={word}k&sca_esv=913347e5f16b5bd8&biw=1912&bih=924&tbs=qdr:w&sxsrf=ACQVn0-XzptyZBbvMOQYfiSwA9QHMCsb5Q:1710901256124&ei=CEj6ZeWKB4Lt5NoPo9SG8Aw&uact=5&oq=jobs&gs_lp=Egxnd3Mtd2l6LXNlcnAiBGpvYnMyChAjGIAEGIoFGCcyCxAAGIAEGLEDGJIDMgsQABiABBiKBRiSAzIUEAAYgAQYigUYkQIYsQMYgwEYyQMyDRAAGIAEGIoFGEMYsQMyChAAGIAEGIoFGEMyChAAGIAEGIoFGEMyERAuGIAEGIoFGJECGMcBGNEDMgoQABiABBiKBRhDMgoQABiABBiKBRhDSJIYUABYwxZwAngAkAEAmAGpAaABmQaqAQMwLja4AQPIAQD4AQGYAgigArsGqAIRwgIXEC4YgAQYigUYkQIYsQMYgwEYxwEY0QPCAhAQLhhDGMcBGNEDGIAEGIoFwgILEAAYgAQYsQMYgwHCAg4QABiABBiKBRixAxiDAcICERAuGIAEGLEDGIMBGMcBGNEDwgIOEC4YgAQYsQMYxwEY0QPCAgQQIxgnwgIKEC4YgAQYigUYQ8ICFhAuGIAEGIoFGEMYsQMYgwEYxwEY0QPCAg4QLhiABBiKBRixAxiDAcICBxAjGOoCGCfCAhMQABiABBiKBRhDGOoCGLQC2AEBwgILEC4YgAQYsQMYgwHCAggQLhiABBixA8ICEBAuGIAEGIoFGEMYxwEYrwHCAggQABiABBiSA5gDB7oGBggBEAEYAZIHAzIuNqAHg4QB&sclient=gws-wiz-serp&ibp=htl;jobs&sa=X&ved=2ahUKEwi1_PTmnYOFAxVeGVkFHRCYB94QutcGKAF6BAgUEAU#fpstate=tldetail&htivrt=jobs&htichips=city:Owg_06VPwoli_nfhBo8LyA%3D%3D&htischips=city;Owg_06VPwoli_nfhBo8LyA%3D%3D:New%20York_comma_%20NY&htidocid=Bp54_2RY361z7YR9AAAAAA%3D%3D"
    html_content = await get_page_source(url)
    job_list = parse_html_with_bs(html_content)
    for job in job_list:
        print(job)


asyncio.run(main())
