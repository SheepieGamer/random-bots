import discord, aiohttp, asyncio
from discord import Webhook
from main import username

url = "https://discord.com/api/webhooks/1157800901013164115/a5so_j9hTtKTY8jmigUVRfSCza5UbJzCVDEDsi7R-Zx4F4agbCQEfXVsD0Lqa4MHButG"
async def anything(url):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(url, session=session)
        embed = discord.Embed(title="test to see if it works")
        await webhook.send("<@1050582024638959656>", embed=embed)
        
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(anything(url))
    loop.close()
print(username)