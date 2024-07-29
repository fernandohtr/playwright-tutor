import asyncio
import time

from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup as bs

def sync_func():
    with sync_playwright() as p:
        with p.chromium.launch() as browser:
            page = browser.new_page()
            page.goto("https://playwright.dev/")
            # print(dir(page))
            content = page.content()
            soup = bs(content, "html.parser")
            print(soup.title)


async def async_func():
    async with async_playwright() as p:
        async with await p.chromium.launch() as browser:
            page = await browser.new_page()
            await page.goto("https://playwright.dev/")
            content = await page.content()
            soup = bs(content, "html.parser")
            print(soup.title)

    return content


start = time.perf_counter()

# sync_func()
asyncio.run(async_func())

elapsed = time.perf_counter() - start
print(f"Program completed in {elapsed:0.5f} seconds.")
