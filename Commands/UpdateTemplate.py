import sqlite3
from Helpers import OriginHelper
from Helpers import DMHelper
from Helpers import UserHelper

async def UpdateTemplate(message, bot):
  commands = message.content.split()

  try:
    TemplateIndex = commands.index("!updatetemplate")
    NrOfPlayersIndex = commands.index("!nrofplayers")
    NrOfTanksIndex = commands.index("!nroftanks")
    NrOfDpsIndex = commands.index("!nrofdps")
    NrOfHealersIndex = commands.index("!nrofhealers")
  except ValueError:
    await DMHelper.DMUser(message, f"!nrofplayers, !nroftanks,!nrofdps or !nrofhealers not specified in your command.")
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
    await DMHelper.DMUser(message, f"Something went wrong assigning values, please make sure your template name doesn't contain spaces")
    return

  try:
    if NrOfTanks + NrOfDps + NrOfHealers == NrOfPlayers:
      conn = sqlite3.connect('RaidPlanner.db')
      c = conn.cursor()

      try:
        c.execute(f"SELECT ID FROM Templates WHERE Name = (?) AND CreatorUserID = (?) AND Origin = (?)", (TemplateName, CreatorID, Origin,))
        row = c.fetchone()

        if not row:
          await DMHelper.DMUser(message, f"Template not found or you're not the creator of this template please beware that only the creator of the template is allowed to update the template")
          conn.close()
          return
      except:
        await DMHelper.DMUser(message, f"Something went wrong checking if this template already exists")
        conn.close()
        return

      try:
        TemplateID = row[0]
        c.execute(f"Update Templates SET NrOfPlayers = (?), NrOfTanks = (?), NrOfDps = (?), NrOfHealers = (?) WHERE ID = (?)", (NrOfPlayers, NrOfTanks, NrOfDps, NrOfHealers, TemplateID,))
        
        try:
          conn.commit()
          conn.close()
          await message.channel.send(f"{CreatorDisplay} has updated the template {TemplateName}")
        except:
          await DMHelper.DMUser(message, f"Something went wrong updating the template")
          conn.close()
          return

      except:
        await DMHelper.DMUser(message, f"Something went wrong trying to add template")
        conn.close()
        return
    else:
      await DMHelper.DMUser(message, f"The total of tanks, dps and healers provided required doesn't match the provided total for the number of players")
      conn.close()
      return
  except:
    await DMHelper.DMUser(message, f"Something went wrong updating the template")
    conn.close()
    return