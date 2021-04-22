#!/usr/bin/env python
from string import ascii_uppercase, ascii_lowercase
from sys import argv, exit
from os import path
from logging import basicConfig, getLogger, DEBUG, INFO, CRITICAL
from pickle import dump, load
from random import choice
import hangManResources_rc
from PyQt5 import QtGui, uic
from PyQt5.QtCore import pyqtSlot, QSettings, Qt, QTimer, QCoreApplication, QSignalMapper
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QMessageBox

startingDummyVariableDefault = 100
textOutputDefault = " ---- "
logFilenameDefault = 'hangMan.log'
createLogFileDefault = True
pickleFilenameDefault = ".hangManSavedObjects.pl"
numberOfPlayersDefault = 2
wordListDefault = ["sasquatch"]
wrongGuessMaxCountDefault = 6
maxWordLengthDefault = 15
maxNumberOfPlayers = 5

class PyQtStarter(QMainWindow):
    """A basic shell for a PyQt Project."""

    def __init__(self, parent=None):
        """ Build a GUI  main window for PyQtStarter."""

        super().__init__(parent)
        self.logger = getLogger("Fireheart.PyQtStarter")
        self.appSettings = QSettings()
        self.quitCounter = 0       # used in a workaround for a QT5 bug.

        self.pickleFilename = pickleFilenameDefault

        self.restoreSettings()

        try:
            self.pickleFilename = self.restoreGame()
        except FileNotFoundError:
            self.restartGame()

        uic.loadUi("hangManMainWindow.ui", self)

        self.dummyVariable = True
        self.textOutput = ""

        self.gameOver = False
        self.gameWon = False
        self.alerts = ""
        self.winCounts = [0] * 5
        self.usedWords = []
        self.availableWords = []
        self.currentPlayer = 1
        self.currentWord = ''
        self.currentWrongGuessCount = 0
        self.currentCorrectGuessCount = 0
        self.currentWrongGuessCounts = [0] * 5
        self.currentCorrectGuessCounts = [0] * 5
        self.highlightedLetterButton = None
        self.highlightedLetter = ""
        self.letterPositionsVisible = [False] * 15
        self.letterPositionsValues = [""] * 15
        self.usedLetters = []
        self.usedLetterButtons = []
        self.letterSlotNames = [self.letter1_UI, self.letter2_UI, self.letter3_UI, self.letter4_UI, self.letter5_UI,
                                self.letter6_UI, self.letter7_UI, self.letter8_UI, self.letter9_UI, self.letter10_UI,
                                self.letter11_UI, self.letter12_UI, self.letter13_UI, self.letter14_UI, self.letter15_UI
                                ]
        self.letterButtonNames = [self.letterA_UI, self.letterB_UI, self.letterC_UI, self.letterD_UI, self.letterE_UI,
                                  self.letterF_UI, self.letterG_UI, self.letterH_UI, self.letterI_UI, self.letterJ_UI,
                                  self.letterK_UI, self.letterL_UI, self.letterM_UI, self.letterN_UI, self.letterO_UI,
                                  self.letterP_UI, self.letterQ_UI, self.letterR_UI, self.letterS_UI, self.letterT_UI,
                                  self.letterU_UI, self.letterV_UI, self.letterW_UI, self.letterX_UI, self.letterY_UI,
                                  self.letterZ_UI
                                  ]
        self.playerIndicatorUI = [self.player1IndicatorUI, self.player2IndicatorUI, self.player3IndicatorUI,
                              self.player4IndicatorUI, self.player5IndicatorUI]
        self.rightCountsUI = [self.player1RightUI, self.player2RightUI, self.player3RightUI,
                              self.player4RightUI, self.player5RightUI]
        self.wrongCountsUI = [self.player1WrongUI, self.player2WrongUI, self.player3WrongUI,
                              self.player4WrongUI, self.player5WrongUI]
        self.indicatorStyleStrings = ["color:rgba(255, 0, 0, 0.25);",
                                      "color:rgba(0, 0, 255, 0.25);",
                                      "color:rgba(0, 255, 0, 0.25);",
                                      "color:rgba(253, 128, 8, 0.25);",
                                      "color: rgba(128, 0, 128, 0.25);",
                                      "color:rgba(255, 0, 0, 1.0);",
                                      "color:rgba(0, 0, 255, 1.0);",
                                      "color:rgba(0, 255, 0, 1.0);",
                                      "color:rgba(253, 128, 8, 1.0);",
                                      "color: rgba(128, 0, 128, 1.0);"
                                      ]
        # This will connect all of the letter buttons to one slot (Event Handler).
        # This eliminates the need for 26 event handling methods! :-)
        self.mapper = QSignalMapper()
        for buttonNumber, buttonName in enumerate(self.letterButtonNames):
            buttonName.clicked.connect(self.mapper.map)
            mappedLetter = ascii_lowercase[buttonNumber]
            self.mapper.setMapping(buttonName, ascii_lowercase[buttonNumber])
        self.mapper.mapped[str].connect(self.letterClicked)
        # for letterButtonName in self.letterButtonNames:
        #     letterButtonName.clicked.connect(self.letterClicked)

        self.startNewGame()
        self.preferencesSelectButton.clicked.connect(self.preferencesSelectButtonClickedHandler)
        self.guessButton.clicked.connect(self.guessButtonClickedHandler)

    def __str__(self):
        """String representation for PyQtStarter.
        """

        return "Gettin' started with Qt!!"

    def updateUI(self):
        # self.textOutputUI.setText(self.textOutput)
        for buttonName in self.letterButtonNames:
            if buttonName in self.usedLetterButtons:
                buttonName.setStyleSheet("color: blue")
                buttonName.setEnabled(False)
            else:
                buttonName.setStyleSheet("color: black")
                buttonName.setEnabled(True)
        if self.highlightedLetterButton is not None:
            self.highlightedLetterButton.setStyleSheet("color: red")
        if self.currentWrongGuessCount < 1:
            self.hangManHeadUI.setPixmap(QtGui.QPixmap(""))
        elif self.currentWrongGuessCount >= 1 and self.currentWrongGuessCount < wrongGuessMaxCountDefault:
            self.hangManHeadUI.setPixmap(QtGui.QPixmap(":/images/liveHead"))
        else:
            self.hangManHeadUI.setPixmap(QtGui.QPixmap(":/images/deadHead"))
        if self.currentWrongGuessCount > 1:
            self.hangManBodyUI.setPixmap(QtGui.QPixmap(":/images/" + str(self.currentWrongGuessCount)))
        else:
            self.hangManBodyUI.setPixmap(QtGui.QPixmap(""))
        for position, slotName in enumerate(self.letterSlotNames):
            if self.letterPositionsVisible[position]:
                slotName.setStyleSheet("background-color: transparent; color: black")

        for index in range(0, self.numberOfPlayers):
            self.rightCountsUI[index].setText(str(self.currentCorrectGuessCounts[index]))
            self.wrongCountsUI[index].setText(str(self.currentWrongGuessCounts[index]))
            if index + 1 == self.currentPlayer:     # Set opacity to full
                self.playerIndicatorUI[index].setStyleSheet(self.indicatorStyleStrings[index + maxNumberOfPlayers])
            else:                                   # Set opacity to 1/4
                self.playerIndicatorUI[index].setStyleSheet(self.indicatorStyleStrings[index])

        if self.gameOver:
            self.guessButton.setEnabled(False)
        else:
            self.guessButton.setEnabled(True)

        if self.alerts != '':
            self.statusBarUI.showMessage(self.alerts)
            self.statusBarTimer = QTimer()
            self.statusBarTimer.singleShot(6500, self.clearStatusBar)

    def startNewGame(self):
        try:
            self.currentWord = choice(self.wordList)
            print(f"Current word: {self.currentWord}")
        except IndexError:
            self.logger.info("Recycling word list.")
            self.wordList = self.usedWords
            self.usedWords = []
        self.wordList.remove(self.currentWord)
        self.usedWords.append(self.currentWord)
        self.gameOver = False
        self.gameWon = False
        self.currentWrongGuessCount = 0
        self.currentCorrectGuessCount = 0
        self.currentWrongGuessCounts = [0] * 5
        self.currentCorrectGuessCounts = [0] * 5
        self.highlightedLetterButton = None
        self.highlightedLetter = ""
        self.letterPositionsVisible = [False] * 15
        self.clearLetterButtons()
        self.initializeLetterSlots((self.maxWordLength - len(self.currentWord)) // 2, len(self.currentWord))
        self.updateUI()

    def clearLetterButtons(self):
        self.usedLetters = []
        self.usedLetterButtons = []

    def initializeLetterSlots(self, startingPosition, letterCount):
        for position in range(0, startingPosition):
            self.letterSlotNames[position].setText("")
        for position in range(startingPosition + letterCount, len(self.letterSlotNames)):
            self.letterSlotNames[position].setText("")
        for position in range(startingPosition, startingPosition + letterCount):
            self.letterSlotNames[position].setText(self.currentWord[position - startingPosition])
            self.letterPositionsValues[position] = self.currentWord[position - startingPosition]
        for slotName in self.letterSlotNames[startingPosition:startingPosition + letterCount]:
            slotName.setStyleSheet("background-color: gray; color: gray")

    def restartGame(self):
        if self.createLogFile:
            self.logger.debug("Restarting program")

    def saveGame(self):
        if self.createLogFile:
            self.logger.debug("Saving program state")
        saveItems = (self.dummyVariable)
        if self.appSettings.contains('pickleFilename'):
            with open(path.join(path.dirname(path.realpath(__file__)),  self.appSettings.value('pickleFilename', type=str)), 'wb') as pickleFile:
                dump(saveItems, pickleFile)
        elif self.createLogFile:
                self.logger.critical("No pickle Filename")

    def restoreGame(self):
        if self.appSettings.contains('pickleFilename'):
            self.appSettings.value('pickleFilename', type=str)
            with open(path.join(path.dirname(path.realpath(__file__)),  self.appSettings.value('pickleFilename', type=str)), 'rb') as pickleFile:
                return load(pickleFile)
        else:
            self.logger.critical("No pickle Filename")

    def restoreSettings(self):
        if appSettings.contains('createLogFile'):
            self.createLogFile = appSettings.value('createLogFile')
        else:
            self.createLogFile = createLogFileDefault
            appSettings.setValue('createLogFile', self.createLogFile)

        if self.createLogFile:
            self.logger.debug("Starting restoreSettings")
        # Restore settings values, write defaults to any that don't already exist.
        if self.appSettings.contains('numberOfPlayers'):
            self.numberOfPlayers = self.appSettings.value('numberOfPlayers', type=int)
        else:
            self.numberOfPlayers = numberOfPlayersDefault
            self.appSettings.setValue('numberOfPlayers', self.numberOfPlayers)

        if self.appSettings.contains('maxWordLength'):
            self.maxWordLength = self.appSettings.value('maxWordLength', type=int)
        else:
            self.maxWordLength = maxWordLengthDefault
            self.appSettings.setValue('maxWordLength', self.maxWordLength)

        if self.appSettings.contains('wordList'):
            self.wordList = self.appSettings.value('wordList', [], type=str)
        else:
            self.wordList = wordListDefault
            self.appSettings.setValue('wordList', self.wordList)

        if self.appSettings.contains('createLogFile'):
            self.createLogFile = self.appSettings.value('createLogFile')
        else:
            self.createLogFile = logFilenameDefault
            self.appSettings.setValue('createLogFile', self.createLogFile)

        if self.appSettings.contains('logFile'):
            self.logFilename = self.appSettings.value('logFile', type=str)
        else:
            self.logFilename = logFilenameDefault
            self.appSettings.setValue('logFile', self.logFilename)

        if self.appSettings.contains('pickleFilename'):
            self.pickleFilename = self.appSettings.value('pickleFilename', type=str)
        else:
            self.pickleFilename = pickleFilenameDefault
            self.appSettings.setValue('pickleFilename', self.pickleFilename)

    def guessButtonClickedHandler(self):
        if self.highlightedLetterButton is not None:
            self.usedLetterButtons.append(self.highlightedLetterButton)
            guessedLetter = self.highlightedLetter
            self.usedLetters.append(guessedLetter)
            self.highlightedLetterButton = None
            if guessedLetter.lower() not in self.currentWord:
                self.currentWrongGuessCounts[self.currentPlayer - 1] += 1
                self.currentWrongGuessCount = sum(self.currentWrongGuessCounts)
                print(f"Guessed correctly Right: {self.currentCorrectGuessCount} Wrong: {self.currentWrongGuessCount}")
                print(f"Guessed incorrectly Right: {self.currentCorrectGuessCounts} Wrong: {self.currentWrongGuessCounts}")
                if self.currentWrongGuessCount >= wrongGuessMaxCountDefault:
                    self.declareGameOver(False)
                self.currentPlayer += 1
                self.currentPlayer = 1 if self.currentPlayer > self.numberOfPlayers else self.currentPlayer
                # Switch player on wrong guess. self.currentPlayer is 1 indexed.

            else:
                for position, letter in enumerate(self.letterPositionsValues):
                    if letter.lower() == guessedLetter:
                        self.letterPositionsVisible[position] = True
                        self.currentCorrectGuessCounts[self.currentPlayer - 1] += 1
                        self.currentCorrectGuessCount = sum(self.currentCorrectGuessCounts)
                        print(f"Guessed correctly Right: {self.currentCorrectGuessCount} Wrong: {self.currentWrongGuessCount}")
                        print(f"Guessed correctly Right: {self.currentCorrectGuessCounts} Wrong: {self.currentWrongGuessCounts}")
                        if self.currentCorrectGuessCount == len(self.currentWord):
                            self.declareGameOver(True)
        else:
            self.logger.critical("Guessed letter was None")
        if self.gameOver:
            self.restartTimer = QTimer()
            self.restartTimer.singleShot(6500, self.startNewGame)
        self.updateUI()

    def declareGameOver(self, won):
        self.gameOver = True
        self.gameWon = won
        if won:
            self.alerts = f"Player {self.currentPlayer} won!!"
        else:
            self.alerts = f"Player {self.currentPlayer} lost."
        self.letterPositionsVisible = [True] * 15

    def clearStatusBar(self):
        print("Clearing the status bar")
        self.alerts = ""
        self.statusBarUI.clearMessage()
        self.updateUI()

    @pyqtSlot(str)
    def letterClicked(self, clickedLetter):
        sender = self.sender().mapping(clickedLetter)
        # sender = self.highlightedLetterButton[ascii_lowercase.index(clickedLetter)]
        self.highlightedLetter = clickedLetter
        if sender in self.letterButtonNames:
            print(clickedLetter)
            self.highlightedLetterButton = sender
        else:
            self.logger.critical(f"Unknown letter sent by {self.sender()}")
        self.updateUI()

    @pyqtSlot()  # User is requesting preferences editing dialog box.
    def preferencesSelectButtonClickedHandler(self):
        if self.createLogFile:
            self.logger.info("Setting preferences")
        preferencesDialog = PreferencesDialog()
        preferencesDialog.show()
        preferencesDialog.exec_()
        self.restoreSettings()              # 'Restore' settings that were changed in the dialog window.
        self.updateUI()

    @pyqtSlot()				# Player asked to quit the game.
    def closeEvent(self, event):
        if self.createLogFile:
            self.logger.debug("Closing app event")
        if self.quitCounter == 0:
            self.quitCounter += 1
            quitMessage = "Are you sure you want to quit?"
            reply = QMessageBox.question(self, 'Message', quitMessage, QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.saveGame()
                event.accept()
            else:
                self.quitCounter = 0
                event.ignore()


class PreferencesDialog(QDialog):
    def __init__(self, parent=PyQtStarter):
        super(PreferencesDialog, self).__init__()

        uic.loadUi('preferencesDialog.ui', self)
        self.logger = getLogger("Fireheart.PyQtStarter")

        self.appSettings = QSettings()
        if self.appSettings.contains('numberOfPlayers'):
            self.numberOfPlayers = self.appSettings.value('numberOfPlayers', type=int)
        else:
            self.numberOfPlayers = numberOfPlayersDefault
            self.appSettings.setValue('numberOfPlayers', self.numberOfPlayers)

        if self.appSettings.contains('maxWordLength'):
            self.maxWordLength = self.appSettings.value('maxWordLength', type=int)
        else:
            self.maxWordLength = maxWordLengthDefault
            self.appSettings.setValue('maxWordLength', self.maxWordLength)

        if self.appSettings.contains('wordList'):
            self.wordList = self.appSettings.value('wordList', [], type=str)
        else:
            self.wordList = wordListDefault
            self.appSettings.setValue('wordList', self.wordList)

        if self.appSettings.contains('logFile'):
            self.logFilename = self.appSettings.value('logFile', type=str)
        else:
            self.logFilename = logFilenameDefault
            self.appSettings.setValue('logFile', self.logFilename)

        if self.appSettings.contains('createLogFile'):
            self.createLogFile = self.appSettings.value('createLogFile')
        else:
            self.createLogFile = logFilenameDefault
            self.appSettings.setValue('createLogFile', self.createLogFile )

        self.buttonBox.rejected.connect(self.cancelClickedHandler)
        self.buttonBox.accepted.connect(self.okayClickedHandler)
        self.numberOfPlayersUI.editingFinished.connect(self.numberOfPlayersValueChanged)
        self.maxWordLengthUI.editingFinished.connect(self.maxWordLengthValueChanged)
        self.logFilenameUI.editingFinished.connect(self.logFilenameValueChanged)
        self.wordListUI.textChanged.connect(self.wordListValueChanged)
        self.createLogfileCheckBox.stateChanged.connect(self.createLogFileChanged)

        self.updateUI()

    # @pyqtSlot()
    def numberOfPlayersValueChanged(self):
        self.numberOfPlayers = int(self.numberOfPlayersUI.text())

    # @pyqtSlot()
    def maxWordLengthValueChanged(self):
        self.thirdVariable = int(self.maxWordLengthUI.text())

    # @pyqtSlot()
    def logFilenameValueChanged(self):
        self.logFilename = self.logFilenameUI.text()

    # @pyqtSlot()
    def wordListValueChanged(self):
        self.wordList = self.wordListUI.toPlainText().strip().split('\n')

    # @pyqtSlot()
    def createLogFileChanged(self):
        self.createLogFile = self.createLogfileCheckBox.isChecked()

    def updateUI(self):
        self.numberOfPlayersUI.setValue(self.numberOfPlayers)
        self.maxWordLengthUI.setValue(self.maxWordLength)
        self.logFilenameUI.setText(self.logFilename)
        self.wordListUI.setText('\n'.join(self.wordList))
        if self.createLogFile:
            self.createLogfileCheckBox.setCheckState(Qt.Checked)
        else:
            self.createLogfileCheckBox.setCheckState(Qt.Unchecked)

    # @pyqtSlot()
    def okayClickedHandler(self):
        # write out all settings
        preferencesGroup = (('numberOfPlayers', self.numberOfPlayers),
                            ('maxWordLength', self.maxWordLength),
                            ('wordList', self.wordList),
                            ('logFile', self.logFilename),
                            ('createLogFile', self.createLogFile),
                            )
        # Write settings values.
        for setting, variableName in preferencesGroup:
            # if self.appSettings.contains(setting):
            self.appSettings.setValue(setting, variableName)

        self.close()

    # @pyqtSlot()
    def cancelClickedHandler(self):
        self.close()


if __name__ == "__main__":
    QCoreApplication.setOrganizationName("Fireheart Software")
    QCoreApplication.setOrganizationDomain("fireheartsoftware.com")
    QCoreApplication.setApplicationName("HangMan")
    appSettings = QSettings()
    if appSettings.contains('createLogFile'):
        createLogFile = appSettings.value('createLogFile')
    else:
        createLogFile = createLogFileDefault
        appSettings.setValue('createLogFile', createLogFile)

    if createLogFile:
        startingFolderName = path.dirname(path.realpath(__file__))
        if appSettings.contains('logFile'):
            logFilename = appSettings.value('logFile', type=str)
        else:
            logFilename = logFilenameDefault
            appSettings.setValue('logFile', logFilename)
        basicConfig(filename=path.join(startingFolderName, logFilename), level=INFO,
                    format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s')
    app = QApplication(argv)
    PyQtStarterApp = PyQtStarter()
    PyQtStarterApp.updateUI()
    PyQtStarterApp.show()
    exit(app.exec_())
