import discord
from discord.ui import Button, button, View
import typing
import random
from discord.ext import commands
from discord import app_commands
from discord import File
from asyncio import sleep
import chat_exporter
import datetime
import os, asyncio


activity = discord.Streaming(url="https://www.youtube.com/watch?v=rNYzyQAYBjg", name="midnightsmp.us.to")
status = discord.Activity(type=discord.ActivityType.streaming, name="midnightsmp.us.to")

intents = discord.Intents().all()
client = commands.Bot(command_prefix='m/', intents=intents, status=status, activity=activity)
intents.message_content = True

async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await client.load_extension(f"cogs.{filename[:-3]}")

@client.event  #                   STARTUP MESSAGE
async def on_ready():
  
  await client.tree.sync()
  client.add_view(CreateButton())
  client.add_view(CloseButton())
  client.add_view(TrashButton())
  print('----------------------------------------------------------------')
  print('RUNNING AS {0.user}'.format(client))
  print('----------------------------------------------------------------')




# GET TRANSCRIPT
async def get_transcript(member: discord.Member, channel: discord.TextChannel):
  export = await chat_exporter.export(channel=channel)
  #file_name=f"{member.id}.html"
  with open(f"ticket.html", "w", encoding="utf-8") as f:
    transcript = f.write(export)

  return transcript
    

  


async def send_log(title: str, guild: discord.Guild, description: str, color: discord.Color, file: discord.File):
  log_channel = guild.get_channel(1083504881744224367)
  embed = discord.Embed(
    title=title,
    description=description,
    color=color
  )
  await log_channel.send(embed=embed, file=file)
class CreateButton(View):
  def __init__(self):
    super().__init__(timeout=None)

  @button(label="Create Ticket",style=discord.ButtonStyle.blurple, emoji="🎟️", custom_id="ticketopen")
  async def ticket(self, interaction: discord.Interaction, button: Button):
    await interaction.response.defer(ephemeral=True)
    category: discord.CategoryChannel = discord.utils.get(interaction.guild.categories, id=1136755261814616064)
    for ch in category.text_channels:
      if ch.topic == f"{interaction.user.id} DO NOT CHANGE THE TOPIC OF THIS CHANNEL, IT WILL BREAK THINGS!":
        await interaction.followup.send("You already have a ticket in {0}".format(ch.mention), ephemeral=True)
        return
    r1 : discord.Role = interaction.guild.get_role(1070063627333275688)
    overwrites = {
      interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
      r1: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
      interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
      interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    channel = await category.create_text_channel(
      name=f"{interaction.user}s ticket",
      topic=f"{interaction.user.id} DO NOT CHANGE THE TOPIC OF THIS CHANNEL, IT WILL BREAK THINGS!",
      overwrites = overwrites
    )
    await channel.send(f'Welcome <@{interaction.user.id}>')
    await channel.send(
      embed=discord.Embed(
      title="Ticket Created!",
      description="Please don't ping staff members more, wait for a response.",
      color = discord.Color.green()
      ),
      view = CloseButton()
    )
    await channel.send('<@&1070063627333275688> will be with you soon')
    await interaction.followup.send(
      embed=discord.Embed(
      description = "Created your ticket in {0}".format(channel.mention),
      color = discord.Color.blurple()
      ),
      ephemeral=True
    )
    await send_log(
      title="Ticket Created",
      description="Created by {0}".format(interaction.user.mention),
      color=discord.Color.green(),
      guild=interaction.guild,
      file=None
    )

class CloseButton(View):
  def __init__(Self):
    super().__init__(timeout=None)

  @button(label="Close the ticket",style=discord.ButtonStyle.red, custom_id="close-tickets",emoji="🔒")
  async def close(self, interaction: discord.Interaction, button: Button):
    await interaction.response.defer(ephemeral=True)

    await interaction.channel.send("Closing Ticket...")

    await sleep(3)

    category: discord.CategoryChannel = discord.utils.get(interaction.guild.categories, id = 1136767797200949391)
    
    r1 : discord.Role = interaction.guild.get_role(1070063627333275688)
    
    overwrites = {
      interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
      r1: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
      interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }

    await interaction.channel.edit(category=category, overwrites=overwrites)

    await interaction.channel.send(
      embed=discord.Embed(
        description="This ticket has been closed."
      ),
      view=TrashButton()
    )

    member = interaction.guild.get_member(int(interaction.channel.topic.split(" ")[0]))
    await get_transcript(member=member, channel=interaction.channel)
    #file_name = upload(file_path=f'{member.id}.html', member_name=member.name)
    #link = f"https://brownsheepie2021.github.io/ticket/{file_name}.html"
    await send_log(
      title="Ticket Closed",
      description=f"Closed by : {interaction.user.mention}",
      color=discord.Color.yellow(),
      guild=interaction.guild,
      file=discord.File("ticket.html")
    )
    os.remove('ticket.html')

class TrashButton(View):
  def __init__(self):
    super().__init__(timeout=None)

  @button(label="Delete the ticket", style=discord.ButtonStyle.red, emoji="🗑️", custom_id="delete")
  async def trash(self, interaction: discord.Interaction, button: Button):
    await interaction.response.defer()
    await interaction.channel.send("Deleting Ticket...")
    await sleep(3)

    await interaction.channel.delete()


#                                COMMANDS
@client.command()
@commands.has_permissions(manage_guild=True)
async def giveaway(ctx, mins: int, prize: str):
  embed = discord.Embed(title="Giveaway! :tada:", description = f"{prize}", color = discord.Color.random())

  end = datetime.datetime.utcnow() + datetime.timedelta(seconds = mins * 60)

  embed.add_field(name= "Ends at: ", value = f"{end} UTC")
  embed.set_footer(text=f"Ends {mins} minutes from now!")

  first_msg = await ctx.send(embed = embed)


  await first_msg.add_reaction("🥳")

  await asyncio.sleep(mins * 60)

  msg_reactions = await ctx.channel.fetch_message(first_msg.id)

  users = await msg_reactions.reactions[0].users().flatten()
  users.pop(users.index(client.user))

  winner = random.choice(users)

  await ctx.send(f"Congratulations! {winner.mention} won **{prize}**!!! :tada: :tada:")

@client.command(name='ticket')
@commands.has_permissions(administrator=True)
async def ticket(ctx):
  await ctx.send(
    embed = discord.Embed(
      description='Press the button to create a new ticket!'
    ),
    view = CreateButton()
  )

@client.tree.command(name='support-ticket', description='get support or contact staff by opening a ticket')
async def support_ticket(interaction: discord.Interaction):
  await interaction.response.send_message(
    embed = discord.Embed(
      description='Press the button to create a new ticket!'
    ),
    view = CreateButton(),
    ephemeral=True
  )

@client.tree.command(name='ping', description='get the bots ping')
async def ping(interaction: discord.Interaction):
  bot_ping = round(client.latency * 1000)
  await interaction.response.send_message(f"The bots ping is {bot_ping} ms.")

@client.command(name='stats', description='set up stats for the server')
async def stats(ctx):
    members = []
    bots = []
    async for user in ctx.guild.fetch_members(limit=None):
        if user.bot:
            bots.append(user)
            await asyncio.sleep(2)
        else:
            members.append(user)
            await asyncio.sleep(2)
    memberNum = len(members)
    botNum = len(bots)
    total = memberNum + botNum
    await ctx.send(f"bots: {botNum}\nmembers: {memberNum}\ntotal: {total}")
    await client.get_channel(1065389925316436098).edit(name=f"All Members: {total}")
    await asyncio.sleep(2)
    await client.get_channel(1065389929359749231).edit(name=f"Members: {memberNum}")
    await asyncio.sleep(2)
    await client.get_channel(1065389933797318687).edit(name=f"Bots: {botNum}")
    await asyncio.sleep(2)

@client.tree.command(name='invite', description='invite link for Midnight Projects')
async def invite(interaction: discord.Interaction):
  embed=discord.Embed(title="Invite all your friends:\nhttps://discord.gg/cZMjuY4wQW", color=0xFF5555)
  embed.set_author(name="Midnight Projects#6814", icon_url="https://cdn.discordapp.com/attachments/980990414972674088/1084582260671512576/amazing_moon.png")
  embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/980990414972674088/1084582260671512576/amazing_moon.png")
  embed.set_footer(text="Developed by @sheepiegamer")
  await interaction.response.send_message(embed=embed, ephemeral=True)

@client.tree.command(name='info', description='get information about the bot')
async def info(interaction: discord.Interaction):
  bot_ping = round(client.latency * 1000)
  members = []
  bots = []
  async for user in interaction.guild.fetch_members(limit=None):
      if user.bot:
          bots.append(user)
      else:
          members.append(user)
  memberNum = len(members)
  botNum = len(bots)
  total = memberNum + botNum
  embed=discord.Embed(title="Info", description=f'Creator: **@sheepiegamer**\nPing: {bot_ping}ms\n     __Server Stats__\n{memberNum} members,\n{botNum} bots\nTotal: {total}\nServer I am built for: :link: https://discord.gg/cZMjuY4wQW\n:fire: Add other bots made by **@sheepiegamer** to your servers: :link: https://discord.gg/Xq44fY3Fdv :fire:', color=0xFF5555)
  embed.set_author(name="Midnight Projects#6814", icon_url="https://cdn.discordapp.com/attachments/980990414972674088/1084582260671512576/amazing_moon.png")
  embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/980990414972674088/1084582260671512576/amazing_moon.png")
  embed.set_footer(text="Developed by @sheepiegamer")
  await interaction.response.send_message(embed=embed, ephemeral=True)

@client.tree.command(name='warn', description='wan a member for breaking the rules')
@app_commands.describe(member='the member you want to warn')
async def warn(ctx, member: discord.Member, punishment: typing.Literal['warn1', 'warn2', 'warn3', 'banwarn1', 'banwarn2', 'banwarn3']):
  
  if punishment == 'warn1':
    punishment = ctx.guild.get_role(1011811606692368384)
    await member.add_roles(punishment)
    embed=discord.Embed(title="Success!", description='User has been warned for the first time!', color=0xFF5555)
    embed.set_author(name="Midnight Projects#6814", icon_url="https://cdn.discordapp.com/attachments/980990414972674088/1084582260671512576/amazing_moon.png")
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/980990414972674088/1084582260671512576/amazing_moon.png")
    embed.set_footer(text="Developed by @sheepiegamer")
    await ctx.response.send_message(embed=embed, ephemeral=True)
  if punishment == 'warn2':
    punishment = ctx.guild.get_role(1011811838897434747)
    await member.add_roles(punishment)
    embed=discord.Embed(title="Success!", description='User has been warned for the second time!', color=0xFF5555)
    embed.set_author(name="Midnight Projects#6814", icon_url="https://cdn.discordapp.com/attachments/980990414972674088/1084582260671512576/amazing_moon.png")
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/980990414972674088/1084582260671512576/amazing_moon.png")
    embed.set_footer(text="Developed by @sheepiegamer")
    await ctx.response.send_message(embed=embed, ephemeral=True)
  if punishment == 'warn3':
    punishment = ctx.guild.get_role(1011811950759530546)
    await member.add_roles(punishment)
    embed=discord.Embed(title="Success!", description='User has been warned for the third time!', color=0xFF5555)
    embed.set_author(name="Midnight Projects#6814", icon_url="https://cdn.discordapp.com/attachments/980990414972674088/1084582260671512576/amazing_moon.png")
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/980990414972674088/1084582260671512576/amazing_moon.png")
    embed.set_footer(text="Developed by @sheepiegamer")
    await ctx.response.send_message(embed=embed, ephemeral=True)
  if punishment == 'banwarn1':
    punishment = ctx.guild.get_role(1011813692016447569)
    await member.add_roles(punishment)
    embed=discord.Embed(title="Success!", description='User has been banwarned for the first time!', color=0xFF5555)
    embed.set_author(name="Midnight Projects#6814", icon_url="https://cdn.discordapp.com/attachments/980990414972674088/1084582260671512576/amazing_moon.png")
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/980990414972674088/1084582260671512576/amazing_moon.png")
    embed.set_footer(text="Developed by @sheepiegamer")
    await ctx.response.send_message(embed=embed, ephemeral=True)
  if punishment == 'banwarn2':
    punishment = ctx.guild.get_role(1011813851618099404)
    await member.add_roles(punishment)
    embed=discord.Embed(title="Success!", description='User has been banwarned for the second time!', color=0xFF5555)
    embed.set_author(name="Midnight Projects#6814", icon_url="https://cdn.discordapp.com/attachments/980990414972674088/1084582260671512576/amazing_moon.png")
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/980990414972674088/1084582260671512576/amazing_moon.png")
    embed.set_footer(text="Developed by @sheepiegamer")
    await ctx.response.send_message(embed=embed, ephemeral=True)  
  if punishment == 'banwarn3':
    punishment = ctx.guild.get_role(1011813981230481531)
    await member.add_roles(punishment)
    embed=discord.Embed(title="Success!", description='User has been banwarned for the third time!', color=0xFF5555)
    embed.set_author(name="Midnight Projects#6814", icon_url="https://cdn.discordapp.com/attachments/980990414972674088/1084582260671512576/amazing_moon.png")
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/980990414972674088/1084582260671512576/amazing_moon.png")
    embed.set_footer(text="Developed by @sheepiegamer")
    await ctx.response.send_message(embed=embed, ephemeral=True)

@client.tree.command(name='mute', description='mute a member')
@app_commands.describe(member='the member you want to mute', duration='how long you would like to mute them in minutes')
async def mute(ctx, member: discord.Member, duration: float):
  mute = ctx.guild.get_role(884950529577467934)
  await member.add_roles(mute)
  embed=discord.Embed(title="Success!", description=f'User has been muted for {duration} minute(s)!', color=0xFF5555)
  embed.set_author(name="Midnight Projects#6814", icon_url="https://cdn.discordapp.com/attachments/980990414972674088/1084582260671512576/amazing_moon.png")
  embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/980990414972674088/1084582260671512576/amazing_moon.png")
  embed.set_footer(text="Developed by @sheepiegamer")
  await ctx.response.send_message(embed=embed, ephemeral=True)
  time = duration * 60
  await asyncio.sleep(time)
  await member.remove_roles(mute)

@client.tree.command(name='tempban', description='temporarily ban a member')
@app_commands.describe(member='the member you want to tempban')
async def tempban(ctx, member: discord.Member):
  tempban = ctx.guild.get_role(1011988893714890762)
  await member.add_roles(tempban)
  embed=discord.Embed(title="Success!", description='User has been temp-banned!', color=0xFF5555)
  embed.set_author(name="Midnight Projects#6814", icon_url="https://cdn.discordapp.com/attachments/980990414972674088/1084582260671512576/amazing_moon.png")
  embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/980990414972674088/1084582260671512576/amazing_moon.png")
  embed.set_footer(text="Developed by @sheepiegamer")
  await ctx.response.send_message(embed=embed, ephemeral=True)
  await asyncio.sleep(604800)
  await member.remove_roles(tempban)

@client.tree.command(name='minecraft-server', description='join the minecraft server')
async def minecraft_server(interaction: discord.Interaction):
  embed=discord.Embed(title="Minecraft Server", description='Java: midnightsmp.us.to\nBedrock: \n    IP: midnightsmp.us.to\n    Port: 25565\n **Visit <#1041835352157077686> for more infomation for bedrock!**', color=0xFF5555)
  embed.set_author(name="Midnight Projects#6814", icon_url="https://cdn.discordapp.com/attachments/980990414972674088/1084582260671512576/amazing_moon.png")
  embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/980990414972674088/1084582260671512576/amazing_moon.png")
  embed.set_footer(text="Developed by @sheepiegamer")
  await interaction.response.send_message(embed=embed, ephemeral=True)

@client.tree.command(name='report', description='report a bug or user to the staff')
async def report(interaction: discord.Interaction):
  embed=discord.Embed(title="Report something", description='Please go to <#1011693848344408106> for support', color=0xFF5555)
  embed.set_author(name="Midnight Projects#6814", icon_url="https://cdn.discordapp.com/attachments/980990414972674088/1084582260671512576/amazing_moon.png")
  embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/980990414972674088/1084582260671512576/amazing_moon.png")
  embed.set_footer(text="Developed by @sheepiegamer")
  await interaction.response.send_message(embed=embed, ephemeral=True)

@client.tree.command(name='help', description='shows a list of all commands')
async def help(interaction: discord.Interaction):
  embed=discord.Embed(title="Help", description="**/help** - this menu\n**/invite** - gets the invite link for **Midnight Projects**\n**/ping** - gets the bot's ping(ms)\n**/info** - gets information about the bot\n**/minecraft-server** - gets instructions on how to join the minecraft server\n**/report** - report a bug or user to the staff team\n\n__ADMIN COMMANDS__\n**/warn** - warn a member\n**/mute** - mute a member\n**/tempban** - temporarily ban a member", color=0xFF5555)
  embed.set_author(name="Midnight Projects#6814", icon_url="https://cdn.discordapp.com/attachments/980990414972674088/1084582260671512576/amazing_moon.png")
  embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/980990414972674088/1084582260671512576/amazing_moon.png")
  embed.set_footer(text="Developed by @sheepiegamer")
  await interaction.response.send_message(embed=embed, ephemeral=True)

client.run('MTEyMzcwMTM0NTA2MTQ0NTYzMg.GcaGBj.U1wCkbkXi-Dh_j4nedzOFewgyJgfi7AABnQ90I')
