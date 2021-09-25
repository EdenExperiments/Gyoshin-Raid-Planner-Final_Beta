import sqlite3
from Helpers import OriginHelper
from Helpers import DMHelper
from Helpers import UserHelper

async def AddTemplate(message, bot):
  commands = message.content.split()

  try:
    TemplateIndex = commands.index("!addtemplate")
    NrOfPlayersIndex = commands.index("!nrofplayers")
    NrOfTanksIndex = commands.index("!nroftanks")
    NrOfDpsIndex = commands.index("!nrofdps")
    NrOfHealersIndex = commands.index("!nrofhealers")
  except ValueError:
    await DMHelper.DMUser(message, "!nrofplayers, !nroftanks, !nrofdps or !nrofhealers is not specified in your command.")
    return

  try:
    TemplateName = commands[TemplateIndex + 1]
    Origin = await OriginHelper.GetOrigin(message)
    CreatorID = message.author.id
    CreatorDisplay = await UserHelper.GetDisplayName(message, CreatorID, bot)
    NrOfPlayers = int(commands[NrOfPlayersIndex + 1])
    NrOfTanks = int(commands[NrOfTanksIndex + 1])
    NrOfDps = int(commands[NrOfDpsIndex + 1])
    NrOfHealers = int(commands[NrOfHealersIndex + 1])
  except:
    await DMHelper.DMUser(message, "Something went wrong assigning values, please make sure your template name doesn't contain spaces")
    return

  if NrOfPlayers <= 0:
    await DMHelper.DMUser(message, "Please ensure the !nrofplayers value is greater than 0 when adding a template.")
    return

  try:
    if NrOfTanks + NrOfDps + NrOfHealers == NrOfPlayers:
      conn = sqlite3.connect('RaidPlanner.db')
      c = conn.cursor()

      try:
        c.execute(f"SELECT ID FROM Templates WHERE Name = (?) AND CreatorUserID = (?) AND Origin = (?)", (TemplateName, CreatorID, Origin,))
        row = c.fetchone()

        if row:
          await DMHelper.DMUser(message, f"This template already exists")
          conn.close()
          return
      except:
        await DMHelper.DMUser(message, f"Something went wrong checking if this template already exists")
        conn.close()
        return

      try:
        c.execute(f"INSERT INTO Templates (Name, Origin, CreatorUserID, NrOfPlayers, NrOfTanks, NrOfDps, NrOfHealers) VALUES (?, ?, ?, ?, ?, ?, ?)", (TemplateName, Origin, CreatorID, NrOfPlayers, NrOfTanks, NrOfDps, NrOfHealers))
        conn.commit()
        await message.channel.send(f"{CreatorDisplay} has added the template {TemplateName} to the server.")
        conn.close()
      except:
        await DMHelper.DMUser(message, f"Something went wrong trying to add template")
        conn.close()
        return

  except:
    await DMHelper.DMUser(message, f"The total of tanks, dps and healers provided required doesn't match the provided total for the number of players")
    return