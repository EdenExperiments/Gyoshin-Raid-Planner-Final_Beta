import re
import sqlite3
import asyncio
from discord import ChannelType
from Helpers import RoleHelper
from Helpers import UserHelper
from Helpers import NotificationHelper
from Helpers import OriginHelper
from Helpers import DMHelper
from Helpers import RaidIDHelper
from Helpers import MessageHelper
from Commands import Withdraw
from Commands import ChangeRole

async def JoinRaid(message, bot, RoleName, UserID):
  try:
    RaidID = await RaidIDHelper.GetRaidIDFromMessage(message)
  except ValueError:
    await DMHelper.DMUserByID(bot, UserID, f"Something went wrong.")
    return

  # Role verification
  try:     
    RoleID = await RoleHelper.GetRoleID(RoleName)
  except:
    await DMHelper.DMUserByID(bot, UserID, f"Invalid role, please enter a valid role, you can call !roles to see available roles.")
    return

  # Obtain origin and userID, for inputs to database
  Origin = await OriginHelper.GetOrigin(message)
  GuildName = await OriginHelper.GetName(message)

  if not Origin or not UserID:
    await DMHelper.DMUserByID(bot, UserID, f"Something went wrong resolving the user or server ID.")
    return

  # Open database connection
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  #Collect required information from raid, number of players and roles, and if already formed or cancelled. 
  try:
    c.execute(f"SELECT ID, Name, Date, Origin, OrganizerUserID, NrOfPlayersRequired, NrOfPlayersSignedUp, NrOfTanksRequired, NrOfTanksSignedUp, NrOfDpsRequired, NrOfDpsSignedUp, NrOfHealersRequired, NrOfHealersSignedUp, Status FROM Raids WHERE ID = (?) AND Origin = (?)", (RaidID, Origin,))
  except:
    await DMHelper.DMUserByID(bot, UserID, f"Something went wrong when searching for this run.")
    conn.close()
    return

  try:
    row = c.fetchone()
  except:
    await DMHelper.DMUserByID(bot, UserID, f"I was not able to find run {RaidID}.")
    conn.close()
    return

  try:
    RaidID = row[0]
    Description = row[1]
    Date = row[2]
    SplitDate = Date.split(' ')
    Date = SplitDate[0]
    Time = SplitDate[1]

    # Split date into day, month and year values
    splitdate = Date.split('-')
    day = splitdate[2]
    month = splitdate[1]
    year = splitdate[0]
    
    LocalDate = f"{day}-{month}-{year} {Time}"
    Origin = row[3]
    Organizer = row[4]
    NrOfPlayersRequired = row[5]
    NrOfPlayersSignedUp = row[6]
    NrOfTanksRequired = row[7]
    NrOfTanksSignedUp = row[8]
    NrOfDpsRequired = row[9]
    NrOfDpsSignedUp = row[10]
    NrOfHealersRequired = row[11]
    NrOfHealersSignedUp = row[12]  
    Status = row[13]
  except:
    await DMHelper.DMUserByID(bot, UserID, f"Something went wrong retrieving run information.")
    conn.close()
    return

  if Status == "Cancelled":
    await DMHelper.DMUserByID(bot, UserID, f"This run does not have the status 'Forming', please ensure that you're not joining an already cancelled run.")
    conn.close()
    return

  # Ensure that the user is not trying to join a raid they have already joined
  c.execute(f"SELECT ID, RoleID FROM RaidMembers WHERE RaidID = (?) and UserID = (?)", (RaidID, UserID))

  usercheck = c.fetchone()
  
  # Checks for waiting for dm replies
  def DMCheck(dm_message):
    return (dm_message.channel.type == ChannelType.private and dm_message.author.id == UserID)
    
  if usercheck:
    try:
      RoleIDSignedUpAs = usercheck[1]
      RoleNameSignedUpAs = await RoleHelper.GetRoleName(RoleIDSignedUpAs)
    except:
      await DMHelper.DMUserByID(bot, UserID, f"Something went wrong obtaining role information")
      conn.close()
      return
    
    # Offer to withdraw if user is signed up as this role
    if RoleID == RoleIDSignedUpAs:
      CanWithdraw = None
      while not CanWithdraw:
        await DMHelper.DMUserByID(bot, UserID, f"You have already joined the run {Description} on {LocalDate} in the {GuildName} server as a {RoleNameSignedUpAs}, would you like to withdraw from this run (Y/N)?")
        try:
          withdrawresponse = await bot.wait_for(event='message' ,timeout = 30, check= DMCheck)
          if withdrawresponse.content == "Y" or withdrawresponse.content == "y" or withdrawresponse.content == "Yes" or withdrawresponse.content == "yes":
            CanWithdraw = "yes"
          elif withdrawresponse.content == "N" or withdrawresponse.content == "n" or withdrawresponse.content == "No" or withdrawresponse.content == "no":
            CanWithdraw = "no"
          else:
            await DMHelper.DMUserByID(bot, UserID, f"Invalid answer detected, please respond with yes or no.")
            continue
        except asyncio.TimeoutError:
          conn.close()
          await DMHelper.DMUserByID(bot, UserID, f"Your request has timed out, please click the button again if you still wish to withdraw from the run.")
          return
    
      if CanWithdraw == "yes":
        await Withdraw.WithdrawFromRaid(message, bot, UserID)
        conn.close()
        return
      elif CanWithdraw == "no":
        conn.close()
        return
      
    # Offer to change role if user is signed up with another role
    elif RoleID != RoleIDSignedUpAs:
      CanChangeRole = None
      while not CanChangeRole:
        await DMHelper.DMUserByID(bot, UserID, f"You have already joined the run {Description} on {LocalDate} in the {GuildName} server as a {RoleNameSignedUpAs}, would you like to change to {RoleName} for this run (Y/N)?")
        try:
          changeroleresponse = await bot.wait_for(event='message' ,timeout = 30, check= DMCheck)
          if changeroleresponse.content == "Y" or changeroleresponse.content == "y" or changeroleresponse.content == "Yes" or changeroleresponse.content == "yes":
            CanChangeRole = "yes"
          elif changeroleresponse.content == "N" or changeroleresponse.content == "n" or changeroleresponse.content == "No" or changeroleresponse.content == "no":
            CanChangeRole = "no"
          else:
            await DMHelper.DMUserByID(bot, UserID, f"Invalid answer detected, please respond with yes or no.")
            continue
        except asyncio.TimeoutError:
          conn.close()
          await DMHelper.DMUserByID(bot, UserID, f"Your request has timed out, please click the button again if you still wish to change your role for this run.")
          return
      
      if CanChangeRole == "yes":
        await ChangeRole.ChangeRole(message, bot, RoleName, UserID)
        conn.close()
        return
      elif CanChangeRole == "no":
        conn.close()
        return

  if not usercheck:
    # Update Raids table based on role retrieved
    if RoleName == 'tank':
      if NrOfTanksSignedUp == NrOfTanksRequired:
        await DMHelper.DMUserByID(bot, UserID, f"This run already has the required number of tanks, please join with a different role.")
        conn.close()
        return
      else:
        try:        
          c.execute(f"Update Raids SET NrOfPlayersSignedUp = NrOfPlayersSignedUp + 1, NrOfTanksSignedUp = NrOfTanksSignedUp + 1 WHERE ID = (?) AND Origin = (?)", (RaidID, Origin,))
        except:
          await DMHelper.DMUserByID(bot, UserID, f"Something went wrong updating the number of signed up players and tanks")
          conn.close()
          return
    elif RoleName == 'dps':
      if NrOfDpsSignedUp == NrOfDpsRequired:
        await DMHelper.DMUserByID(bot, UserID, f"This run already has the required number of dps, please join with a different role.")
        conn.close()
        return
      else:
        try:
          c.execute(f"Update Raids SET NrOfPlayersSignedUp = NrOfPlayersSignedUp + 1, NrOfDpsSignedUp = NrOfDpsSignedUp + 1 WHERE ID = (?) AND Origin = (?)", (RaidID, Origin,))
        except:
          await DMHelper.DMUserByID(bot, UserID, f"Something went wrong updating the number of signed up players and dps")
          conn.close()
          return
    elif RoleName == 'healer':
      if NrOfHealersSignedUp == NrOfHealersRequired:
        await DMHelper.DMUserByID(bot, UserID, f"This run already has the required number of healers, please join with a different role.")
        conn.close()
        return
      else:
        try:
          c.execute(f"Update Raids SET NrOfPlayersSignedUp = NrOfPlayersSignedUp + 1, NrOfHealersSignedUp = NrOfHealersSignedUp + 1 WHERE ID = (?) AND Origin = (?)", (RaidID, Origin,))
        except:
          await DMHelper.DMUserByID(bot, UserID, f"Something went wrong updating the number of signed up players and healers")
          conn.close()
          return
    else:
      await DMHelper.DMUserByID(bot, UserID, f"Something went wrong trying to retrieve the role")
      conn.close()
      return

    # Insert user into raid members for raidID
    try:
      c.execute(f"INSERT INTO RaidMembers (Origin, UserID, RaidID, RoleID) VALUES (?, ?, ?, ?)", (Origin, UserID, RaidID, RoleID))
      conn.commit()

      JoinedUserDisplayName = await UserHelper.GetDisplayName(message, UserID, bot)
      await message.channel.send(f"{JoinedUserDisplayName} has joined the party {Description} on {LocalDate} as a {RoleName}!")
      UpdatedMessage = await MessageHelper.UpdateRaidInfoMessage(message, bot, UserID, Origin)
      await message.edit(content=UpdatedMessage)
    except:
      await DMHelper.DMUserByID(bot, UserID, f"Something went wrong joining you to this run.")
      conn.close()

    # Check if party is now full and can be set to "Formed"
    try:
      c.execute(f"SELECT NrOfPlayersRequired, NrOfPlayersSignedUp FROM Raids  WHERE ID = (?) AND Origin = (?)", (RaidID, Origin,))
      row = c.fetchone()
      
      if row:
        NrOfPlayersRequired = row[0]
        NrOfPlayersSignedUp = row[1]
        
      if NrOfPlayersRequired == NrOfPlayersSignedUp:
        try:  
          c.execute(f"UPDATE Raids SET Status = 'Formed' WHERE ID = (?) and Origin = (?)", (RaidID, Origin))
          try:
            conn.commit()
            conn.close()
            UpdatedMessage = await MessageHelper.UpdateRaidInfoMessage(message, bot, UserID, Origin)
            await message.edit(content=UpdatedMessage)
            NotifyOrganizerMessage = await NotificationHelper.NotifyUser(message, Organizer)
            await message.channel.send(f"{NotifyOrganizerMessage}\nYour crew for {Description} on {LocalDate} has been assembled!")
          except:
            await DMHelper.DMUserByID(bot, UserID, f"Something went wrong joining you to this run.")
            conn.close()
            return
        except:
          await DMHelper.DMUserByID(bot, UserID, f"Something went wrong updating party status to formed.")
          conn.close()
          return
    except:
      await DMHelper.DMUserByID(bot, UserID, f"Something went wrong updating the number of signed up players and dps")
      conn.close()
      return