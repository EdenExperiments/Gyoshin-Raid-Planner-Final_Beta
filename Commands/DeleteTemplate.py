import sqlite3
from Helpers import OriginHelper
from Helpers import DMHelper
from Helpers import UserHelper

async def DeleteTemplate(message, bot):
  commands = message.content.split()
  TemplateIndex = commands.index("!deletetemplate")

  try:
    TemplateName = commands[TemplateIndex + 1]
    Origin = await OriginHelper.GetOrigin(message)
    CreatorID = message.author.id
    CreatorDisplay = await UserHelper.GetDisplayName(message, CreatorID, bot)
  except:
    await DMHelper.DMUser(message, f"Something went wrong assigning values, please make sure your template name doesn't contain any spaces")
    return

  try:
    conn = sqlite3.connect('RaidPlanner.db')
    c = conn.cursor()

    c.execute(f"SELECT ID FROM Templates WHERE Name = (?) AND CreatorUserID = (?) AND Origin = (?)", (TemplateName, CreatorID, Origin,))
    row = c.fetchone()

    if not row:
      await DMHelper.DMUser(message, f"Template not found or you're not the creator of this template, please beware that only the creator of the template is allowed to update the template")
      conn.close()
      return
  except:
      await DMHelper.DMUser(message, f"Something went wrong checking if this template already exists")
      conn.close()
      return

  try:
    TemplateID = row[0]
    c.execute(f"DELETE FROM Templates WHERE ID = (?)", (TemplateID,))
    
    try:
      conn.commit()
      await message.channel.send(f"{CreatorDisplay} has deleted the template {TemplateName} from the server")
      conn.close()
    except:
      await DMHelper.DMUser(message, f"Something went wrong deleting the template")
      conn.close()
      return
  except:
    await DMHelper.DMUser(message, f"Something went wrong trying to delete the template")
    conn.close()
    return