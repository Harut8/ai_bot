import asyncio
import os
from urllib.parse import urlparse

from httpx import AsyncClient, Response
from bs4 import BeautifulSoup as bs

from app.helper import add_content_to_db


class Scrapping:

    @staticmethod
    def is_valid_url(url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception as e:
            return False

    @staticmethod
    async def get_data(url: str) -> Response:
        try:
            async with AsyncClient(timeout=3) as client:
                response = await client.get(url)
                return response
        except Exception as e:
            raise e

    @staticmethod
    async def parse_async_queue(queue: asyncio.Queue):
        while True:
            get_from_queue = queue.get()
            try:
                url_to_parse = await asyncio.wait_for(get_from_queue, 3)
                data_to_parse = await Scrapping.get_data(url_to_parse)
                res = await Scrapping.scrap_data(data_to_parse)
                txt = res.find("div", {"class": "elementor-text-editor elementor-clearfix"}).text
                await add_content_to_db(txt)
            except asyncio.TimeoutError as e:
                break

    @staticmethod
    async def scrap_data(data: Response):
        try:
            soup = bs(data.text, 'html.parser')
            return soup
        except Exception as e:
            raise e

    @staticmethod
    async def get_sub_links(soup: bs):
        for a_href in soup.find_all("a", href=True, limit=5):
            url = a_href["href"]
            yield url

    @staticmethod
    async def put_url_into_queue(queue: asyncio.Queue, base_parsed_data: bs):
        async for url_needed_parse in Scrapping.get_sub_links(base_parsed_data):
            if Scrapping.is_valid_url(url_needed_parse):
                queue.put_nowait(url_needed_parse)

    @staticmethod
    async def scrap(url_to_parse: str) -> None:
        queue = asyncio.Queue()
        data_to_parse: Response = await Scrapping.get_data(url_to_parse)
        base_parsed_data = await Scrapping.scrap_data(data_to_parse)
        await asyncio.gather(
            Scrapping.put_url_into_queue(queue, base_parsed_data),
            Scrapping.parse_async_queue(queue),
        )
