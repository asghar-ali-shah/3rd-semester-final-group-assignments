import PyQt5
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QFrame, QMessageBox, QLabel
import sys

from MyWidgets import VLine, MyFindWidget, MyReplaceWidget

welcome_msg = '''Welcome to ModPad -- The Modified Version of Notepad 

Data Structures Final Group Assignment # 1     


Group Members: 
        ----- Asghar Ali Shah -- Abdul Basit -- Yahya Malik -----
        
        
        
        
        
        
        
                            🐭 🐈
'''


def get_lower_case(text: str):
    return " ".join([word.lower() for word in text.split(" ")])


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        self.setWindowTitle('ModPad')
        self.setWindowIcon(QtGui.QIcon("icon.svg"))
        self.setGeometry(250, 100, 1100, 700)
        self.filename = ''
        # QPlainTextEdit setup
        self.editText = QtWidgets.QPlainTextEdit(welcome_msg)
        self.editText.setFont(PyQt5.QtGui.QFont())
        self.editText.setLineWrapMode(0)
        self.editText.setUndoRedoEnabled(True)
        self.editText.setFont(QtGui.QFont("Droid Sans Mono", 14, QtGui.QFont.Weight.Normal))
        self.setCentralWidget(self.editText)
        self.cursor = self.editText.textCursor()

        # menubar Setup
        menubar = self.menuBar()
        # file menu
        self.fileMenu = menubar.addMenu("File")
        self.fileMenu.addAction("New", self.new_act, shortcut=PyQt5.QtGui.QKeySequence.New).setStatusTip(
            "Create a New File")
        self.fileMenu.addAction("Open..", self.open_act, shortcut=PyQt5.QtGui.QKeySequence.Open).setStatusTip(
            "Open a File")
        self.fileMenu.addAction("Save", self.save_act, shortcut=PyQt5.QtGui.QKeySequence.Save).setStatusTip(
            "Save a File")
        self.fileMenu.addAction("Save As", self.save_as_act, shortcut='Ctrl+Shift+s').setStatusTip(
            "Save File as")
        self.fileMenu.addAction("Exit", self.exit_act, shortcut=PyQt5.QtGui.QKeySequence.Quit).setStatusTip(
            "Exit ModPad")
        # edit menu
        self.editMenu = menubar.addMenu("Edit")
        self.editMenu.addAction("Change Font", self.change_font_act).setStatusTip("Change Editor Font")
        self.editMenu.addAction("Zoom In/Increase Font Size", self.zoom_in_act, shortcut='Ctrl+=').setStatusTip(
            "Zoom In")
        self.editMenu.addAction("Zoom Out/Decrease Font Size", self.zoom_out_act,
                                shortcut=PyQt5.QtGui.QKeySequence.ZoomOut).setStatusTip("Zoom Out")
        self.editMenu.addAction("Undo", self.undo_act, shortcut=PyQt5.QtGui.QKeySequence.Undo).setStatusTip(
            "Perform Undo")
        self.editMenu.addAction("Redo", self.redo_act, shortcut=PyQt5.QtGui.QKeySequence.Redo).setStatusTip(
            "Perform Redo")

        # view Menu
        self.viewMenu = menubar.addMenu("View")
        self.viewMenu.addAction("Find", self.find_act, shortcut=PyQt5.QtGui.QKeySequence.Find).setStatusTip("Find a "
                                                                                                            "Word or "
                                                                                                            "Phrase")
        self.viewMenu.addAction("Replace", self.replace_act, shortcut=PyQt5.QtGui.QKeySequence.Replace) \
            .setStatusTip("Replace a Word or Phrase with another")

        # toolbar Setup
        self.toolBar = self.addToolBar('Clear Formatting')
        self.clearFormattingAction = QtWidgets.QAction("Clear Formatting")
        self.clearFormattingAction.triggered.connect(self.clear_formatting)
        self.clearFormattingAction.setStatusTip("Clear Text Formatting of Find Action")
        self.toolBar.addAction(self.clearFormattingAction)
        self.toolBar.hide()
        # statusBar setup
        self.statusBar = QtWidgets.QStatusBar()
        self.setStatusBar(self.statusBar)

        # save status label on statusBar
        self.saveLabel = QtWidgets.QLabel()
        self.editText.textChanged.connect(self.save_state_changed_act)

        # word count label on statusBar
        self.statusBar.addPermanentWidget(self.saveLabel)
        self.statusBar.addPermanentWidget(VLine())
        self.statusBar.addPermanentWidget(QtWidgets.QLabel("Words: "))
        self.countLabel = QtWidgets.QLabel()
        self.statusBar.addPermanentWidget(self.countLabel)
        self.count_words()

        # Words Found Count on status bar
        self.findCount = QLabel("")
        self.statusBar.addPermanentWidget(VLine())
        self.statusBar.addPermanentWidget(self.findCount)

    ################ Functions #################

    def new_act(self):
        if self.saveLabel.text() != "SAVED" or len(self.editText.toPlainText()):
            self.show_save_warning()
        else:
            self.editText.clear()
            self.filename = ""

    def open_act(self):
        filename = QtWidgets.QFileDialog().getOpenFileName()[0]
        if filename:
            try:
                with open(filename, 'r') as file:
                    self.filename = filename
                    self.editText.clear()
                    self.editText.setPlainText(file.read())
                    self.editText.moveCursor(PyQt5.QtGui.QTextCursor.Start)
                    filename = filename[0].split("/")
                    filename = filename[len(filename) - 1]
                    self.statusBar.showMessage(f'Editing --  {filename}', 2500)
                    self.saveLabel.setText("SAVED")
            except FileNotFoundError:
                pass

    def save_as_act(self):
        filename = QtWidgets.QFileDialog().getSaveFileName()[0]
        try:
            file = open(filename, 'w')
            self.filename = filename
            file.write(self.editText.toPlainText())
            file.close()
            self.saveLabel.setText("SAVED")
            if self.filename:
                self.statusBar.showMessage(f'Saved to {self.filename}', 2500)
        except FileNotFoundError:
            pass

    def save_act(self):
        try:
            file = open(self.filename, 'w')
            file.write(self.editText.toPlainText())
            file.close()
            self.saveLabel.setText("SAVED")
            if self.filename:
                self.statusBar.showMessage(f'Saved to {self.filename}', 2500)
        except FileNotFoundError:
            self.save_as_act()

    def change_font_act(self):
        font, valid = QtWidgets.QFontDialog().getFont()
        if valid:
            self.editText.setFont(font)
        self.statusBar.showMessage(f'Font Changed to {font.rawName()}')

    def zoom_in_act(self):
        if self.editText.font().pointSize() < 31:
            self.editText.zoomIn(1)

    def zoom_out_act(self):
        if self.editText.font().pointSize() > 9:
            self.editText.zoomOut(1)

    def undo_act(self):
        self.editText.undo()

    def redo_act(self):
        self.editText.redo()

    def show_save_warning(self):
        msg = QMessageBox()
        msg.setWindowTitle("Save Document")
        msg.setText("Current File is not saved. Are You Sure You "
                    "Want to Continue Nig?")
        msg.setInformativeText("You wil lost all of your unsaved data on this file.")
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        msg.buttonClicked.connect(self.popup_button_new)
        msg.exec_()

    def popup_button_new(self, i):
        if i.text() == "&Yes":
            self.editText.clear()

    def save_state_changed_act(self):
        self.saveLabel.setText("**NOT SAVED**")
        self.count_words()

    def count_words(self):
        text = self.editText.toPlainText()
        count = text.split(" ")
        count = [i for i in count if i.strip()]
        self.countLabel.setText(str(len(count)))

    def word_count_act(self):
        pass

    def exit_act(self):
        msg = QMessageBox()
        msg.setWindowTitle("Exit ModPad")
        msg.setText("Current File is not saved. Are You Sure You "
                    "Want to Exit ModPad Nig?")
        msg.setInformativeText("You wil lost all of your unsaved data on this file.")
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.buttonClicked.connect(self.popup_button_exit)
        msg.exec_()

    def popup_button_exit(self, i):
        if i.text() == "&Yes":
            self.close()

    def find_act(self):
        MyFindWidget(self)

    def find_text(self, text):
        highlightFormat = QtGui.QTextCharFormat()
        highlightFormat.setBackground(QtGui.QBrush(QtGui.QColor("grey")))
        pattern = text.lower()
        regex = QtCore.QRegExp(pattern)
        # Process the displayed document
        pos = 0
        index = regex.indexIn(get_lower_case(self.editText.toPlainText()), pos)
        count = 0
        while index != -1:
            # Select the matched text and apply the desired format
            self.cursor.setPosition(index)
            self.cursor.movePosition(QtGui.QTextCursor.EndOfWord, 1)
            if index != 0 and self.editText.toPlainText()[index - 1] == " ":
                self.cursor.mergeCharFormat(highlightFormat)
                count += 1
            # Move to the next match
            pos = index + regex.matchedLength()
            index = regex.indexIn(get_lower_case(self.editText.toPlainText()), pos)
        msg = QMessageBox()
        msg.setWindowTitle("Words Found")
        if count == 0:
            msg.setText(f'No Words Found!')
        else:
            msg.setText(f'Words Found: {count}')
            self.findCount.setText(f'Words Find Count: {count}')
            self.toolBar.show()
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

    def replace_act(self):
        MyReplaceWidget(self)
    
    def replace_text(self, text):
        old = text[0]
        new = text[1]

        # Beginning of undo block
        self.cursor.beginEditBlock()

        # Use flags for case match
        flags = QtGui.QTextDocument.FindFlags()
        flags = flags | QtGui.QTextDocument.FindFlag.FindCaseSensitively

        # Replace all we can
        while True:
            # self.editor is the QPlainTextEdit
            r = self.editText.find(old, flags)
            if r:
                qc = self.editText.textCursor()
                if qc.hasSelection():
                    qc.insertText(new)
            else:
                break

        # Mark end of undo block
        self.cursor.endEditBlock()

    def clear_formatting(self):
        text = str(self.editText.toPlainText())
        self.editText.clear()
        self.editText.setPlainText(text)
        self.findCount.setText("")
        self.toolBar.hide()


app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec_())

# noinspection PyUnreachableCode
'''
################## TO FIX #####################

--> error on canceling file opening -- Resolved
--> add themes functionality -- idea dropped
--> redo, undo -- later
-->MyFindWidget, Replace -- in work


'''
