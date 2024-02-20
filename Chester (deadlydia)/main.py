import discord, os
from discord.ext import commands
from discord import Webhook
discord.utils.setup_logging()
import discord, aiohttp, asyncio
from discord import Webhook
from secret import secret

username = ""

async def send(username, username2):
    url = "https://discord.com/api/webhooks/1157800901013164115/a5so_j9hTtKTY8jmigUVRfSCza5UbJzCVDEDsi7R-Zx4F4agbCQEfXVsD0Lqa4MHButG"
    async def anything(url):
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(url, session=session)
            embed = discord.Embed(title=f"{username2} is selling a head!!", description=f"{username} is selling a head. DM them about it.")
            await webhook.send("<@1050582024638959656> <@1117914448745738444>", embed=embed)
            
    if __name__ == "__main__":
        loop = asyncio.new_event_loop()
        loop.run_until_complete(await anything(url))
        loop.close()

async def send_two(username, username2):
    url = "https://discord.com/api/webhooks/1157800901013164115/a5so_j9hTtKTY8jmigUVRfSCza5UbJzCVDEDsi7R-Zx4F4agbCQEfXVsD0Lqa4MHButG"
    async def anything(url):
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(url, session=session)
            embed = discord.Embed(title=f"{username2} is buying a head!!", description=f"{username} is buying a head. DM them about it.")
            await webhook.send("<@1050582024638959656> <@1117914448745738444>", embed=embed)
            
    if __name__ == "__main__":
        loop = asyncio.new_event_loop()
        loop.run_until_complete(await anything(url))
        loop.close()


class InitBot(commands.Bot):
    async def setup_hook(self):
      print("-----------------------------------------------")
      print(f"Bot logged in as {self.user}")
      print("-----------------------------------------------")
activity = discord.Activity(type=discord.ActivityType.watching, name="over Chester | *help")
bot = InitBot(command_prefix="*", intents=discord.Intents.all(), activity=activity)

@bot.command(name="buy-head")
async def sell(ctx):
    await ctx.reply("Thank you! <@1050582024638959656> or <@1117914448745738444> will be with you soon.")
    await send_two(username=ctx.author.mention, username2=ctx.author)



@bot.command(name="sell-head")
async def sell(ctx):
    await ctx.reply("Thank you! <@1050582024638959656> or <@1117914448745738444> will be with you soon.")
    await send(username=ctx.author.mention, username2 = ctx.author)


bot.run(secret)