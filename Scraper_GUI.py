import sys
import os


from PyQt6 import uic
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QWidget, 
    QHBoxLayout, 
    QVBoxLayout, 
    QGridLayout, 
    QLineEdit,
    QPushButton)
from PyQt6.QtGui import QPalette, QColor 

# app = QtWidgets.QApplication(sys.argv)

# window = uic.loadUi("untitled1/form.ui")
# window.show()
# app.exec()


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.load_ui()
        self.widgit_hub()

    def load_ui(self):
        # path = Path(__file__).resolve().parent / "form.ui"
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)
        else:
            raise Exception("Unable to find application path. Potentially neither script file nor frozen file")
        ui_file = uic.loadUi(application_path+ "/eHRAF_Scraper_Creator/form.ui", self)
    def widgit_hub(self):
        self.pushButton_URLSubmit.clicked.connect(self.set_text_box)

    def set_text_box(self):
        self.label.setText(self.plainTextEdit_URL.toPlainText())
        



def main():
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

