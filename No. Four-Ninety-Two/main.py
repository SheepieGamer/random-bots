import discord, aiohttp, datetime, asyncio, random, requests, os, chat_exporter, json
from itertools import cycle
from discord.ext import commands, tasks
from config import *
from emojify import emojify_image
from PIL import Image
from typing import Union
from discord.ui import Button, button, View
discord.utils.setup_logging()


class InitBot(commands.Bot):
    async def setup_hook(self):
      bot.add_view(CreateButton())
      bot.add_view(CloseButton())
      bot.add_view(TrashButton())
      print("-----------------------------------------------")
      print(f"Bot logged in as {self.user}")
      print("-----------------------------------------------")
    
bot = InitBot(command_prefix="*", intents=discord.Intents.all(), activity=discord.Game(name="*help | No. Four-Ninety-Two")) ############
#bot.remove_command("help") # remove ugly code block help command

async def end_giveaway(prize=None, channel=None, winner=None, users=None):
    winning_announcement = discord.Embed(color = 0xff2424)
    winning_announcement.set_author(name = f'THE GIVEAWAY HAS ENDED!', icon_url= 'https://i.imgur.com/DDric14.png')
    winning_announcement.add_field(name = f'🎉 Prize: {prize}', value = f'🥳 **Winner**: {winner.mention}\n 🎫 **Number of Entrants**: {len(users)}', inline = False)
    winning_announcement.set_footer(text = 'Thanks for entering!')
    await channel.send(f"{winner.mention}", embed = winning_announcement)

async def get_transcript(member: discord.Member, channel: discord.TextChannel):
  export = await chat_exporter.export(channel=channel)
  file_name=f"{member.id}.html"
  with open(f"ticket.html", "w", encoding="utf-8") as f:
    transcript = f.write(export)

  return transcript


async def send_log(title: str, guild: discord.Guild, description: str, color: discord.Color, file: discord.File):
    log_channel = guild.get_channel(1159612558060310679)
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    await log_channel.send(embed=embed, file=file)


class CreateButton(View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @button(label="Create Ticket",style=discord.ButtonStyle.blurple, emoji="🎫", custom_id="ticketopen")
    async def ticket(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        category: discord.CategoryChannel = discord.utils.get(interaction.guild.categories, id=1159588868585164932)
        for ch in category.text_channels:
            if ch.topic == f"{interaction.user.id} DO NOT CHANGE THE TOPIC OF THIS CHANNEL!":
                await interaction.followup.send("You already have a ticket open in {0}".format(ch.mention), ephemeral=True)
                return
        r1: discord.Role = interaction.guild.get_role(1159590026225647656)
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            r1: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        channel = await category.create_text_channel(
            name=f"{interaction.user}-ticket",
            topic=f"{interaction.user.id} DO NOT CHANGE THE TOPIC OF THIS CHANNEL!",
            overwrites=overwrites
        )
        await channel.send(
            embed=discord.Embed(
                title="Ticket Created!",
                description=f"Don't ping a staff member, they will be here soon.",
                color=discord.Color.random()
            ),
            view = CloseButton()
        )
        await channel.send(
            f"<@{interaction.user.id}>"
        )
        await interaction.followup.send(
            embed=discord.Embed(
                description="Created your ticket in {0}".format(channel.mention),
                color=discord.Color.random()
            ),
            ephemeral=True
        )
        await send_log(title="Ticket Created",
                       description="Created by {0}".format(interaction.user.mention),
                       color=discord.Color.random(),
                       guild=interaction.guild,
                       file=None
                       )

class CloseButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Close the ticket",style=discord.ButtonStyle.red, custom_id="closeticket",emoji="🔒")
    async def close(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)

        await interaction.channel.send("Closing this ticket in 3 seconds!")

        await asyncio.sleep(3)

        category: discord.CategoryChannel = discord.utils.get(interaction.guild.categories, id = 1159588902240276541)
        
        r1: discord.Role = interaction.guild.get_role(1159590026225647656)
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            r1: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        await interaction.channel.edit(category=category, overwrites=overwrites)
        await interaction.channel.send(
            embed=discord.Embed(description="Ticket Closed!", color = discord.Color.random()), view = TrashButton())
        member = interaction.guild.get_member(int(interaction.channel.topic.split(" ")[0]))
        await get_transcript(member=member, channel=interaction.channel)
        #file_name = upload(file_path=f'{member.id}.html', member_name=member.name)
        #link = f"https://brownsheepie2021.github.io/ticket/{file_name}.html"
        await send_log(
        title="Ticket Closed",
        description=f"Closed by: {interaction.user.mention}",
        color=discord.Color.random(),
        guild=interaction.guild,
        file=discord.File("ticket.html")
        )
        os.remove('ticket.html')

class TrashButton(View):
    def __init__(self):
        super().__init__(timeout=None)

        
    @button(label="Delete the ticket", style=discord.ButtonStyle.red,emoji="🗑️", custom_id="trash")
    async def trash(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.channel.send("Deleting the ticket in 3 seconds...")
        
        await asyncio.sleep(3)

        await interaction.channel.delete()


class HelpView(discord.ui.Select):
    def __init__(self):
        options=[
                discord.SelectOption(label="General", value="General"),
                discord.SelectOption(label="Fun & Games", value="Fun & Games"),
                discord.SelectOption(label="Moderation", value="Moderation")]
        super().__init__(placeholder="Select an option",max_values=1,min_values=1,options=options)
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "General":
          embed = discord.Embed(
                                title="Help: General", 
                                description="**Help:** Shows the message this is replying to\n**Ping:** Gets the bot's ping (latency) in milliseconds\n**Get invite:** Gets an invite link for No. Four-Ninety-Two that lasts 7 days\n**get-help:** Creates a Support Ticket for support", 
                                url="https://homemade.sheepiegamer20.com/sheepie-ai", 
                                color=discord.Color.random()
                                )
          await interaction.response.send_message(embed=embed, ephemeral=True)
        elif self.values[0] == "Fun & Games":
          embed = discord.Embed(
                                title="Help: Fun & Games", 
                                description=f"**Hack:** Pretends to hack the specified user\n**Emojify:** Turns an image url into an array of emojis\n**Tetris:** Plays a real and working game of Tetris in Discord!!\n**<@1157418281393721467>:** talk to an AI, after ``@pinging`` it reply to it with the mention feature ON", 
                                url="https://homemade.sheepiegamer20.com/sheepie-ai", 
                                color=discord.Color.random()
                                )
          await interaction.response.send_message(embed=embed, ephemeral=True)
        elif self.values[0] == "Moderation":
          embed = discord.Embed(
                                title="Help: Moderation", 
                                description="**Giveaway:** Starts a giveaway. Specify how long it should last (in minutes) then the prize\n**Mute:** Mutes a user. Specify the user to mute then the time muted (in development) \n**Ban:** Bans the specified user.\n**Kick:** Kicks the specified user, you may specify the reason\n**Purge:** Deletes the amount of messages specified, or all", 
                                url="https://homemade.sheepiegamer20.com/sheepie-ai", 
                                color=discord.Color.random()
                                )
          await interaction.response.send_message(embed=embed, ephemeral=True)

class Help(discord.ui.View):
    def __init__(self, *, timeout = 180):
        super().__init__(timeout=timeout)
        self.add_item(HelpView())

@bot.command()
async def healp(ctx):
    view = Help()
    embed = discord.Embed(title="Choose a Category", url="https://homemade.sheepiegamer20.com/sheepie-ai", color=discord.Color.random())
    embed.add_field(name="\nDifferent Categories", value="*General:*\n> random uncategorized commands\n*Fun & Games:*\n> commands about different games and fun things\n *Moderation:*\n> commands related to moderation")
    await ctx.reply(view=view, embed=embed)

@bot.command(name="setup-ticket")
@commands.has_permissions(administrator=True)
async def ticket(ctx):
    await ctx.send(
        embed=discord.Embed(
            description="Press the button to create a new ticket!"
        ),
        view=CreateButton()
    )


@bot.command(aliases=['k'])
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member,*,reason="No reason provided"):
    await ctx.reply(f"  {member} was kicked for reason: **{reason}**")
    await member.send(f":warning:Sorry! You were kicked for reason: **{reason}**")
    await member.kick(reason=reason)


@bot.command(aliases=['b'])
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member,*,reason="No reason provided"):
    try:
      embed = discord.Embed(title="  Banned", description=f"{member} was banned for reason: **{reason}**", color=discord.Color.random())
      await member.send(f":warning:Sorry! You were banned for reason: **{reason}**")
      await ctx.reply(embed=embed)
      await member.ban(reason=reason)
    except KeyError:
      pass



@bot.command(pass_context = True, help='clears messages above it based on the number passed in, or pass in "all" to purge all')
@commands.has_permissions(manage_guild=True)
async def purge(ctx, amount: str):
  if amount == "all":
    await ctx.channel.purge()
    embed = discord.Embed(title="Purged all messages", color = discord.Color.random())
    msg = await ctx.reply(embed=embed)
    await msg.add_reaction()
  else:
    await ctx.channel.purge(limit=(int(amount) + 1))
    embed = discord.Embed(title=f"Purged {amount} messages", color = discord.Color.random())
    await ctx.reply(embed=embed)


@bot.command(aliases=['unb'])
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int, *, reason=None):
    await ctx.reply(":warning: If it isn't working, make sure to put in the user's ID after ``s!unban``")
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user, reason=reason)
        embed = discord.Embed(title="  Unban", description=f"{user.name} ({user.id}) has been unbanned.", color=discord.Color.random())
        await ctx.reply(embed=embed)
    except discord.NotFound:
        embed = discord.Embed(title="  Error", description=f"Banned User with ID {user_id} not found.", color=discord.Color.random())
        await ctx.reply(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(title="  Error", description="I do not have permission to unban users, or this user is higher up on the role list than me.", color=discord.Color.random())
        await ctx.reply(embed=embed)
    except Exception as e:
        embed = discord.Embed(title="  Unkown Error", description=str(e), color=discord.Color.random())
        await ctx.reply(embed=embed)

@bot.command(name="ping")
async def ping(ctx):
  """
  get's the bots ping (latency) in milliseconds, no arguments
  """
  em = discord.Embed(
    title="Pong!",
    description="{0}ms".format(round(bot.latency * 1000, 1)),
    color=discord.Color.random()
  )
  await ctx.reply(embed=em)

@bot.command()
async def flatworm(ctx):
    """post's a beloved flatworm"""
    await ctx.reply("I love flatworms!!", file=discord.File("flatworm.gif"))




"""
@bot.command()
@commands.has_permissions(manage_guild=True)
async def giveaway(ctx, mins: float,*, prize: str):
  embed = discord.Embed(title="Giveaway! :tada:", description = f"{prize}", color = discord.Color.random())

  end = datetime.datetime.utcnow() + datetime.timedelta(seconds = mins * 60)

  embed.add_field(name= "Ends at: ", value = f"{end} UTC")
  embed.set_footer(text=f"Ends {mins} minutes from now!")

  first_msg = await ctx.reply(embed = embed)


  await first_msg.add_reaction("🥳")

  await asyncio.sleep(mins * 60)

  msg_reactions = await ctx.channel.fetch_message(first_msg.id)

  users = await msg_reactions.reactions[0].users().flatten()
  users.pop(users.index(bot.user))

  winner = random.choice(users)
  await ctx.reply(f"{winner} has won the giveaway for **{prize}**")
"""



@bot.command()
async def emojify(ctx, url: Union[discord.Member, str], size: int = 14, help="turns an image url into an array of emojis"):
    """turns an image url into an array of emojis"""
    if not isinstance(url, str):
        url = url.display_avatar.url

    def get_emojified_image():
        r = requests.get(url, stream=True)
        image = Image.open(r.raw).convert("RGB")
        res = emojify_image(image, size)

        if size > 14:
            res = f"```{res}```"
        return res

    result = await bot.loop.run_in_executor(None, get_emojified_image)
    await ctx.reply(result)




@bot.command()
async def hack(ctx, member: discord.Member):
    wait_time = 3
    await ctx.reply(f":keyboard::robot: Hacking <@{member.id}>!")
    await ctx.send(embed=discord.Embed(
        title=f"Aquiring Email...",
        color=discord.Color.random()
    ))
    await asyncio.sleep(wait_time)
    percent_one = random.randint(3, 38)
    await ctx.send(f"{percent_one}% done")
    await asyncio.sleep(wait_time - 1)
    percent_two = random.randint(41, 63)
    await ctx.send(f"{percent_two}% done")
    await asyncio.sleep(wait_time - 1)
    percent_three = random.randint(66, 92)
    await ctx.send(f"{percent_three}% done")
    await asyncio.sleep(wait_time - 1)
    await ctx.send("Email Hacked!")
    await asyncio.sleep(wait_time - 1)
    
    await ctx.send(embed=discord.Embed(
        title=f"Aquiring Passwords...",
        color=discord.Color.random()
    ))
    await asyncio.sleep(wait_time)
    percent_one = random.randint(3, 38)
    await ctx.send(f"{percent_one}% done")
    await asyncio.sleep(wait_time - 1)
    percent_two = random.randint(41, 63)
    await ctx.send(f"{percent_two}% done")
    await asyncio.sleep(wait_time - 1)
    percent_three = random.randint(66, 92)
    await ctx.send(f"{percent_three}% done")
    await asyncio.sleep(wait_time - 1)
    await ctx.send("Passwords Hacked!")
    await asyncio.sleep(wait_time - 1)
    
    await ctx.send(embed=discord.Embed(
        title=f"Aquiring IP Address...",
        color=discord.Color.random()
    ))
    percent_one = random.randint(3, 47)
    await ctx.send(f"{percent_one}% done")
    await asyncio.sleep(wait_time - 1)
    percent_two = random.randint(51, 92)
    await ctx.send(f"{percent_two}% done")
    await asyncio.sleep(wait_time - 1)
    await ctx.send("IP Hacked!")
    embed = discord.Embed(title=f"{member} has been successfully hacked!",description="Click [here](https://homemade.sheepiegamer20.com/hacked-credentials/28ADJFE122HS721HG/) to see all the credentials", color=discord.Color.random())
    await ctx.reply(embed=embed)



@bot.event 
async def on_message(message: discord.Message):
        if bot.user in message.mentions:
            message.channel.typing()
        if message.author.id != bot.user.id and not message.author.bot and bot.user in message.mentions:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BASE_URL}&uid={message.author.id}&msg={message.content}") as r:
                    if r.status != 200:
                        return await message.reply("An error occured while accessing the chat API!")
                    j = await r.json()

                    await message.reply(j['cnt'], mention_author=True)
        await bot.process_commands(message)



bot.run(TOKEN)