import logging
import asyncio
import random
from io import BytesIO
from typing import Optional
from fake_useragent import UserAgent # https://pypi.org/project/fake-useragent/

import requests

from configs import ParserConfigs


#!TODO: make full async
#!TODO: remove configs to .conf file



# global variables
current_subreddit_index = 0
# removed user agent from headers to avoid bans
user_agent_manager = UserAgent()

logger = logging.getLogger(__name__)



# Returns the next element of the CAT_SUBREDDITS array.
# Loops back if the end is reached
def next_subreddit(subreddits: list[str]):
    global current_subreddit_index

    subreddit = subreddits[current_subreddit_index]
    current_subreddit_index = (current_subreddit_index + 1) % len(subreddits)

    return subreddit


# Returns the top posts of a subreddit
# time_filter: hour, day, week, month, year, all
def get_top_posts(subreddit: str, limit: int=10, time_filter:str="day", custom_headers: dict={}) -> Optional[dict]:
    logger.info(f"Getting top posts from r/{subreddit}")
    url = f"https://www.reddit.com/r/{subreddit}/top.json"

    try:
        response = requests.get(
            url, 
            headers={
                "User-Agent": user_agent_manager.random, # generate user agent for every request randomly
                **custom_headers # custom user headers
            }, 
            params={ # dont need another var for this
                "limit": limit,
                "t": time_filter
            }
        )
        response.raise_for_status()
        
        posts = response.json()["data"]["children"]
        return posts

    except Exception as e:
        # added some context
        logger.error(f"Error getting top posts from \n    url: {url}\n    Exception: {e}")
        # do not return None here, useless


# Takes a reddit post's url and provides the attached image.
def get_image_data(post: dict, custom_headers: dict={}) -> Optional[bytes]:
    # returns None if no image is attached
    
    try:
        url = post["data"]["url"]
    except Exception:
        logger.error("Post does not contain url")
        return None

    if not url.startswith("https://i.redd.it"):
        logger.warning(f"Post contains non-image data: {url}")
        return None

    try:
        img = requests.get(url, headers={
                "User-Agent": user_agent_manager.random, # generate user agent for every request randomly
                **custom_headers # custom user headers
            })
        logger.info(f"Retrieved image data from: {url}.")
        return img.content
    except Exception as e:
        # do not use another log message for the same action
        logger.error(f"Could not retreive post: {url}, exception: {e}")


def get_next_image_data(subreddits: list[str], attempts: int, custom_headers: dict) -> Optional[bytes]:
    for i in range(1, attempts+1):
        subreddit = next_subreddit(subreddits)
        top_posts = get_top_posts(subreddit, custom_headers=custom_headers)

        if not top_posts:
            logger.warning(f"No top posts found in r/{subreddit}. Trying next subreddit. (attempt {i})")
            continue

        logger.info(f"Found top posts in r/{subreddit}.")

        for post in top_posts:
            image_data = get_image_data(post, custom_headers=custom_headers)
            if image_data:
                logger.info(f"Retrieved image data from r/{subreddit}")
                return image_data

        logger.warning(f"No image data found in any post from r/{subreddit}. (attempt {i})")


async def send_picture(bot, image_data, chat_id) -> Optional[bytes]:
    await bot.send_photo(
        chat_id=chat_id,
        photo=BytesIO(image_data),
    )
    logger.info(f"Sent picture to {chat_id}.")


async def main_loop(bot, chat_id, configs: ParserConfigs):
    while True:
        sleep_time = random.randint(configs.min_time, configs.max_time) # removed magic values
        logger.info(f"Next picture will be sent in {sleep_time} seconds.")
        await asyncio.sleep(sleep_time)

        image_data = get_next_image_data(
            configs.cat_subreddits,
            configs.max_request_attempts,
            configs.custom_headers
        ) # attemps variable has not been used

        if not image_data:
            logger.error("Could not get an image to send. Skipping message")
            continue

        await send_picture(bot, image_data, chat_id)



