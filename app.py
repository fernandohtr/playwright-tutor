import ast
import asyncio
import httpx
import re

from typing import Union

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup as bs

from .schemas import Entry, ProcessInfo, ErrorMessage
from .cache import client

# segredo de justica
# 0204051-13.2023.8.06.0296

ONE_HOUR = 60 * 60

COURTS = {
    "8.02": "tjal",
    "8.06": "tjce",
}


def main(entry: Entry) -> Union[ProcessInfo, ErrorMessage]:
    loop = asyncio.get_event_loop()
    if loop.is_running():
        return loop.create_task(get_process_data(entry))
    return asyncio.run(get_process_data(entry))


async def get_process_data(entry: Entry) -> Union[ProcessInfo, ErrorMessage]:
    cache = await client.get(entry.process_number)

    match_pattern = bool(re.search(r"^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$", entry.process_number))
    if not match_pattern:
        return ErrorMessage(error="Process number must have this parttern: XXXXXXX-XX.XXXX.X.XX.XXXX")
    
    if cache:
        data_str = cache.decode("utf-8")
        data_dict = ast.literal_eval(data_str)
        return data_dict

    DOWNLOADER = {
        "tjal": None,
        "tjce": tjce_main,
    }

    court = get_court(entry.process_number)
    return await DOWNLOADER[court](entry.process_number)


def get_court(number: str) -> str:
    a = number.split(".")[2]
    b = number.split(".")[3]

    numbers_from_court = ".".join([a, b])

    return COURTS[numbers_from_court]


async def tjce_main(number: str) -> ProcessInfo:
    tjce1_result, tjce2_result = await asyncio.gather(
        tjce1_async(number),
        tjce2_async(number),
    )

    data = {
        "first_instance": tjce1_extract(tjce1_result),
        "second_instance": tjce2_extract(tjce2_result),
    }

    data_str = str(data)
    await client.set(number, data_str, ex=ONE_HOUR)
    return ProcessInfo(**data)


async def tjce1_async(number: str) -> str:
    url = f"https://esaj.tjce.jus.br/cpopg/show.do?processo.numero={number}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    soup = bs(response.text, "html.parser")
    msg = soup.find("td", id="mensagemRetorno")

    if msg and (
        "Falha na tentativa de exibir detalhes" in msg.text or
        "Não existem informações disponíveis" in msg.text or
        "Não foi possível obter os dados do processo" in msg.text
    ):
        return ""
    return response.text


def tjce1_extract(page: str) -> dict | None:
    if not page:
        return None
    
    soup = bs(page, "html.parser")

    classe = soup.find("span", id="classeProcesso").text    
    assunto = soup.find("span", id="assuntoProcesso").text
    foro = soup.find("span", id="foroProcesso").text
    vara = soup.find("span", id="varaProcesso").text

    return {
        "classe": classe,
        "assunto": assunto,
        "foro": foro,
        "vara": vara,
    }


async def tjce2_async(number: str) -> str:
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

            await page.wait_for_load_state("load")
            first_page = await page.content()

            soup = bs(first_page, "html.parser")
            msg = soup.find("td", id="mensagemRetorno")

            if msg and (
                "Não foi possível executar esta operação" in msg.text or
                "deve ser preenchido" in msg.text or
                "Não existem informações disponíveis" in msg.text
            ):
                return ""

            if await page.query_selector("#processoSelecionado"):
                await page.locator("#processoSelecionado").nth(0).click()
                await page.locator("#botaoEnviarIncidente").click()
                await page.wait_for_load_state("load")
                return await page.content()
            return await page.content()


def tjce2_extract(page: str) -> dict | None:
        if not page:
            return None

        soup = bs(page, "html.parser")

        classe = soup.find("div", id="classeProcesso").find("span").text
        assunto = soup.find("div", id="assuntoProcesso").find("span").text
        secao = soup.find("div", id="secaoProcesso").find("span").text
        orgao = soup.find("div", id="orgaoJulgadorProcesso").find("span").text
        area = soup.find("div", id="areaProcesso").find("span").text

        return {
            "classe": classe,
            "assunto": assunto,
            "secao": secao,
            "orgao": orgao,
            "area": area,
        }
