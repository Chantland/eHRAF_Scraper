import sys
import os
from URL_generator import URL_generator as ug
import re
from eHRAF_Scraper import Scraper

from PyQt6 import uic
from PyQt6.QtCore import QSize, Qt, QRect
from PyQt6.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QWidget, 
    QHBoxLayout, 
    QVBoxLayout, 
    QGridLayout, 
    QLineEdit,
    QPushButton)
from PyQt6.QtGui import QPalette, QColor, QRegion, QPainter


# app = QtWidgets.QApplication(sys.argv)

# window = uic.loadUi("untitled1/form.ui")
# window.show()
# app.exec()


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.descript = ''
        self.URL = ''
        self.setFixedSize(QSize(850, 650))
        self.load_ui()
        self.widgit_setup()
        self.widgit_hub()

    def load_ui(self):
        # path = Path(__file__).resolve().parent / "form.ui"
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)
        else:
            raise Exception("Unable to find application path. Potentially neither script file nor frozen file")
        uic.loadUi(application_path+ "/eHRAF_Scraper_Creator/form.ui", self)
    def widgit_setup(self):
        # Set up the Id's to beter match what is used in the URL generator and for esear indexing
        # 0 None
        # 1 any (or)
        # 2 all (and)
        self.buttonGroup_Culture.setId(self.pushButton_CultNone, 0)
        self.buttonGroup_Culture.setId(self.pushButton_CultAny, 1)
        
        self.buttonGroup_Subject.setId(self.pushButton_SubNone, 0)
        self.buttonGroup_Subject.setId(self.pushButton_SubAny, 1)
        self.buttonGroup_Subject.setId(self.pushButton_SubAll, 2)

        self.buttonGroup_Keyword.setId(self.pushButton_KeyNone, 0)
        self.buttonGroup_Keyword.setId(self.pushButton_KeyAny, 1)
        self.buttonGroup_Keyword.setId(self.pushButton_KeyAll, 2)

        self.buttonGroup_SubjKey_Conj.setId(self.pushButton_SubKeyOr, 1)
        self.buttonGroup_SubjKey_Conj.setId(self.pushButton_SubKeyAnd, 2)

        self.continueButton = QPushButton(self)
        self.continueButton.setText("Continue")
        self.stopButton = QPushButton(self)
        self.stopButton.move(120,0)
        # self.buttonGroup_filter_CulturalLevel.setId(self.checkBox_EA, 0)
        # self.buttonGroup_filter_CulturalLevel.setId(self.checkBox_SCCS, 1)
        # self.buttonGroup_filter_CulturalLevel.setId(self.checkBox_PSF, 2)
        # self.buttonGroup_filter_CulturalLevel.setId(self.checkBox_SRS, 3)

    def widgit_hub(self):
        
        self.pushButton_URLSubmit.clicked.connect(self.set_URL)
        self.pushButton_AdvSubmit.clicked.connect(self.create_URL)
        
    def set_text_box(self):
        self.textBrowser.setText(self.plainTextEdit_URL.toPlainText())
    def textBox_descript_append(self, string:str):
        self.descript += string + "\n"
        self.textBrowser_Descript.setText(self.descript)
    def textBox_URL_set(self, string:str):
        string = "URL in use:\n" + self.URL
        self.textBrowser_URL.setText(string)
    def textBox_warning(self, warning:str):
        self.text_clear()
        self.textBrowser_Descript.setText(warning)
    def text_clear(self):
        self.descript = ''
        self.textBrowser_Descript.setText('')
        self.textBrowser_URL.setText('')
    def set_URL(self):
        URL = self.plainTextEdit_URL.toPlainText()
        if URL == '':
            self.textBox_warning("No URL submitted")
            return
        eHRAF_URL = re.match(r'^https://ehrafworldcultures.yale.edu/', URL)
        if not eHRAF_URL:
            self.textBox_warning("Error, must be a URL from eHRAF")
            return
        self.URL = URL
        self.textBox_URL_set("URL in use:\n"+ self.URL)
        self.web_scraper()
    def create_URL(self):
        cultures = self.plainTextEdit_Culture.toPlainText()
        cult_conj =  self.buttonGroup_Culture.id(self.buttonGroup_Culture.checkedButton())
        subjects = self.plainTextEdit_Subject.toPlainText()
        subjects_conj = self.buttonGroup_Subject.id(self.buttonGroup_Subject.checkedButton())
        concat_conj = self.buttonGroup_SubjKey_Conj.id(self.buttonGroup_SubjKey_Conj.checkedButton())
        keywords = self.plainTextEdit_Keyword.toPlainText()
        keywords_conj = self.buttonGroup_Keyword.id(self.buttonGroup_Keyword.checkedButton())
        # if one or more of the cultural filters are checked, append it to the list
        cultural_level_samples = []
        for i in range(4):
            if self.buttonGroup_filter_CulturalLevel.buttons()[i].isChecked():
                cultural_level_samples.append(self.buttonGroup_filter_CulturalLevel.buttons()[i].text())
        if cultures == '' and subjects == '' and keywords == '':
            self.textBox_warning("No search terms provided, please add then submit again.")
            return
        URL_gen = ug()
        URL = URL_gen.URL_generator(cultures=cultures,
                            cult_conj=cult_conj,
                            subjects=subjects,
                            subjects_conj=subjects_conj,
                            concat_conj= concat_conj,
                            keywords= keywords,
                            keywords_conj= keywords_conj,
                            cultural_level_samples= cultural_level_samples)
        if URL == '':
            self.textBox_warning("No viable search terms were found, please check for spelling mistakes")
            return
        self.URL = URL
        self.text_clear() #if success, clear out the windows
        self.textBox_descript_append(URL_gen.invalid_inputs())
        self.textBox_URL_set("URL in use:\n" + self.URL)
        self.web_scraper()
    def web_scraper(self):
        self.scraper = Scraper(url=self.URL)
        region_info = self.scraper.region_scraper()
        if region_info is not None:
            self.textBrowser_Descript.setText(region_info)
            self.scraper.web_close()
            return
        
        self.textBox_descript_append(self.scraper.time_req())
        self.textBox_descript_append('Press CONTINUE button or else choose a new query')
        self.continueButton.clicked.connect(self.web_continue())
    def web_continue(self):
        save_message = self.scraper.doc_scraper()
        self.textBox_descript_append('Complete scraping. check the terminal for more info')
        self.textBox_descript_append(save_message)


def main():
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

