# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.4.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QButtonGroup, QFrame, QHBoxLayout,
    QLabel, QMainWindow, QMenuBar, QPlainTextEdit,
    QPushButton, QScrollArea, QSizePolicy, QStatusBar,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setDocumentMode(False)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        self.line.setGeometry(QRect(0, 60, 551, 20))
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.scrollArea = QScrollArea(self.centralwidget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setGeometry(QRect(560, 20, 231, 411))
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 229, 409))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.plainTextEdit_URL = QPlainTextEdit(self.centralwidget)
        self.plainTextEdit_URL.setObjectName(u"plainTextEdit_URL")
        self.plainTextEdit_URL.setGeometry(QRect(10, 20, 431, 31))
        self.plainTextEdit_URL.setAutoFillBackground(False)
        self.plainTextEdit_URL.setOverwriteMode(False)
        self.pushButton_URLSubmit = QPushButton(self.centralwidget)
        self.pushButton_URLSubmit.setObjectName(u"pushButton_URLSubmit")
        self.pushButton_URLSubmit.setGeometry(QRect(450, 20, 100, 32))
        self.plainTextEdit_Keyword = QPlainTextEdit(self.centralwidget)
        self.plainTextEdit_Keyword.setObjectName(u"plainTextEdit_Keyword")
        self.plainTextEdit_Keyword.setGeometry(QRect(220, 100, 321, 31))
        self.plainTextEdit_Keyword.setAutoFillBackground(False)
        self.plainTextEdit_Keyword.setOverwriteMode(False)
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(40, 160, 511, 71))
        self.label.setAlignment(Qt.AlignCenter)
        self.layoutWidget = QWidget(self.centralwidget)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(20, 100, 191, 32))
        self.horizontalLayout = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.pushButton_KeyAnd = QPushButton(self.layoutWidget)
        self.buttonGroup_Keyword = QButtonGroup(MainWindow)
        self.buttonGroup_Keyword.setObjectName(u"buttonGroup_Keyword")
        self.buttonGroup_Keyword.setExclusive(True)
        self.buttonGroup_Keyword.addButton(self.pushButton_KeyAnd)
        self.pushButton_KeyAnd.setObjectName(u"pushButton_KeyAnd")
        self.pushButton_KeyAnd.setIconSize(QSize(36, 36))
        self.pushButton_KeyAnd.setCheckable(True)
        self.pushButton_KeyAnd.setChecked(True)
        self.pushButton_KeyAnd.setAutoDefault(False)
        self.pushButton_KeyAnd.setFlat(False)

        self.horizontalLayout.addWidget(self.pushButton_KeyAnd)

        self.pushButton_KeyOr = QPushButton(self.layoutWidget)
        self.buttonGroup_Keyword.addButton(self.pushButton_KeyOr)
        self.pushButton_KeyOr.setObjectName(u"pushButton_KeyOr")
        self.pushButton_KeyOr.setCheckable(True)

        self.horizontalLayout.addWidget(self.pushButton_KeyOr)

        self.pushButton_KeyNone = QPushButton(self.layoutWidget)
        self.buttonGroup_Keyword.addButton(self.pushButton_KeyNone)
        self.pushButton_KeyNone.setObjectName(u"pushButton_KeyNone")
        self.pushButton_KeyNone.setIconSize(QSize(24, 16))
        self.pushButton_KeyNone.setCheckable(True)
        self.pushButton_KeyNone.setChecked(False)

        self.horizontalLayout.addWidget(self.pushButton_KeyNone)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 24))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.pushButton_KeyAnd.setDefault(False)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"eHRAF Scraper", None))
        self.plainTextEdit_URL.setDocumentTitle("")
        self.plainTextEdit_URL.setPlainText(QCoreApplication.translate("MainWindow", u"URL Here", None))
        self.pushButton_URLSubmit.setText(QCoreApplication.translate("MainWindow", u"Submit", None))
        self.plainTextEdit_Keyword.setDocumentTitle("")
        self.plainTextEdit_Keyword.setPlainText(QCoreApplication.translate("MainWindow", u"Keyword(s)", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"empty2", None))
        self.pushButton_KeyAnd.setText(QCoreApplication.translate("MainWindow", u"And", None))
        self.pushButton_KeyOr.setText(QCoreApplication.translate("MainWindow", u"Or", None))
        self.pushButton_KeyNone.setText(QCoreApplication.translate("MainWindow", u"None", None))
    # retranslateUi

