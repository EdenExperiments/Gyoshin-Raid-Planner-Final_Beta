import discord
import os
import dotenv
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord_components import DiscordComponents, Button, ButtonStyle
from Commands import Templates
from Commands import AddDefaultTemplates
from Commands import AddTemplate
from Commands import UpdateTemplate
from Commands import DeleteTemplate
from Commands import Create
from Commands import Runs
from Commands import Commands
from Commands import Roles
from Commands import Dismiss
from Commands import AddRun
from Commands import MyRuns
from Helpers import DeleteOldRaidDataHelper
from Helpers import ButtonInteractionHelper
from Scripts import MakeDatabase
from Scripts import InsertMasterData

# Enable privileged gateway intents as described on 
# https://discordpy.readthedocs.io/en/latest/intents.html 
# so we can access member objects to retrieve display names and use reactions
intents = discord.Intents.default()
intents.members = True
intents.reactions = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
  print("Ready!")
  DiscordComponents(bot)

  # Nightly job to clean up old data
  @tasks.loop(minutes=60.0)
  async def CleanUpOldRaidData():
    if datetime.utcnow().hour == 5:
      print("Starting cleanup of old raid data!")
      await DeleteOldRaidDataHelper.DeleteOldRaidData()
  CleanUpOldRaidData.start()

# Clean up a users' data after they left the server
@bot.event
async def on_member_leave(member):
  print("leave detected!")
  await MemberHelper.OnMemberLeaveOrRemove(member)
  
# Clean up a users' data after they've been kicked from the server
@bot.event
async def on_member_remove(member):
  print("kick or ban detected!")
  await MemberHelper.OnMemberLeaveOrRemove(member)

# Bot commands
@bot.command(name='templates', aliases=['Templates'])
async def templates(ctx):
  await Templates.GetTemplates(ctx.message, bot)
  
@bot.command(name='create', aliases=['Create'])
async def create(ctx):
  await Create.CreateRaid(ctx.message, bot)
  
@bot.command(name='runs', aliases=['Runs'])
async def runs(ctx):
  await Runs.ListRunsOnDate(ctx.message, bot)
  
@bot.command(name='commands', aliases=['Commands'])
async def commands(ctx):
  await Commands.ListCommands(ctx.message)
  
@bot.command(name='roles', aliases=['Roles'])
async def roles(ctx):
  await Roles.ListRoles(ctx.message)
  
@bot.command(name='addrun', aliases=['Addrun'])
async def addrun(ctx):
  await AddRun.AddRunInDM(ctx.message, bot)
  
@bot.command(name='adddefaulttemplates', aliases=['Adddefaulttemplates','AddDefaultTemplates'])
async def adddefaulttemplates(ctx):
  await AddDefaultTemplates.AddDefaultTemplates(ctx.message)
  
@bot.command(name='addtemplate', aliases=['Addtemplate','AddTemplate'])
async def addtemplate(ctx):
  await AddTemplate.AddTemplate(ctx.message, bot)
  
@bot.command(name='updatetemplate', aliases=['Updatetemplate','UpdateTemplate'])
async def updatetemplate(ctx):
  await UpdateTemplate.UpdateTemplate(ctx.message, bot)
  
@bot.command(name='deletetemplate', aliases=['Deletetemplate','DeleteTemplate'])
async def deletetemplate(ctx):
  await DeleteTemplate.DeleteTemplate(ctx.message, bot)
  
@bot.command(name='dismiss', aliases=['Dismiss'])
async def dismiss(ctx):
  await Dismiss.DismissMember(ctx.message, bot)
  
@bot.command(name='myruns', aliases=['Myruns','MyRuns'])
async def myruns(ctx):
  await MyRuns.ListMyRuns(ctx.message, bot)
  
@bot.command(name='makedatabase', aliases=['Makedatabase','MakeDatabase'])
async def makedatabase(ctx):
  await MakeDatabase.MakeDatabase(ctx.message)
  
@bot.command(name='insertmasterdata', aliases=['Insertmasterdata','InsertMasterdata'])
async def insertmasterdata(ctx):
  await InsertMasterData.InsertMasterData(ctx.message)
  
@bot.command(name='inserttestdata', aliases=['Inserttestdata','InsertTestdata'])
async def inserttestdata(ctx):
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()
  c.execute(f"UPDATE Raids SET OrganizerUserID = 629273364543963147 WHERE ID = 222")
  c.execute(f"UPDATE RaidMembers SET UserID = 629273364543963147 WHERE ID = 1254")
  #c.execute(f"INSERT INTO RaidMembers (UserID, Origin, RaidID, RoleID) VALUES (773276648279375882, 872435633082236969, 219, 2)")
  #c.execute(f"INSERT INTO RaidMembers (UserID, Origin, RaidID, RoleID) VALUES (317337551138586654, 872435633082236969, 219, 2)")
  conn.commit()
  conn.close()

# Message events
# Do nothing if the message is from the bot
@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  # Process commmands if found in message 
  await bot.process_commands(message)

# Button events
@bot.event
async def on_button_click(interaction):
  await ButtonInteractionHelper.OnButtonClick(interaction, bot)

# Get bot token and run on server
load_dotenv()
bot.run(os.getenv('Token'))