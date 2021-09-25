import sqlite3
from Helpers import DMHelper

async def InsertMasterData(message):
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  try:
    c.execute("INSERT INTO Roles VALUES (1, 'tank')")
    c.execute("INSERT INTO Roles VALUES (2, 'dps')")
    c.execute("INSERT INTO Roles VALUES (3, 'healer')")
    
    c.execute("INSERT INTO TeamRoles VALUES (1, 'Leader', 1)")
    c.execute("INSERT INTO TeamRoles VALUES (2, 'Officer', 2)")
    c.execute("INSERT INTO TeamRoles VALUES (3, 'Member', 3)")
    
    c.execute("INSERT INTO TeamRolePermissions VALUES (1, 1, 1, 1, 1, 1, 1, 1, 1, 1)")
    c.execute("INSERT INTO TeamRolePermissions VALUES (2, 2, 1, 1, 1, 1, 1, 0, 0, 0)")
    c.execute("INSERT INTO TeamRolePermissions VALUES (3, 0, 0, 0, 0, 0, 0, 0, 0, 0)")

    conn.commit()
    conn.close()
    await DMHelper.DMUser(message, "Masterdata succesfully added")
    return
  except:
    await DMHelper.DMUser(message, "Something went wrong trying to insert masterdata")
    conn.close()
    return