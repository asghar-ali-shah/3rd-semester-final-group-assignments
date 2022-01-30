from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFrame, QDialog, QMessageBox


class VLine(QFrame):
    # a simple Vertical Line
    def __init__(self):
        super(VLine, self).__init__()
        self.setFrameShape(self.VLine | self.Sunken)


class MyFindWidget(QDialog):
    def __init__(self, mainwindow):
        super(MyFindWidget, self).__init__()
        self.setGeometry(600, 300, 300, 200)
        self.setWindowTitle("Find A Word or Phrase")
        self.mainWindow = mainwindow
        # widgets
        self.findEditText = QtWidgets.QLineEdit()
        self.findButton = QtWidgets.QPushButton("Find")
        self.cancelButton = QtWidgets.QPushButton("Cancel")
        # GridLayout
        self.setContentsMargins(20, 20, 20, 20)
        self.lout = QtWidgets.QGridLayout()
        self.lout.setHorizontalSpacing(20)
        self.lout.addWidget(self.findEditText, 0, 0, 1, 2)
        self.lout.addWidget(self.findButton, 1, 0)
        self.lout.addWidget(self.cancelButton, 1, 1)
        self.setLayout(self.lout)
        self.findButton.clicked.connect(self.find_clicked)
        self.cancelButton.clicked.connect(self.cancel_clicked)
        self.exec_()

    def find_clicked(self):
        text = self.findEditText.text()
        if text.strip():
            self.close()
            self.mainWindow.find_text(text)
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Error:0 Length Find Term")
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Find Text Field is empty or having only spaces")
            msg.StandardButtons(QMessageBox.Ok)
            msg.exec_()

    def cancel_clicked(self):
        self.close()


class MyReplaceWidget(QDialog):
    def __init__(self, mainwindow):
        super(MyReplaceWidget, self).__init__()
        self.setGeometry(600, 300, 300, 200)
        self.setWindowTitle("Find A Word or Phrase")
        self.mainWindow = mainwindow
        # widgets
        self.replaceEditText = QtWidgets.QLineEdit()
        self.replaceByEditText = QtWidgets.QLineEdit()
        self.replaceButton = QtWidgets.QPushButton("Replace")
        self.cancelButton = QtWidgets.QPushButton("Cancel")
        # GridLayout
        self.setContentsMargins(20, 20, 20, 20)
        self.lout = QtWidgets.QGridLayout()
        self.lout.setHorizontalSpacing(20)
        self.lout.addWidget(QtWidgets.QLabel("Replace:"), 0, 0)
        self.lout.addWidget(self.replaceEditText, 1, 0, 1, 2)
        self.lout.addWidget(QtWidgets.QLabel("Replace By:"), 2, 0)
        self.lout.addWidget(self.replaceByEditText, 3, 0, 1, 2)
        self.lout.addWidget(self.replaceButton, 4, 0)
        self.lout.addWidget(self.cancelButton, 4, 1)
        self.setLayout(self.lout)
        self.replaceButton.clicked.connect(self.replace_clicked)
        self.cancelButton.clicked.connect(self.cancel_clicked)
        self.exec_()

    def replace_clicked(self):
        replace, replaceBy = self.replaceEditText.text(), self.replaceByEditText.text()
        if replace.strip() and replaceBy.strip():
            self.close()
            self.mainWindow.replace_text([replace, replaceBy])
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Error:0 Length Replace / Replace By Term")
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Replace / Replace Text Fields should not be empty or have only spaces")
            msg.StandardButtons(QMessageBox.Ok)
            msg.exec_()

    def cancel_clicked(self):
        self.close()
