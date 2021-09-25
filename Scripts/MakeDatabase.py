import sqlite3
from Helpers import DMHelper

async def MakeDatabase(message):
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor() 

  #try:
  CREATE_RAIDS_TABLE = """CREATE TABLE IF NOT EXISTS Raids (
    ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    Name TEXT NOT NULL,
    Origin INTEGER CHECK (Origin >= 0) NOT NULL,
	ChannelID INTEGER CHECK (ChannelID >= 0) NOT NULL,
    Date TEXT NOT NULL,
    OrganizerUserID INTEGER CHECK (OrganizerUserID >= 0) NOT NULL,
    NrOfPlayersRequired INTEGER CHECK (NrOfPlayersRequired >= 1) NOT NULL,
    NrOfPlayersSignedUp INTEGER CHECK (NrOfPlayersSignedUp >= 0) NOT NULL,
    NrOfTanksRequired INTEGER CHECK (NrOfTanksRequired >= 0) NOT NULL,
    NrOfTanksSignedUp INTEGER CHECK (NrOfTanksSignedUp >= 0) NOT NULL DEFAULT 0, 
    NrOfDpsRequired INTEGER CHECK (NrOfDpsRequired >= 0) NOT NULL,
    NrOfDpsSignedUp INTEGER CHECK (NrOfDpsSignedUp >= 0) NOT NULL DEFAULT 0,
    NrOfHealersRequired INTEGER CHECK (NrOfHealersRequired >= 0) NOT NULL,
    NrOfHealersSignedUp INTEGER CHECK (NrOfHealersSignedUp >= 0) NOT NULL DEFAULT 0,
    Status TEXT CHECK( Status IN ('Forming','Formed','Cancelled')) NOT NULL DEFAULT 'Forming',
	RallyCount INTEGER CHECK (RallyCount >= 0) DEFAULT 0,
    UNIQUE (Name, Origin, Date)
  );"""

  c.execute(CREATE_RAIDS_TABLE)
  c.execute(f"CREATE INDEX idx_Raids ON Raids (Origin, Date, Name, Status, OrganizerUserID, RallyCount, ChannelID)")

  CREATE_ROLES_TABLE = """CREATE TABLE IF NOT EXISTS Roles (
    ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    Name TEXT NOT NULL,
    UNIQUE (Name)
  );"""

  c.execute(CREATE_ROLES_TABLE)
  c.execute(f"CREATE INDEX idx_Roles ON Roles (Name)")

  CREATE_RAIDMEMBERS_TABLE = """CREATE TABLE IF NOT EXISTS RaidMembers (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID INTEGER CHECK (UserID >= 0) NOT NULL,
    Origin INTEGER CHECK (Origin >= 0) NOT NULL,
    RaidID INTEGER NOT NULL,
    RoleID INTEGER NOT NULL,
    UNIQUE (UserID, Origin, RaidID),
    FOREIGN KEY(RoleID) REFERENCES Roles(ID),
    FOREIGN KEY(RaidID) REFERENCES Raids(ID) ON DELETE CASCADE
  );"""

  c.execute(CREATE_RAIDMEMBERS_TABLE)
  c.execute(f"CREATE INDEX idx_RaidMembers ON RaidMembers (Origin, RaidID, RoleID, UserID)")

  CREATE_TEMPLATES_TABLE = """CREATE TABLE IF NOT EXISTS Templates (
    ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    Name TEXT CHECK (Name NOT LIKE '% %') NOT NULL,
    Origin INTEGER CHECK (Origin >= 0) NOT NULL,
    CreatorUserID INTEGER CHECK (CreatorUserID >= 0),
    NrOfPlayers INTEGER CHECK (NrOfPlayers >= 1) NOT NULL,
    NrOfTanks INTEGER CHECK (NrOfTanks >= 0) NOT NULL,
    NrOfDps INTEGER CHECK (NrOfDps >= 0) NOT NULL,
    NrOfHealers INTEGER CHECK (NrOfHealers >= 0) NOT NULL,
    UNIQUE (Name, Origin)
  );"""

  c.execute(CREATE_TEMPLATES_TABLE)
  c.execute(f"CREATE INDEX idx_TemplateName ON Templates (Origin, Name, CreatorUserID)")
  c.execute(f"CREATE INDEX idx_NrOfPlayers ON Templates (NrOfPlayers, NrOfTanks, NrOfDps, NrOfHealers)")
    
  CREATE_TEAMS_TABLE = """CREATE TABLE IF NOT EXISTS Teams (
    ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    Name TEXT NOT NULL,
	Description TEXT NOT NULL,
    Origin INTEGER CHECK (Origin >= 0) NOT NULL,
	ChannelID INTEGER CHECK (ChannelID >= 0) NOT NULL,
    CreatorUserID INTEGER CHECK (CreatorUserID >= 0) NOT NULL,
	Recruiting INTEGER CHECK (Recruiting >= 0 AND Recruiting <=1),
	RecruitingTanks INTEGER CHECK (RecruitingTanks >= 0 AND RecruitingTanks <=1),
	RecruitingDps INTEGER CHECK (RecruitingDps >= 0 AND RecruitingDps <=1),
	RecruitingHealers INTEGER CHECK (RecruitingHealers >= 0 AND RecruitingHealers <=1),
    UNIQUE (Name, Origin)
  );"""
    
  c.execute(CREATE_TEAMS_TABLE )
  c.execute(f"CREATE INDEX idx_TeamName ON Teams (Origin, Name, CreatorUserID, ChannelID)")
  c.execute(f"CREATE INDEX idx_Recruiting ON Teams (Recruiting, RecruitingTanks, RecruitingDps, RecruitingHealers)")
	
  CREATE_TEAMMROLES_TABLE = """CREATE TABLE IF NOT EXISTS TeamRoles (
    ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    Name TEXT NOT NULL,
    Hierarchy INTEGER CHECK (Hierarchy >= 0) NOT NULL
  );"""
    
  c.execute(CREATE_TEAMMROLES_TABLE )
  c.execute(f"CREATE INDEX idx_TeamRoles ON TeamRoles (Name, Hierarchy)")
	
  CREATE_TEAMMROLEPERMISSIONS_TABLE = """CREATE TABLE IF NOT EXISTS TeamRolePermissions (
    ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    TeamRoleID INTEGER CHECK (TeamRoleID >= 0) NOT NULL,
    AddMembers INTEGER CHECK (AddMembers = 0 or AddMembers = 1) NOT NULL,
	RemoveMembers INTEGER CHECK (RemoveMembers = 0 or RemoveMembers = 1) NOT NULL,
	ViewApplications INTEGER CHECK (ViewApplications = 0 or ViewApplications = 1) NOT NULL,
	AcceptApplications INTEGER CHECK (AcceptApplications = 0 or AcceptApplications = 1) NOT NULL,
	RejectApplications INTEGER CHECK (RejectApplications = 0 or RejectApplications = 1) NOT NULL,
	PromoteMembers INTEGER CHECK (PromoteMembers = 0 or PromoteMembers = 1) NOT NULL,
	DemoteMembers INTEGER CHECK (DemoteMembers = 0 or DemoteMembers = 1) NOT NULL,
	UpdateTeamInfo INTEGER CHECK (UpdateTeamInfo = 0 or UpdateTeamInfo = 1) NOT NULL,
	FOREIGN KEY(TeamRoleID) REFERENCES TeamRoles(ID)
  );"""
    
  c.execute(CREATE_TEAMMROLEPERMISSIONS_TABLE )
  c.execute(f"CREATE INDEX idx_TeamRolePermissions ON TeamRolePermissions (TeamRoleID, AddMembers, RemoveMembers, ViewApplications, AcceptApplications, RejectApplications, PromoteMembers, DemoteMembers, UpdateTeamInfo)")
    
  CREATE_TEAMMEMBERS_TABLE = """CREATE TABLE IF NOT EXISTS TeamMembers (
    ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    TeamID INTEGER CHECK (TeamID >= 0) NOT NULL,
    Origin INTEGER CHECK (Origin >= 0) NOT NULL,
    UserID INTEGER CHECK (UserID >= 0) NOT NULL,
    RoleID INTEGER CHECK (RoleID >= 0) NOT NULL,
	TeamRoleID INTEGER CHECK (TeamRoleID >= 0) NOT NULL,
    UNIQUE (TeamID, Origin, UserID),
    FOREIGN KEY(TeamID) REFERENCES Teams(ID),
    FOREIGN KEY(RoleID) REFERENCES Roles(ID),
	FOREIGN KEY(TeamRoleID) REFERENCES TeamRoles(ID)
  );"""
    
  c.execute(CREATE_TEAMMEMBERS_TABLE )
  c.execute(f"CREATE INDEX idx_TeamMember ON TeamMembers (Origin, TeamID, UserID, TeamRoleID)")
	
  CREATE_TEAMAPPLICATIONS_TABLE = """CREATE TABLE IF NOT EXISTS TeamApplications (
    ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    TeamID INTEGER CHECK (TeamID >= 0) NOT NULL,
    Origin INTEGER CHECK (Origin >= 0) NOT NULL,
    Description TEXT NOT NULL,
    RoleID INTEGER CHECK (RoleID >= 0) NOT NULL,
	UserID INTEGER CHECK (UserID >= 0) NOT NULL,      
	Status TEXT CHECK( Status IN ('Open','Accepted','Rejected')) NOT NULL DEFAULT 'Open',
	UNIQUE (TeamID, Origin, UserID),
    FOREIGN KEY(TeamID) REFERENCES Teams(ID),
    FOREIGN KEY(RoleID) REFERENCES Roles(ID)
  );"""
    
  c.execute(CREATE_TEAMAPPLICATIONS_TABLE )
  c.execute(f"CREATE INDEX idx_TeamApplications ON TeamApplications (Origin, TeamID, UserID, RoleID)")

  conn.commit()
  conn.close()
  await message.channel.send(f"Database succesfully created")
  return
  #except:
    #await message.channel.send(f"Something went wrong trying to create the database")
    #conn.close()
    #return