import asyncio, discord, aiohttp, time
from discord import Webhook

while True:
    asyncio.sleep(602)
    async def anything(url):
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(url, session=session)
            await webhook.send("m/thing")

    if __name__ == "__main__":
        url = "https://discord.com/api/webhooks/1138247846177546494/1-Ekg-BTH9u69xl7dtonFmQPHu6D4M6X6uyPEgjuzEhgv3_cXlqh_o_9iLjCABkDszLE"

        loop = asyncio.new_event_loop()
        loop.run_until_complete(anything(url))
        loop.close()
        print("sent")