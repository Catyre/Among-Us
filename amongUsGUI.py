# @author Caleb Remocaldo, 2046
# @creativeLead Kennis Dye, 2069
# This program accepts user input regarding the names of the player roster TXT file and the list of
#   D^2's to be done and randomly assigns each player a task, then writes that data into a new TXT
#   file called "Shuffled D Squareds.txt".  Finally, each player is emailed their tasks and whether
#   or not they are an impsoter
###################################################################################################
# TODO: Clear and rewrite player list if new .txt file is entered
#       Add entry for adding new player names/tasks
#       Fix layout
#       Make task list scroll horizontally (or increase window size)
#       Make player and task frames larger
#       Display a player's tasks if their name is clicked on
# test

import math
import ssl
import smtplib
import random
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from credentials import EMAIL, PASSWORD

class Player:
    """Class for players in the game."""
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


class ScrollableFrame(Frame):
    """Class to make a scrollable frame for the player and task boxes."""
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = Canvas(self)
        scrollbar = Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = Frame(canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


class TextEditor:
    def __init__(self, root):
        pass


class AmongUsGUI:
    """Class to define GUI states."""
    def __init__(self, root):
        # Create a frame for the player file explorer:
        self.playerExplorerFrame = Frame(root)
        self.playerExplorerFrame.grid(column = 0, row = 0)

        # Create label for File Explorer for finding player file
        self.labelPlayerExplorer = Label(self.playerExplorerFrame, text = 'Select Player File: ')
        self.labelPlayerExplorer.grid(column = 0, row = 0)

        # Create a button for the player file explorer.  Executes playerFileExplorer
        self.buttonPlayer = Button(self.playerExplorerFrame, text = 'Browse Files', command = self.playerFileExplorer)
        self.buttonPlayer.grid(column = 1, row = 0)

        # Create a frame for the task file explorer
        self.taskExplorerFrame = Frame(root)
        self.taskExplorerFrame.grid(column = 0, row = 1)

        # Create label for file explorer for finding task file
        self.labelTaskExplorer = Label(self.taskExplorerFrame, text = 'Select Task File: ')
        self.labelTaskExplorer.grid(column = 0, row = 0)

        # Create a button for the task file explorer.  Executes taskFileExplorer
        self.buttonTask = Button(self.taskExplorerFrame, text = 'Browse Files', command = self.taskFileExplorer)
        self.buttonTask.grid(column = 1, row = 0)

        # Create combo box (and its label) to select the amount of imposters.
        #   Max imposters 5
        self.imposterFrame = Frame(root)
        self.imposterFrame.grid(column = 0, row = 2)
        self.imposterCountList = ['1', '2', '3', '4', '5']
        self.imposterLabel = Label(self.imposterFrame, text = 'How many imposters?')
        self.imposterLabel.grid(column = 0, row = 0)
        self.imposterCombo = ttk.Combobox(self.imposterFrame, values = self.imposterCountList)
        self.imposterCombo.set('Pick an option')
        self.imposterCombo.current(1)
        self.imposterCombo.grid(column = 1, row = 0)

        # Create frame for the run button and label
        self.runFrame = Frame(root)
        self.runFrame.grid(column = 0, row = 3)

        # Create label for Run button
        self.labelRun = Label(self.runFrame, text = 'Display players and tasks: ')
        self.labelRun.grid(column = 0, row = 3)

        # Create a button to run the program.  Executes runProgram
        self.buttonRun = Button(self.runFrame, text = 'Run', command = self.runProgram)
        self.buttonRun.grid(column = 1, row = 3)

        # Create a frame to house the list of players in the game
        self.playerFrame = Frame(root, highlightbackground = 'black', highlightthickness = 1)
        self.playerFrame.grid(column = 0, row = 4)

        # Create scrollbar for playerFrame
        self.playerScroll = ScrollableFrame(self.playerFrame)

        # Create a frame to house the list of tasks in the game
        self.taskFrame = Frame(root, highlightbackground = 'black', highlightthickness = 1)
        self.taskFrame.grid(column = 1, row = 4)

        # Create a scrollbar for taskFrame
        self.taskScroll = ScrollableFrame(self.taskFrame)

        # Create entry and button for adding new players to the player list
        self.addPlayerFrame = Frame(root)
        self.addPlayerFrame.grid(column = 0, row = 5)
        self.addPlayerLabel = Label(self.addPlayerFrame, text = 'Add more players:')
        self.addPlayerLabel.grid(column = 0, row = 0)
        self.addPlayerEntry = Entry(self.addPlayerFrame)
        self.addPlayerEntry.grid(column = 1, row = 0)
        self.addPlayerButton = Button(self.addPlayerFrame, text = 'Add', command = lambda: addPlayer(self.playerFile))
        self.addPlayerButton.grid(column = 2, row = 0)

        # Create an entry and button for adding new tasks to the task list
        self.addTaskFrame = Frame(root)
        self.addTaskFrame.grid(column = 1, row = 5)
        self.addTaskLabel = Label(self.addTaskFrame, text = 'Add more tasks:')
        self.addTaskLabel.grid(column = 0, row = 0)
        self.addTaskEntry = Entry(self.addTaskFrame)
        self.addTaskEntry.grid(column = 1, row = 0)
        self.addTaskButton = Button(self.addTaskFrame, text = 'Add', command = lambda: addTask(self.taskFile))
        self.addTaskButton.grid(column = 2, row = 0)

    def playerFileExplorer(self):
        """Opens a file explorer to choose a player file"""
        self.playerFile = filedialog.askopenfilename(initialdir = '/',
                                                        title = 'Select Player File',
                                                        filetypes = (('Text files', '*.txt'),))
        if self.playerFile != '':
            self.labelPlayerExplorer.configure(text='File Opened: ' + self.playerFile)

    def taskFileExplorer(self):
        """Opens a file explorer to choose a task file"""
        self.taskFile = filedialog.askopenfilename(initialdir = '/',
                                                    title = 'Select Task File',
                                                    filetypes = (('Text files', '*.txt'),))
        if self.taskFile != '':
            self.labelTaskExplorer.configure(text = 'File Opened: ' + self.taskFile)

    def runProgram(self):
        """Runs the majority of the program"""
        #removeLabels()
        self.imposterCount = self.imposterCombo.get()

        self.playerFile = '/Users/cremocal/Desktop/Python Projects/Among Us/players.txt'
        self.taskFile = '/Users/cremocal/Desktop/Python Projects/Among Us/tasks.txt'

        self.participants = getPlayers(self.playerFile)
        self.tasks = getTasks(self.taskFile)
        shuffleTasks(self.participants, self.tasks)
        self.players = cleanNonPlayers(self.participants)
        self.imposters = selectImposters(self.players, self.imposterCount)
        writeTasks(self.participants)
        #sendEmail(players, imposters)

        # Populate player frame
        for player in self.participants:
            if player.name in self.imposters:
                Label(self.playerScroll.scrollable_frame, text=player.name, fg='red').pack(anchor='w')
            elif int(player.playing) == 0:
                Label(self.playerScroll.scrollable_frame, text = player.name).pack(anchor='w')
            else:
                Label(self.playerScroll.scrollable_frame, text=player.name, fg='blue').pack(anchor='w')

        self.playerScroll.pack()

        # Populate task frame
        for task in self.tasks:
            Label(self.taskScroll.scrollable_frame, text=task[0]).pack(anchor='w')
        self.taskScroll.pack()


def addPlayer(fileName, playerName):
    with open(fileName, 'a') as playerFile:
        playerFile.write(playerName)


def addTask(fileName):
    pass


# Retrieve the list of players
def getPlayers(fileName):
    players = []

    with open(fileName, 'r') as roster:
        allData = roster.readlines()[1:]

        for player in allData:
            if not player.isspace():
                players.append(Player(player.split(',')[0] + ' ' + player.split(',')[1],
                                        player.split(',')[2], player.split(',')[3][:-1]))

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


            server.sendmail(senderEmail, player.email, message)
            print('Tasks and role successfully sent to ' + player.name + ' (' + player.email + ')')


def main():
     root = Tk()

     root.title('Among Us IRL')
     #root.geometry('700x700')
     gui = AmongUsGUI(root)

     root.mainloop()


if __name__ == '__main__':
    main()
