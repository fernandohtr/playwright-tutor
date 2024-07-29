import asyncio
import time

from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup as bs


def tjal1():
    with sync_playwright() as p:
        with p.chromium.launch(headless=True) as browser:
            page = browser.new_page()
            page.goto("https://www2.tjal.jus.br/cpopg/open.do")
            page.locator("#numeroDigitoAnoUnificado").fill("0710643-05.2024")
            page.locator("#foroNumeroUnificado").fill("0001")
            page.locator("#botaoConsultarProcessos").click()
            page.wait_for_load_state("load")

            soup = bs(page.content(), "html.parser")
            try:

                classe = soup.find("span", id="classeProcesso").text
                assunto = soup.find("span", id="assuntoProcesso").text
                foro = soup.find("span", id="foroProcesso").text
                vara = soup.find("span", id="varaProcesso").text
                juiz = soup.find("span", id="juizProcesso").text

                data = {
                    "classe": classe,
                    "assunto": assunto,
                    "foro": foro,
                    "vara": vara,
                    "juiz": juiz,
                }
                print(data)
            except:
                breakpoint()


def tjce2():
    with sync_playwright() as p:
        with p.chromium.launch(headless=True) as browser:
            page = browser.new_page()
            page.goto("https://esaj.tjce.jus.br/cposg5/open.do")

            page.locator("#numeroDigitoAnoUnificado").fill("0070337-91.2008")
            page.locator("#foroNumeroUnificado").fill("0001")
            page.locator("#pbConsultar").click()
            page.wait_for_selector("#modalIncidentes")
            page.locator("#processoSelecionado").nth(0).click()
            page.locator("#botaoEnviarIncidente").click()
            page.wait_for_load_state("load")
            soup = bs(page.content(), "html.parser")
            try:

                classe = soup.find("div", id="classeProcesso").find("span").text
                assunto = soup.find("div", id="assuntoProcesso").find("span").text
                secao = soup.find("div", id="secaoProcesso").find("span").text
                orgao = soup.find("div", id="orgaoJulgadorProcesso").find("span").text
                area = soup.find("div", id="areaProcesso").find("span").text

                data = {
                    "classe": classe,
                    "assunto": assunto,
                    "secao": secao,
                    "orgao": orgao,
                    "area": area,
                }
                print(data)
            except:
                breakpoint()


async def async_func():
    async with async_playwright() as p:
        async with await p.chromium.launch() as browser:
            page = await browser.new_page()
            await page.goto("https://www2.tjal.jus.br/cpopg/open.do")
            content = await page.content()
            soup = bs(content, "html.parser")
            ano = page.locator("#numeroDigitoAnoUnificado")
            print(soup.title)
            print(f"{ano = }")

    return content


async def tjce2_async():
    async with async_playwright() as p:
        async with await p.chromium.launch(headless=True) as browser:
            page = await browser.new_page()
            await page.goto("https://esaj.tjce.jus.br/cposg5/open.do")

            await page.locator("#numeroDigitoAnoUnificado").fill("0070337-91.2008")
            await page.locator("#foroNumeroUnificado").fill("0001")
            await page.locator("#pbConsultar").click()
            await page.wait_for_selector("#modalIncidentes")
            await page.locator("#processoSelecionado").nth(0).click()
            await page.locator("#botaoEnviarIncidente").click()
            await page.wait_for_load_state("load")
            soup = bs(await page.content(), "html.parser")
            try:

                classe = soup.find("div", id="classeProcesso").find("span").text
                assunto = soup.find("div", id="assuntoProcesso").find("span").text
                secao = soup.find("div", id="secaoProcesso").find("span").text
                orgao = soup.find("div", id="orgaoJulgadorProcesso").find("span").text
                area = soup.find("div", id="areaProcesso").find("span").text

                data = {
                    "classe": classe,
                    "assunto": assunto,
                    "secao": secao,
                    "orgao": orgao,
                    "area": area,
                }
                print(data)
            except:
                breakpoint()


start = time.perf_counter()

asyncio.run(tjce2_async())

elapsed = time.perf_counter() - start
print(f"Program completed in {elapsed:0.5f} seconds.")
