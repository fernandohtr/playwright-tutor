import asyncio
import time
import httpx

from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup as bs

from .common import Entry

COURTS = {
    "8.02": "tjal",
    "8.06": "tjce",
}


def get_court(number: str) -> str:
    a = number.split(".")[2]
    b = number.split(".")[3]

    numbers_from_court = ".".join([a, b])

    return COURTS[numbers_from_court]


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


async def tjce1_async(number):
    # 0070337-91.2008.8.06.0001
    url = f"https://esaj.tjce.jus.br/cpopg/show.do?processo.numero={number}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    return response.text


def tjce1_extract(page):
    soup = bs(page, "html.parser")
    try:
        classe = soup.find("span", id="classeProcesso").text
        assunto = soup.find("span", id="assuntoProcesso").text
        foro = soup.find("span", id="foroProcesso").text
        vara = soup.find("span", id="varaProcesso").text

        data = {
            "classe": classe,
            "assunto": assunto,
            "foro": foro,
            "vara": vara,
        }
        return data
    except:
        breakpoint()


async def tjce2_async(number):
    async with async_playwright() as p:
        async with await p.chromium.launch(headless=True) as browser:
            page = await browser.new_page()
            await page.goto("https://esaj.tjce.jus.br/cposg5/open.do")

            a = number.split(".")[0]
            b = number.split(".")[1]

            n1 = ".".join([a, b])
            n2 = number.split(".")[-1]

            await page.locator("#numeroDigitoAnoUnificado").fill(n1)
            await page.locator("#foroNumeroUnificado").fill(n2)
            await page.locator("#pbConsultar").click()
            await page.wait_for_selector("#modalIncidentes")
            await page.locator("#processoSelecionado").nth(0).click()
            await page.locator("#botaoEnviarIncidente").click()
            await page.wait_for_load_state("load")
            return await page.content()


def tjce2_extract(page):
        soup = bs(page, "html.parser")

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
            return data
        except:
            breakpoint()


async def tjce_main(number):
    tjce1_result, tjce2_result = await asyncio.gather(
        tjce1_async(number),
        tjce2_async(number)
    )

    return {
        "1st instance": tjce1_extract(tjce1_result),
        "2nd instance": tjce2_extract(tjce2_result),
    }


DOWNLOADER = {
    "tjal": None,
    "tjce": tjce_main,
}


async def async_main(entry: Entry):
    court = get_court(entry.process_number)
    return await DOWNLOADER[court](entry.process_number)


def main(entry: Entry):
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # If the loop is already running, create a task in the running loop
        return loop.create_task(async_main(entry))
    else:
        # Otherwise, start a new event loop
        return asyncio.run(async_main(entry))



if __name__ == "__main__":
    # start = time.perf_counter()

    # asyncio.run(tjce_main())

    # elapsed = time.perf_counter() - start
    # print(f"Program completed in {elapsed:0.5f} seconds.")

    with open("tjce.html") as f:
        page = f.read()

    tjce2_extract(page)
