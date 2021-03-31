#!/usr/bin/env python
from string import ascii_uppercase, ascii_lowercase
from sys import argv, exit
from os import path
from logging import basicConfig, getLogger, DEBUG, INFO, CRITICAL
from pickle import dump, load
import hangManResources_rc
from PyQt5 import QtGui, uic
from PyQt5.QtCore import pyqtSlot, QSettings, Qt, QTimer, QCoreApplication
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
        self.usedWords = []
        self.availableWords = []
        self.currentWord = "sasquatch"
        self.currentWrongGuessCount = 0
        self.currentCorrectGuessCount = 0
        self.highlightedLetterButton = None
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

        # This will connect all of the letter buttons to one slot (Event Handler).
        # This eliminates the need for 26 event handling methods! :-)
        for letterButtonName in self.letterButtonNames:
            letterButtonName.clicked.connect(self.letterClicked)

        self.initializeLetterSlots((maxWordLengthDefault - len(self.currentWord)) // 2, len(self.currentWord))
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

        if self.gameOver:
            self.guessButton.setEnabled(False)
        else:
            self.guessButton.setEnabled(True)

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
        self.usedLetterButtons.append(self.highlightedLetterButton)
        if self.highlightedLetterButton is not None:
            guessedLetter = ascii_lowercase[self.letterButtonNames.index(self.highlightedLetterButton)]
            self.usedLetters.append(guessedLetter)
            self.highlightedLetterButton = None
            if guessedLetter.lower() not in self.currentWord:
                self.currentWrongGuessCount += 1
                print(f"Guessed incorrectly Right: {self.currentCorrectGuessCount} Wrong: {self.currentWrongGuessCount}")
                if self.currentWrongGuessCount >= wrongGuessMaxCountDefault:
                    self.gameOver = True
            else:
                for position, letter in enumerate(self.letterPositionsValues):
                    if letter.lower() == guessedLetter:
                        self.letterPositionsVisible[position] = True
                        self.currentCorrectGuessCount += 1
                        print(f"Guessed correctly Right: {self.currentCorrectGuessCount} Wrong: {self.currentWrongGuessCount}")
                        if self.currentCorrectGuessCount == len(self.currentWord):
                            self.gameWon = True
        else:
            self.logger.critical("Guessed letter was None")

        self.updateUI()

    @pyqtSlot()	   # Tells PyQT that we don't want the optional argument, and only want one signal for this autoconnect.
    def letterClicked(self):
        sender = self.sender()
        if sender in self.letterButtonNames:
            print(sender.text())
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
