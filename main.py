import logging
import asyncio
import os
import sys
import os
from dotenv import load_dotenv # https://pypi.org/project/python-dotenv/
from telegram import Bot
from telegram.error import InvalidToken

from configs import ParserConfigs
from bot import main_loop
from exceptions import *


CAT_SUBREDDITS = ["cats", "blackcats", "OneOrangeBraincell", "danglers", "Catswithjobs", "airplaneears", "IllegallySmolCats", "catsareliquid", "Blep"]
GET_REQUEST_ATTEMPTS = 5
MIN_WAIT_TIME = 10 # seconds
MAX_WAIT_TIME = 15 # seconds


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

logger = logging.getLogger(__name__)


async def main():
    # loading .env file, file must be in the same dir
    # Example:
    #    .
    #    ├── .env
    #    └── main.py

    load_dotenv()
    
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    CHAT_ID = os.environ.get("CHAT_ID")

    if BOT_TOKEN is None:
        # just raise custom exception
        raise TokenNotFoundException()

    if CHAT_ID is None:
        raise ChatIdNotFoundException()

    try:
        bot = Bot(token=BOT_TOKEN)
        me = await bot.get_me() # Check token validity
        logger.info("Bot connected: @%s", me.username)
    except InvalidToken:
        raise InvalidTokenException()

    configs = ParserConfigs(
        min_time=MIN_WAIT_TIME,
        max_time=MAX_WAIT_TIME,
        max_request_attempts=GET_REQUEST_ATTEMPTS,
        cat_subreddits=CAT_SUBREDDITS
    )

    await main_loop(bot, CHAT_ID, configs)



if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: pass
    except Exception as ex:
        # do not skip any of critical exceptions
        logger.critical(ex)
