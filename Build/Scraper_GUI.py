# for installing the GUI (if you want to make changes) use the py installer prompt: 
# pyinstaller --onefile --add-data 'Resources/favicon.icns:.' --add-data 'Resources/eHRAF_Scraper_Creator:eHRAF_Scraper_Creator'  --icon=Resources/favicon.icns Scraper_GUI.py
# then place the file created in the dist folder into the main folder where the Scraper_GUI.py was first ran. You may need to manually chnage the icon

# DONE: Cannot run two subsequent runs of the scraper without it crashing. Perhaps due to issues with initializing and deleting the driver.
# DONE: check scraper for crashes. There is one which I thought was fixed but maybe not. It happens when the initial source tabs are clicked but cannot load yet seem to not initialize the reclick feature. Currently the error will save a partial file.
# DONE: fix scraper info which returns the number of rows of the excel file rather than the number of passages.
# DONE: initialize the options for headless and rerun
# DONE: standardize the save files so that similar search terms (pear, grandma vs. grandma, pear) are regarded as the same.
# DONE: implement "enter name" feature. This is easy to implement but hard to look nice without crowding.
# DONE: implement better looking continue button which is unclicakble until the right time
# TODO: implement a stop button
# TODO: if possible make the terminal print out to the GUI's terminal but this is optional.

import sys
import os
from URL_Generator import URL_Generator as ug
import re
from eHRAF_Scraper import Scraper

import PyQt6
from PyQt6 import uic
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import (
    QApplication, 
    QMainWindow)
from PyQt6.QtGui import QIcon


# app = QtWidgets.QApplication(sys.argv)

# window = uic.loadUi("untitled1/form.ui")
# window.show()
# app.exec()


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.descript = ''
        self.URL = ''
        self.setFixedSize(QSize(880, 780))
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
        uic.loadUi(application_path+ "/Resources/eHRAF_Scraper_Creator/form.ui", self)
    def widgit_setup(self):
        # Set up the Id's to beter match what is used in the URL generator and for easier indexing
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

        # self.continueButton = QPushButton(self)
        # self.continueButton.setText("Continue")
        # self.stopButton = QPushButton(self)
        # self.stopButton.move(120,0)
        # self.buttonGroup_Filter_CulturalLevel.setId(self.checkBox_EA, 0)
        # self.buttonGroup_Filter_CulturalLevel.setId(self.checkBox_SCCS, 1)
        # self.buttonGroup_Filter_CulturalLevel.setId(self.checkBox_PSF, 2)
        # self.buttonGroup_Filter_CulturalLevel.setId(self.checkBox_SRS, 3)

    def widgit_hub(self):
        # set up the submit buttons to listen for clicks
        self.pushButton_URLSubmit.clicked.connect(self.set_URL)
        self.pushButton_AdvSubmit.clicked.connect(self.create_URL)
        # continue on when user is ready
        self.pushButton_Continue.clicked.connect(self.web_continue)
    def set_text_box(self): #relic from previous test, DELETE
        self.textBrowser.setText(self.plainTextEdit_URL.toPlainText())
    def textBox_descript_append(self, string:str): #update the description box
        self.descript += string + "\n\n"
        self.textBrowser_Descript.setText(self.descript)
    def textBox_URL_set(self): #update the URL box
        self.textBrowser_URL.setText(self.URL)
    def textBox_warning(self, warning:str): #give warning flag if user does something wrong
        self.text_clear()
        self.textBrowser_Descript.setText(warning)
        self.pushButton_Continue.setEnabled(False)
    def text_clear(self): #clear both boxes of text
        self.descript = ''
        self.textBrowser_Descript.setText('')
        self.textBrowser_URL.setText('')
    def set_URL(self): #if URL submit button is clicked, just use that URL but first check if it is valid
        URL = self.plainTextEdit_URL.toPlainText()
        if URL == '':
            self.textBox_warning("No URL submitted")
            return
        eHRAF_URL = re.match(r'^https://ehrafworldcultures.yale.edu/search', URL)
        if not eHRAF_URL:    
            self.textBox_warning("Error, must be a search URL from eHRAF")
            return
        self.URL = URL
        self.text_clear() #if success, clear out the windows
        self.textBox_URL_set()
        self.web_scraper()
    def create_URL(self): #construct the URL from the inputs of the advanced search
        # extract all the advanced search input boxes and buttons
        cultures = self.plainTextEdit_Culture.toPlainText()
        cult_conj =  self.buttonGroup_Culture.id(self.buttonGroup_Culture.checkedButton())
        subjects = self.plainTextEdit_Subject.toPlainText()
        subjects_conj = self.buttonGroup_Subject.id(self.buttonGroup_Subject.checkedButton())
        concat_conj = self.buttonGroup_SubjKey_Conj.id(self.buttonGroup_SubjKey_Conj.checkedButton())
        keywords = self.plainTextEdit_Keyword.toPlainText()
        keywords_conj = self.buttonGroup_Keyword.id(self.buttonGroup_Keyword.checkedButton())
        # check to make sure a search term was provided
        if cultures == '' and subjects == '' and keywords == '':
            self.textBox_warning("No search terms provided, please add then submit again.")
            return
        # if one or more of the cultural filters are checked, append it to the list
        cultural_level_samples = []
        for i in range(4):
            if self.buttonGroup_Filter_CulturalLevel.buttons()[i].isChecked():
                cultural_level_samples.append(self.buttonGroup_Filter_CulturalLevel.buttons()[i].text())
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
        self.textBox_descript_append(URL_gen.invalid_inputs()) #Add invalid inputs and scraper count
        self.textBox_URL_set()
        self.web_scraper()
    def web_scraper(self):

        # Set Info
        user = self.plainTextEdit_NameInput.toPlainText()
        if user == '':
            user = None
        
        # set options
        # if "Show Browser?" is marked as "No" then do not show the browser upon launch
        if self.buttonGroup_Options_ShowBrowser.id(self.buttonGroup_Options_ShowBrowser.checkedButton()) == -2:
            headless = True
        else:
            headless = False
        # if "partial files?" is marked "No" then do not use the partial files if present
        if self.buttonGroup_Options_PartialFile.id(self.buttonGroup_Options_PartialFile.checkedButton()) == -2:
            rerun = True
        else:
            rerun = False

        # initialize the scraper
        self.scraper = Scraper(url=self.URL, headless=headless, rerun=rerun, user=user)
        # If there is nothing the scrape, then escape
        warning = self.scraper.region_scraper() 
        if warning is not None:
            self.textBrowser_Descript.setText(warning)
            self.scraper.web_close()
            return
        
        self.textBox_descript_append(self.scraper.time_req())
        # DELETE COMMENTS HERE, THEY ARE FOR REFERENCE
        # color.BOLD + 'Hello, World!' + color.END
        # text = 'Press ' + color_app('CONTINUE','CYAN', 'UNDERLINE') + 'button or else choose a new query'
        text = 'Press the CONTINUE button or else choose a new query'
        self.textBox_descript_append(text)
        self.pushButton_Continue.setEnabled(True)
        
    def web_continue(self):
        # Doc_save count
        if self.pushButton_PartialSave_None.isChecked():
            saveRate = None
        else: 
            try: #turn to integer if possible
                saveRate = int(self.plainTextEdit_PartialSave_DocCount.toPlainText())
            except:
                saveRate = None
        self.scraper.doc_scraper(saveRate=saveRate)
        self.textBox_descript_append('Completed scraping. Check the terminal for more info\n\n\n')
        self.pushButton_Continue.setEnabled(False)
        return

# change text color within Python
# taken from Bacara at https://stackoverflow.com/questions/8924173/how-can-i-print-bold-text-in-python
class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

def color_app(string, *args):
    text = string
    for i in args:
        i = i.upper()
        try:
            text = getattr(color, i) + text
        except:
            continue
    text += color.END
    return text

# get path to images
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# execute and update the GUI window
def main():
    app = QApplication(sys.argv)
    main = MainWindow()
    app.setWindowIcon(QIcon(resource_path("Resources/favicon.icns")))
    main.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

