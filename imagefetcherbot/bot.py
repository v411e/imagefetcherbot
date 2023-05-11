import asyncio
import json
from datetime import datetime, timedelta
from typing import Tuple, Type
import os

import pytz
from aiohttp.web import Request, Response
from maubot import Plugin, MessageEvent
from maubot.handlers import command, web
from mautrix.types import TextMessageEventContent, Format, MessageType
from mautrix.util import markdown

from .config import Config


class ImagefetcherBot(Plugin):
    config: Config

    async def start(self) -> None:
        self.config.load_and_update()

    @command.passive(
        regex=r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)(jpeg|JPEG|jpg|JPG|png|PNG|gif|GIF|svg|SVG|webp)"
    )
    async def download(self, evt: MessageEvent, match: Tuple[str]) -> None:
        inkserver_url = self.config.get("inkserver_url", None)
        if not inkserver_url:
            self.log.warning("inkserver_url not configured")
            return

        data = json.dumps({"url": match[0], "user": evt.sender})
        headers = {'content-type': 'application/json'}

        resp = await self.http.post(url=inkserver_url, data=data, headers=headers)
        if resp.status == 200:
            await evt.react("✅")
        else:
            await evt.react("❌")

    @web.get("/health")
    async def health(self, req: Request) -> Response:
        return Response(status=200)

    @classmethod
    def get_config_class(cls) -> Type[Config]:
        return Config
