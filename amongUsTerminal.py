# @author Caleb Remocaldo, 2046
# @creativeLead Kennis Dye, 2069
# This program accepts user input regarding the names of the player roster TXT file and the list of
#   D^2's to be done and randomly assigns each player a task, then writes that data into a new TXT
#   file called "Shuffled D Squareds.txt".  Finally, each player is emailed their tasks and whether
#   or not they are an impsoter

import math, ssl, smtplib, random
from credentials import EMAIL, PASSWORD

class Player:
    def __init__(self, name, email, playing):
        self.name = name
        self.email = email
        self.playing = playing
        self.playerStatus = ''
        self.tasks = []

    def determineStatus(self, imposters):
        if int(self.playing) == 0:
            return 'Not playing'
       
        if self.name in imposters:
            return 'Imposter'
        else:
            return 'Crewmate'

# Retrieve the list of players
def getPlayers(fileName):
    players = []
   
    with open(fileName, 'r') as roster:
        allData = roster.readlines()[1:]

        for player in allData:
            if not player.isspace():
                players.append(Player(player.split(',')[0] + ' ' + player.split(',')[1], player.split(',')[2], player.split(',')[3][:-1]))

    return players

# Retrieve the list of tasks to be done
def getTasks(fileName):
    tasks = []
   
    with open(fileName, 'r') as taskFile:
        allData = taskFile.readlines()

        for line in allData:
            task = line.split(',')
            playersNeeded = task[1][:-1]
            tasks.append([task[0], playersNeeded])

    return tasks

# Shuffle the tasks and tie each one to a player
def shuffleTasks(players, taskList):
    TASKCOUNT = math.ceil(len(taskList)/len(players))

    for player in players:
        copyTask = taskList.copy()

        for i in range(TASKCOUNT):
            player.tasks.append(copyTask.pop(random.randint(0, len(copyTask)-1))[0])

# Write the newly assigned tasks to a new TXT file
def writeTasks(participants):
    with open('Shuffled Tasks.txt', 'w', newline = '') as finalTask:
        for person in participants:
            finalTask.write(person.name + ': ')
           
            for task in person.tasks:
                finalTask.write(task + ', ')
               
            finalTask.write('\n')

# This is necessary in case there are people doing tasks but not
#   participating in Among Us
def cleanNonPlayers(players):
    playing = []
   
    for player in players:
        if int(player.playing) == 1:
            playing.append(player)

    return playing

# Self-explanatory
def selectImposters(players, imposterCount):
    imposters = []

    try:
        for i in range(int(imposterCount)):
            imposters.append(random.choice(players).name)
    except IndexError:
        print('IndexError: there are no players to select imposters from')

    return imposters

def sendEmail(players, imposters):
    port = 465  # For SSL

    imposterString = ''
    for i in range(len(imposters) - 1):
        imposterString = imposterString + imposters[i] + ', '

    imposterString = imposterString + imposters[len(imposters)-1]
   
    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(EMAIL, PASSWORD)

        for player in players:
            message = """\
Subject: Among Us Tasks


Player {0},
\tHere are your tasks for tonight's game.  You are a crewmate.

TASKS: {1}.

Godspeed
""".format(player.name, player.tasks).encode('ascii', 'ignore')
           
            if player.name in imposters:
                message = """\
Subject: Among Us Tasks


Player {0},
\tHere are your tasks for tonight's game.  You are an imposter.  The imposters are {1}.

TASKS: {2}.

Godspeed
""".format(player.name, imposterString, player.tasks).encode('ascii', 'ignore')
            elif int(player.playing) == 0:
                message = """\
Subject: Work Session Tasks


{0},
\tHere are your tasks for tonight's work session.

TASKS: {1}.
""".format(player.name, player.tasks).encode('ascii', 'ignore')

    
            server.sendmail(EMAIL, player.email, message)
            print('Tasks and role successfully sent to ' +  player.name + ' (' + player.email + ')')

def main():
    print('This program will randomize tasks for weekly work sessions and email players those tasks.')
    print('The .txt files of tasks and player names must be in the same folder as this program.')
    print('If you run into a problem, either fix it yourself or contact me at cremocal@purdue.edu')
    print('======================================================================================\n')

    # Input values

    roster = input("Enter name of player's .txt file: ")
    tasks = input("Enter name of task .txt file: ")
    imposterCount = input("How many imposters this round? ")

    # For debugging
    #roster = 'temp.txt'
    #tasks = 'tasks.txt'
    #imposterCount = 1

    # Collect list of players and tasks to be done
    participants = getPlayers(roster)
    taskList = getTasks(tasks)

    # Shuffle tasks and randomly assign them to players
    shuffleTasks(participants, taskList)

    # Separate those playing from those just doing tasks
    players = cleanNonPlayers(participants)
   
    # Select the imposters
    imposters = selectImposters(players, imposterCount)

    # Write the tasks to a TXT file, then send the email to each player
    writeTasks(participants)
    #sendEmail(players, imposters)

   
    # Send players and their tasks, along with playing status, to standard output
    print('\n{0} \t\t\t\t {1} \t\t\t\t\t      {2}'.format('PLAYER', 'TASKS', 'PLAYER STATUS'))
    print('='*100)

    for player in participants:
        player.playerStatus = player.determineStatus(imposters)
       
        print('{0}\t\t\t\t\t\t\t\t\t{1}'.format(player.name.title(), player.playerStatus))

        for task in player.tasks:
            print(f'\t\t\t\t{task:^20}')
       
    print('\nTasks have been shuffled and written to a new file.  So live!\n')
   

main()
