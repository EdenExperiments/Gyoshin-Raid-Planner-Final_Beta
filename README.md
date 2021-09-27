# Gyoshin-Raid-Planner-Final_Beta
Final Beta code before minor edits. Added to show progress from Initial Beta code. 

Disclaimer: Gyoshin was project managed by Martijin Bos, not myself. I would like to thank Martijin for inviting me to their project and giving me a chance to gain some experience on a more complex real life project. I would also like to thank them for teaching me about the database side of the project. Initial versions of commands i created up to BETA release were mostly programmed myself (with a few UI edits by Martijin), with Martijin pushing me to use resources and other commands for guidance when stuck but not outright giving me answers, and also giving guidance on how to refactor code to look more polished and handle errors better once code was functional.

My main contributions to this are general help in design, commands such as !addrun, !create, and code for cancelling, joining or using rally for a party was largely developed by myself. Secondly, the main issue resolved by myself was figuring out how to collect data from a DM response and creating the helper function for this. alongside this, I have assisted with general debugging, taking bugs recorded on confluence and updating tables when complete and tested. 

Gyoshin is a Discord Bot, initially created to help my Final Fantasy XIV server have a simple and functional way of planning raid parties. Using Python and additional libraries/APIs such as Discord, datetime, re and sqlite3, Gyoshin allows users to create, and manage parties on a discord server. By saving the party to a database with references to the server channel ID, it allows several servers to use at once without picking up all the raids. 

Users can join raids, by choosing specific roles, withdraw from raids, cancel raids if they are the organiser, and rally the users within one hour of the set datetime of the event.


- Link will be here once Gyoshin is out of beta

## Current Commands
Basic commands:
!addrun, used to start a conversation with the bot that will guide you through the process to create a run

!adddefaulttemplates, used to add some default templates for FFXIV example use: !adddefaulttemplates

!commands, lists all supported commands example use: !commands

!dismiss, used to remove a member from the run example use: !dismiss 2 (this is the number you see after Run:) @UserName (you can just tag the user you want to dismiss, only the 
organizer of the run is allowed to dismiss members)

!myruns, show upcoming runs you've signed up for up to a maximum of 5 example use: !myruns

!roles, lists all available roles example use: !roles

!runs, used to retrieve all runs planned on a specific date example use: !runs 01-08-2021

!templates, lists all available templates that can be used to create a run with example use: !templates

Advanced commands:

!create, used to create a run example use without template (for if you don't want to go through a conversation with the bot):

!create TestRaid !date 01-08-2021 19:00 !nrofplayers 24 !nroftanks 3 !nrofdps 15 !nrofhealers 6 !role tank
Example use with template:
!create TestRaid !date 01-08-2021 19:00 !template raid !role tank

!addtemplate, used to create a custom template example use: !addtemplate TestTemplate !nrofplayers 8 !nroftanks 2 !nrofdps 4 !nrofhealers 2

!updatetemplate, used to update an existing template example use: !updatetemplate TestTemplate !nrofplayers 8 !nroftanks 2 !nrofdps 4 !nrofhealers 2 (only the creator of the template is allowed to update)

!deletetemplate, used to delete a template example use: !deletetemplate TestTemplate (only the creator of the template is allowed to delete)

Button explanations:

Role (Tank/DPS/Healer) buttons, if you're not part of a run clicking one of the role buttons will add you to that run on that role

If you're already part of the run and you click on the same role button as the role you've signed up with you'll be given the option to withdraw from the run

If you're already part of the run and you click on another role button then the role you've signed up with you'll be given the option to change your role for the run
Rally button, you can use this button to tag all members that are signed up to this specific run (this will only work from 1 hour before the start time of the run up until the start time and can only be executed by players who are also signed up to this run up to a maximum amount of 3 times)

Reschedule button, gives the organizer of the run the option to reschedule the run to another date (upon rescheduling all members besides the organizer will be removed from the run)

Cancel button, gives the organizer of the run the option to cancel the run

## Developer RoadMap:

Complete final edits to bot based on requests from beta server.
Improve responsiveness, currently being done by changing from emojies to Discord buttons.
Add teams function, allowing team leaders for larger raid content.

### not all files are on github, such as packages, just main programmed files for reference

