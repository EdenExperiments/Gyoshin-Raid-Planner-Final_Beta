import re
import sqlite3
from discord_components import DiscordComponents, Button, ButtonStyle
from Helpers import ButtonInteractionHelper
from Helpers import DateTimeFormatHelper
from Helpers import RoleHelper
from Helpers import OriginHelper
from Helpers import UserHelper
from Helpers import RoleIconHelper
from Helpers import DMHelper
from Helpers import ReactionHelper

async def CreateRaid(message, bot):
  commands = message.content.split()
  
  # Obtain server ID
  Origin = await OriginHelper.GetOrigin(message)
  if not Origin:
    return

  # Get Index values for commands
  try:
    DateIndex = commands.index("!date")
    RoleIndex = commands.index("!role")
  except ValueError:
    await DMHelper.DMUser(message, f"!date or !role not found in your message, please make sure you add these commands to your message.")
    return

  # Assign values to variables 
  try:
    Date = commands[DateIndex + 1]
    Time = commands[DateIndex + 2]
    Role = commands[RoleIndex + 1]
    DateTime = Date + " " + Time
    ChannelID = message.channel.id
  except:
    await DMHelper.DMUser(message, f"Unable to assign variables, please specify values after your commands.")
    return

  #DateTime verification
  pattern = re.compile(r'((\d{2})-(\d{2})-(\d{4})) (\d{2}):(\d{2})')
  match = pattern.match(DateTime)

  if not match:
    await DMHelper.DMUser(message, f"Invalid date and time detected, please use the dd-mm-yyyy hh:mm format")
    return

  # Sent datetime to function to format for SQL
  try:
    sqldatetime = await DateTimeFormatHelper.LocalToSqlite(message, DateTime)
    
    if not sqldatetime:
      return
  except:
    return

  # Role verification
  try:     
    RoleID = await RoleHelper.GetRoleID(Role)
  except:
    await DMHelper.DMUser(message, f"Invalid role, please enter a valid role, you can call !Roles to see available roles.")
    return

  # Creating variables for number of players in role, making one for role creator has chosen
  NumberOfCurrentTanks = 0
  NumberOfCurrentDps = 0
  NumberOfCurrentHealers = 0

  if Role == "tank":
    NumberOfCurrentTanks = 1
  elif Role == "dps":
    NumberOfCurrentDps = 1
  elif Role == "healer":
    NumberOfCurrentHealers = 1
  else:
    pass

  # 1 Create raid without template, 
  # 1.1 Example command !CreateRaid TestRaid !DateTime 01-08-2021 19:00 !NrOfPlayers 24 !NrOfTanks 3 !NrOfDps 15 !NrOfHealers 6 !Role Tank

  if "!template" not in commands:

    # Check that each required command is in split message
    try: 
      NrOfPlayersIndex = commands.index("!nrofplayers")
      NrOfTanksIndex = commands.index("!nroftanks")
      NrOfDpsIndex = commands.index("!nrofdps")
      NrOfHealersIndex = commands.index("!nrofhealers")
    except ValueError:
      await DMHelper.DMUser(message, f"!nrofplayers, !nroftanks, !nrofdps, or nrofhealers, or !template is not found in your command.")
      return

    # Check a variable can be set a value for each command
    try:
      NrOfPlayers = int(commands[NrOfPlayersIndex + 1])
      if NrOfPlayers <= 0:
        await DMHelper.DMUser(message, f"!nrofplayers must be greater than 0.")
        return
      NrOfTanks = int(commands[NrOfTanksIndex + 1])
      NrOfDps = int(commands[NrOfDpsIndex + 1])
      NrOfHealers = int(commands[NrOfHealersIndex + 1])
    except ValueError:
      await DMHelper.DMUser(message, f"Please ensure that the value after !NrOfPlayers, !NrOfTanks, !NrOfDps, or NrOfHealers value is a valid number.")
      return
    except:
      await DMHelper.DMUser(message, f"Unable to assign variables, please specify values after your commands.")
      return

    # Check that number of players and roles are all above 0
    if any(x < 0 for x in [NrOfPlayers, NrOfTanks, NrOfDps, NrOfHealers]):
      await DMHelper.DMUser(message, f"Please ensure player and role values are equal to or greater than 0.")
      return

    #Ensure the number of players equals the sum of each role
    if NrOfPlayers != NrOfTanks + NrOfDps + NrOfHealers:
      await DMHelper.DMUser(message, f"Please ensure the total of each role equals the total number of players required.")
      return

    #Check that name is valid, first find first command after !Create
    MinIndexOfCommands = min(DateIndex, RoleIndex, NrOfPlayersIndex, NrOfTanksIndex, NrOfDpsIndex, NrOfHealersIndex)

    #check to ensure that there is a value after !Create that isn't another command
    if MinIndexOfCommands == 1:
      await DMHelper.DMUser(message, f"No valid name present after !create, please name your run after !create.")
      return
    
    # Set name to strings between !Create and next command
    try:
      Name = " ".join(commands[1:MinIndexOfCommands])
    except:
      await DMHelper.DMUser(message, f"Something went wrong setting the name of the run")
      return

  # 2 Create raid with template
  # 2.1 Example command !CreateRaid TestRaid !DateTime 01-08-2021 19:00 !Template Normal !Role Tank
  # Check message for all commands and split input into the following variables, RaidName, Origin, Creator, DateTime, TemplateName, Role
  else:
    TemplateIndex = commands.index("!template")
    Template = commands[TemplateIndex + 1]

    #Check that name is valid, first find first command after !Create
    MinIndexOfCommands = min(DateIndex, RoleIndex, TemplateIndex)

    #check to ensure that there is a value after !Create that isn't another command
    if MinIndexOfCommands == 1:
      await DMHelper.DMUser(message, f"No valid name found for your run, please provide a name for your run after !Create.")
      return

    # Set name to strings between !Create and next command
    try:
      Name = " ".join(commands[1:MinIndexOfCommands])
    except:
      await DMHelper.DMUser(message, f"Something went wrong trying to create the name of the run")
      return

    # Open connection to the database
    conn = sqlite3.connect('RaidPlanner.db')
    c = conn.cursor()

    # Find Template and store values into rows
    try:
      c.execute(f"SELECT NrOfPlayers, NrOfTanks, NrOfDps, NrOfHealers FROM Templates WHERE Name = (?)", (Template,))

      row = c.fetchone()
      
      if not row:
        await DMHelper.DMUser(message, f"I could not find the template {Template} on this server")
        conn.close()
        return
    except:
      await DMHelper.DMUser(message, f"Something went wrong checking for template")
      conn.close()
      return

    try:        
      NrOfPlayers = row[0]
      NrOfTanks = row[1]
      NrOfDps = row[2]
      NrOfHealers = row[3]
    except:
      await DMHelper.DMUser(message, f"Something went wrong obtaining the player and/or role numbers from the template.")
      conn.close()   
      return
  
  #check that user hasn't entered a role with no slots
  if NumberOfCurrentTanks > NrOfTanks or NumberOfCurrentHealers > NrOfHealers or NumberOfCurrentDps > NrOfDps:
      await DMHelper.DMUser(message, f"You have entered a role which has no available slots, please ensure correct number for !nrof(role) was used or template is correct for your requirements")
      return
  
  #Check if organizer is creating a run for themselves, set status to Formed if so
  if NrOfPlayers == 1:
    Status = "Formed"
  else:
    Status = "Forming"
  
  try:
    Creator = await UserHelper.GetUserID(message)
  except:
    await DMHelper.DMUser(message, f"Something went wrong obtaining your user ID")
    return
  
  try:
    CreatorDisplay = await UserHelper.GetDisplayName(message, Creator, bot)
  except:
    await DMHelper.DMUser(message, f"Something went wrong obtaining the users' nickname on the server")
    return

  if not Origin or not Creator:
    await DMHelper.DMUser(message, f"Error obtaining Discord IDs.")
    return

  # Open connection to the database
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  # 2.3 Check if there's already a raid with the same origin + name
  try:
    c.execute(f"SELECT Name FROM Raids WHERE Origin = (?) and Name = (?) and Date = (?)", (Origin, Name, sqldatetime))

    row = c.fetchone()
  except:
    conn.close()
    return

  if row:
    await DMHelper.DMUser(message, "There is already a raid of the same description and time as your !create request, if making a party for the same event, please add \"Party 2\" for example")
    conn.close()
    return

  # 2.4 Create query to insert raid into database
  try:
    c.execute(f"INSERT INTO Raids (Name, Origin, Date, OrganizerUserID, NrOfPlayersRequired, NrOfPlayersSignedUp, NrOfTanksRequired, NrOfTanksSignedUp, NrOfDpsRequired, NrOfDpsSignedUp, NrOfHealersRequired, NrOfHealersSignedUp, Status, ChannelID) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (Name, Origin, sqldatetime, Creator, NrOfPlayers, 1, NrOfTanks, NumberOfCurrentTanks, NrOfDps, NumberOfCurrentDps, NrOfHealers, NumberOfCurrentHealers, Status, ChannelID))
  except:
    await DMHelper.DMUser(message, f"Something went wrong trying to create the run.")
    conn.close()
    return

  # Saving unique Raid ID to insert into next table
  RaidID = c.lastrowid

  #Create joining data for raid members with join on Raid ID
  try:
    c.execute(f"INSERT INTO RaidMembers (Origin, UserID, RaidID, RoleID) VALUES (?, ?, ?, ?)", (Origin, Creator, RaidID, RoleID))
  except:
    await DMHelper.DMUser(message, "Something went wrong trying to add you as a member to this run.")
    conn.close()
    return

  # Get role icons
  try:
    TankIcon = await RoleIconHelper.GetTankIcon(bot, 'Tank')
    DpsIcon = await RoleIconHelper.GetDpsIcon(bot, 'Dps')
    HealerIcon = await RoleIconHelper.GetHealerIcon(bot, 'Healer')
  except:
    await DMHelper.DMUser(message, f"Something went wrong retrieving role icons")
    conn.close()
    return

  # 3 Post message to channel saying the raid is being formed
  try:
    conn.commit()
    message = await message.channel.send(f"**Run:** {RaidID}\n**Description:** {Name}\n**Organizer:** {CreatorDisplay}\n**Date (UTC):** {DateTime}\n**Status:** {Status}\n{TankIcon} {NumberOfCurrentTanks}\/{NrOfTanks} {DpsIcon} {NumberOfCurrentDps}\/{NrOfDps} {HealerIcon} {NumberOfCurrentHealers}\/{NrOfHealers}",components=[[Button(style=ButtonStyle.blue, label="Tank", custom_id="tank_btn"),Button(style=ButtonStyle.red, label="DPS", custom_id="dps_btn"),Button(style=ButtonStyle.green, label="Healer", custom_id="healer_btn"),Button(style=ButtonStyle.grey, label="Rally", custom_id="rally_btn")],[Button(style=ButtonStyle.grey, label="Members", custom_id="members_btn"),Button(style=ButtonStyle.grey, label="Reschedule", custom_id="reschedule_btn"),Button(style=ButtonStyle.red, label="Cancel", custom_id="cancel_btn")]])
    conn.close()
     
  except:
    await DMHelper.DMUser(message, f"Something went wrong creating the run")    
    conn.close()
    
  return