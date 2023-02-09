# for installing the GUI (if you want to make changes) use the py installer prompt: 
# pyinstaller  --onefile --add-data 'Resources:Resources'  --icon=Resources/favicon.icns Scraper_GUI.py
# Note that to make this an app also use --windowed


# DONE: Cannot run two subsequent runs of the scraper without it crashing. Perhaps due to issues with initializing and deleting the driver.
# DONE: check scraper for crashes. There is one which I thought was fixed but maybe not. It happens when the initial source tabs are clicked but cannot load yet seem to not initialize the reclick feature. Currently the error will save a partial file.
# DONE: fix scraper info which returns the number of rows of the excel file rather than the number of passages.
# DONE: initialize the options for headless and rerun
# DONE: standardize the save files so that similar search terms (pear, grandma vs. grandma, pear) are regarded as the same.
# DONE: implement "enter name" feature. This is easy to implement but hard to look nice without crowding.
# DONE: implement better looking continue button which is unclicakble until the right time
# TODO: (OPTIONAL) implement a stop button
# DONE: (basically) make the terminal print out to the GUI's terminal.
# TODO: (potentially) Add more filters that eHRAF already allows.
# DONE: Add passage page number columns to the excel files - eHRAF_Scraper.py
# DONE: Have excel files include passage numbers - eHRAF_Scraper.py
# DONE: Allow for extra advanced search culture and keywords queries where a second set of culture and keywords can be searched
# DONE: Create an option for the list of culture's passage counts to be outputted in GUI terminal - eHRAF_Scraper.py and Scraper_GUI.py
# DONE: Reorganize the passage count output so that it proceeds to the next line if overflow occurs - eHRAF_Scraper.py
# DONE: create "section" column that extracts the section part of the document title - eHRAF_Scraper.py
# DONE: Create an option for individual culture files to be created.
# DONE: Fix problem where if you try to do cultural count on a folder whose _altogether_dataset does not match the number of cultural files, extra rows will be created
# DONE: Make time estimates more accurate by giving large scrapings a log scale
# RJCT: (REJECTED) remove the years after some author's names
# RJCT: (REJECTED) clean the page info as it is all over the place (sometimes roman numerals, sometimes this format "[p.156]", this format "-156-", or sometimes just "156")
# DONE: Install app so dependancies are included automatically
# TODO: Initiate app instead of exe so that no terminal is outputted and the image of the file is an icon
# TODO: (Potentially) make exe be represented as an icon
# DONE: Integrate scraper run failure within the GUI terminal allowing for almost all information to be accessed outside the OS terminal. Also, stop the GUI from crashing when the Scraper crashes
# DONE: Fix for upon repeated use, the browser font can be turned blue
# DONE: Implement file saving which can be more concise should the file be too big.
# DONE: filter cultural inputs for accented characters




import sys
import os
from URL_Generator import URL_Generator as ug
import re
from eHRAF_Scraper import Scraper

import PyQt6
from PyQt6 import uic, QtTest
from PyQt6.QtCore import (QSize, QCoreApplication)
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox, 
    QMainWindow)
from PyQt6.QtGui import QIcon, QColor


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
    def load_ui(self): #for loading UI. This used to have more code but then it was moved
        uic.loadUi(resource_path("Resources/eHRAF_Scraper_Creator/form.ui"), self)

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

        self.buttonGroup_ExtraClause.setId(self.pushButton_ExtraClause_Not, 0)
        self.buttonGroup_ExtraClause.setId(self.pushButton_ExtraClause_Or, 1)
        self.buttonGroup_ExtraClause.setId(self.pushButton_ExtraClause_And, 2)

        self.buttonGroup_ExtraClause_Subject.setId(self.pushButton_ExtraClause_SubNone, 0)
        self.buttonGroup_ExtraClause_Subject.setId(self.pushButton_ExtraClause_SubAny, 1)
        self.buttonGroup_ExtraClause_Subject.setId(self.pushButton_ExtraClause_SubAll, 2)

        self.buttonGroup_ExtraClause_Keyword.setId(self.pushButton_ExtraClause_KeyNone, 0)
        self.buttonGroup_ExtraClause_Keyword.setId(self.pushButton_ExtraClause_KeyAny, 1)
        self.buttonGroup_ExtraClause_Keyword.setId(self.pushButton_ExtraClause_KeyAll, 2)

        self.buttonGroup_ExtraClause_SubjKey_Conj.setId(self.pushButton_ExtraClause_SubKeyOr, 1)
        self.buttonGroup_ExtraClause_SubjKey_Conj.setId(self.pushButton_ExtraClause_SubKeyAnd, 2)       

        # set up tab size (reset from the UI)
        self.tabWidget.setFixedWidth(571) # set default tab length

        # set visibility of extra tab to start out as hidden
        self.groupBox_ExtraClause.setVisible(False)
        self.groupBox_ExtraClause_Buttons.setVisible(False)

        # set visibility of the region filter box
        self.groupBox_Region.setVisible(False)
        # save the regional names to reduce repeat down below.
        self.regionName_list = []
        self.set_region() #set the region at the start
    
    def widgit_hub(self):
        # set up the submit buttons to listen for clicks
        self.pushButton_URLSubmit.clicked.connect(self.set_URL)
        self.pushButton_AdvSubmit.clicked.connect(self.create_URL)
        # continue on when user is ready
        self.pushButton_Continue.clicked.connect(self.web_continue)

        # turn the sub buttons for the "Display number of passages per culture" option on or off
        self.radioButton_DisplayPassages_YES.toggled.connect(self.DisplayNumReveal)

        # reveal additional search clause
        self.checkBox_ExtraClause.toggled.connect(self.ShowExtraClause)

        # Filter tab
        # change size
        self.tabWidget.currentChanged.connect(self.FilterTab_Changed)
        # change region
        self.comboBox_RegionSelection.currentIndexChanged.connect(self.set_region)
        
    def FilterTab_Changed(self, index):
        # change size of textbox to allow filters only if it is not already changed
        if self.tabWidget.tabText(index) == "Filters":
            self.groupBox_Region.setVisible(True)
            if not self.checkBox_ExtraClause.isChecked():
                self.textBrowser_Descript.setGeometry(600, 20, 261, 531-325) #flip text box
        else:
            self.groupBox_Region.setVisible(False)
            if not self.checkBox_ExtraClause.isChecked():
                self.textBrowser_Descript.setGeometry(600, 20, 261, 531) # text box     
    
    def set_region(self):
        # set the region box to the same as the selected drop down tab
        self.stackedWidget_Region.setCurrentIndex(self.comboBox_RegionSelection.currentIndex())
        #select the hypothetical all button
        self.allButton = self.stackedWidget_Region.currentWidget().children()[0].children()[-1]
        if self.allButton.text() != "ALL": #if not where we think it is, cycle until we find it.
            for button in self.allButton.parent().children():
                if button.text() == "ALL":
                    self.allButton = button
                    break
            else:
                raise Exception("Error, no Filter ALL button has been found")
        # only add the regionName if it has not been added before (you could probably just inialize all the "ALL" at the start and it would work too)
        if self.comboBox_RegionSelection.currentText() not in self.regionName_list:
            self.allButton.toggled.connect(self.click_allRegion) #set listening
            self.regionName_list.append(self.comboBox_RegionSelection.currentText())
        
    def click_allRegion(self):
        # set checked for all the buttons if it is checked, otherwise turn it off
        for index, button in enumerate(self.allButton.parent().children()):
            if isinstance(button, QCheckBox) and button.text() != "ALL":
                if self.allButton.isChecked():
                    self.allButton.parent().children()[index].setChecked(True)
                else:
                    self.allButton.parent().children()[index].setChecked(False)

    # def textBrowser_Descript(self, string:str): #update the description box
    #     self.descript += string + "\n\n"
    #     self.textBrowser_Descript.setText(self.descript)
    def textBox_URL_set(self): #update the URL box
        self.textBrowser_URL.setText(self.URL)

    def textBox_warning(self, warning:str, crash:bool=False): #give warning flag if user does something wrong
        self.text_clear()
        # if the scraper crashed, give a failure warning and close the webpage unless it is not already closed
        if crash:
            self.textBrowser_Descript.append("<font color='red'><b>THE SCRAPER HAS CRASHED</b></font><br>")
            self.textBrowser_Descript.setTextColor(QColor("black")) #put in to make sure this stays as black as for an unknown reason the text can become blue
            try:
                self.scraper.web_close()
            except:
                pass
        # Add text warning
        self.textBrowser_Descript.append(f'{warning}\n')
        self.pushButton_Continue.setEnabled(False)
    
    def text_clear(self): #clear both boxes of text
        self.descript = ''
        self.textBrowser_Descript.setText('')
        self.textBrowser_URL.setText('')
    
    def DisplayNumReveal(self): #reveal or hide the extra buttons for the display passages option
        # if Yes is checked, then reveal the buttons, otherwise hide the buttons
        if  self.radioButton_DisplayPassages_YES.isChecked():
            self.pushButton_DisplayPassages_Culture.setEnabled(True)
            self.pushButton_DisplayPassages_Count.setEnabled(True)
        else:
            self.pushButton_DisplayPassages_Culture.setEnabled(False)
            self.pushButton_DisplayPassages_Count.setEnabled(False)
    
    def ShowExtraClause(self):
        # if toggled to true, display extra clause, otherwise revert back to original
        if self.checkBox_ExtraClause.isChecked():
            # set visibility
            self.groupBox_ExtraClause.setVisible(True)
            self.groupBox_ExtraClause_Buttons.setVisible(True)

            # set increased size
            self.setFixedSize(QSize(1180, 780)) #window
            self.textBrowser_Descript.setGeometry(600, 20+20, 261+300, 531-345) #flip text box
            self.tabWidget.setFixedWidth(self.tabWidget.width()+580) # set enlarged tab width
            self.textBrowser_URL.setFixedWidth(self.textBrowser_URL.width()+300) #URL box
            self.pushButton_Continue.setGeometry(self.pushButton_Continue.x()+145,\
                self.pushButton_Continue.y(),self.pushButton_Continue.width(),self.pushButton_Continue.height())  # move the continue button (I couldn't find how to just move the X without changing the width)
        else:
            # set visibility
            self.groupBox_ExtraClause.setVisible(False)
            self.groupBox_ExtraClause_Buttons.setVisible(False)

            # reset to default size:
            self.setFixedSize(QSize(880, 780)) #window
            self.textBrowser_Descript.setGeometry(600, 20, 261, 531) # text box
            self.tabWidget.setFixedWidth(self.tabWidget.width()-580) #tab
            self.textBrowser_URL.setFixedWidth(self.textBrowser_URL.width()-300) #URL box
            self.pushButton_Continue.setGeometry(self.pushButton_Continue.x()-145,\
                self.pushButton_Continue.y(),self.pushButton_Continue.width(),self.pushButton_Continue.height())  # reset the continue button (I couldn't find how to just move the X without changing the width)
    
    def getFiltersClicked(self, filter):
        # if one or more of the filters are checked, append it to the list
        filter_list = []
        for i in range(len(filter.buttons())):
            if filter.buttons()[i].isChecked():
                filter_list.append(filter.buttons()[i].text())
        return filter_list
    def set_URL(self): #if URL submit button is clicked, just use that URL but first check if it is valid
        URL = self.plainTextEdit_URL.toPlainText()
        if URL == '':
            self.textBox_warning("No URL submitted")
            return
        regex_search = re.search(r'Run URL: ', URL)
        if regex_search is not None:
            URL = re.sub(r'Run URL: ', '', URL)
        regex_search = re.match(r'^https://ehrafworldcultures.yale.edu/search', URL)
        if not regex_search:    
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
        # only include the clause arguments if the box is currently clicked. Otherwise use default
        if self.checkBox_ExtraClause.isChecked():
            exClause_conj = self.buttonGroup_ExtraClause.id(self.buttonGroup_ExtraClause.checkedButton())
            exClause_subjects = self.plainTextEdit_ExtraClause_Subject.toPlainText()
            exClause_subjects_conj = self.buttonGroup_ExtraClause_Subject.id(self.buttonGroup_ExtraClause_Subject.checkedButton())
            exClause_concat_conj = self.buttonGroup_ExtraClause_SubjKey_Conj.id(self.buttonGroup_ExtraClause_SubjKey_Conj.checkedButton())
            exClause_keywords = self.plainTextEdit_ExtraClause_Keyword.toPlainText()
            exClause_keywords_conj = self.buttonGroup_ExtraClause_Keyword.id(self.buttonGroup_ExtraClause_Keyword.checkedButton())
        else:
            exClause_conj = 1
            exClause_subjects = ''
            exClause_subjects_conj = 1
            exClause_concat_conj = 1
            exClause_keywords = ''
            exClause_keywords_conj = 1


        # check to make sure a search term was provided
        if cultures == '' and subjects == '' and keywords == '' and exClause_subjects == '' and exClause_keywords == '':
            self.textBox_warning("No search terms provided, please add then submit again.")
            return
        filter_dict = {"culture_level_samples":self.getFiltersClicked(self.buttonGroup_Filter_CulturalLevel),
                       "document_level_samples":self.getFiltersClicked(self.buttonGroup_Filter_DocumentLevel),
                       "document_types":self.getFiltersClicked(self.buttonGroup_Filter_DocumentTypes),
                       "subsistence_types":self.getFiltersClicked(self.buttonGroup_Filter_SubsistenceTypes),
                       "series":self.getFiltersClicked(self.buttonGroup_Filter_Series),
                       "published_date":self.getFiltersClicked(self.buttonGroup_Filter_PublishedDate), 
                       "subregions":self.getFiltersClicked(self.buttonGroup_Filter_Regions)}

        URL_gen = ug()
        URL = URL_gen.URL_generator(cultures=cultures,
                            cult_conj=cult_conj,
                            subjects=subjects,
                            subjects_conj=subjects_conj,
                            concat_conj= concat_conj,
                            keywords= keywords,
                            keywords_conj= keywords_conj,
                            exClause_conj = exClause_conj,
                            exClause_subjects = exClause_subjects,
                            exClause_subjects_conj = exClause_subjects_conj,
                            exClause_concat_conj = exClause_concat_conj,
                            exClause_keywords = exClause_keywords,
                            exClause_keywords_conj = exClause_keywords_conj,
                            cultural_level_samples= filter_dict["culture_level_samples"])
        if URL == '':
            self.textBox_warning("No viable search terms were found, please check for spelling mistakes")
            return
        self.URL = URL
        self.text_clear() #if success, clear out the windows
        self.textBrowser_Descript.append(f'{URL_gen.invalid_inputs()}\n') #Add invalid inputs and scraper count
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

        # if "save seaparte culture files" is marked "YES" then save separate cultural files
        if self.radioButton_CultureIndividualFiles_YES.isChecked():
            cultureFiles = True
        else:
            cultureFiles = False

        # initialize the scraper
        try:
            self.scraper = Scraper(url=self.URL, headless=headless, rerun=rerun, user=user, cultureFiles=cultureFiles)
            # Run the region scraper. If there is nothing the scrape, then escape
            warning = self.scraper.region_scraper() 
            if warning is not None:
                self.textBox_warning(warning)
                self.textBrowser_URL.setText(self.URL)
                self.scraper.web_close()
                return
        except:
            self.textBox_warning(warning="Unable to load the initial webpage properly, please try resubmitting", failure=True)
            return
        
        # If the file name is too long, give a warning.
        if self.scraper.file_length_warning is not None:
            self.textBrowser_Descript.append(f"<font color='red'>{self.scraper.file_length_warning}<font><br>")



        # Display time required to Scrape
        self.textBrowser_Descript.append(f'{self.scraper.time_req()}\n')

        # Display (optionally) all the cultures and passage counts
        if self.radioButton_DisplayPassages_YES.isChecked():
            # -2 = culture, -3 equals "count"
            if self.buttonGroup_Options_DisplayPassages_CoC.id(self.buttonGroup_Options_DisplayPassages_CoC.checkedButton()) == -2:
                cultureCount = "culture"
            elif self.buttonGroup_Options_DisplayPassages_CoC.id(self.buttonGroup_Options_DisplayPassages_CoC.checkedButton()) == -3:
                cultureCount = "count"
            else:
                raise Exception("No value button number returned for buttonGroup_Options_DisplayPassages_CoC.id")
            self.textBrowser_Descript.append(f'{self.scraper.cult_count(by=cultureCount)}\n')
        # DELETE COMMENTS HERE, THEY ARE FOR REFERENCE
        # color.BOLD + 'Hello, World!' + color.END
        # text = 'Press ' + color_app('CONTINUE','CYAN', 'UNDERLINE') + 'button or else choose a new query'

        # If there is a matching query, output info
        if self.scraper.querySkipper:
            self.textBrowser_Descript.append("File with the same search query found, skipping successfully scraped cultures\n")
            # also give a warning if you might be overwriting the wrong long file.
            if self.scraper.file_length_warning is not None:
                self.textBrowser_Descript.append("<font color='red'>WARNING, due to the shortening of the file name, your query could be mistaken for another. Check the current _Altogether_Dataset.xlsx to be sure.<font><br>")



        self.textBrowser_Descript.append("<br><font color='blue'>Press the <b>CONTINUE</b> button or else choose a new query</font><br><br>")
        self.pushButton_Continue.setEnabled(True)
        
    def web_continue(self):
        # Routine partial saving initialization. If checked, have no partial saving, else set the partial saving to what user specified (or default)
        if self.pushButton_PartialSave_None.isChecked():
            saveRate = None
        else: 
            try: #turn to integer if possible
                saveRate = int(self.plainTextEdit_PartialSave_DocCount.toPlainText())
            except:
                saveRate = None
        if self.scraper.querySkipper:
            pas_count_total = self.scraper.partial_file_return()[1]
            self.textBrowser_Descript.append(f'{pas_count_total} passages loaded from partial file\n')
            QCoreApplication.processEvents() #process the events then wait so that the text can be loaded. Likely it may be good to use Qthreads instead
            QtTest.QTest.qWait(100)
        QCoreApplication.processEvents()
        # run the actual scraping. if it should fail, output the reason
        try:
            self.scraper.doc_scraper(saveRate=saveRate)
        except:
            # if known failure occurred, print out, otherwise give unknown
            try:
                self.textBox_warning(self.scraper.fail_text, crash=True)
                self.textBrowser_Descript.append(f'{self.scraper.exception_text}\n')
            except:
                self.textBox_warning("Unknown failure has occurred", crash=True)
            return
        self.textBrowser_Descript.append(f'Completed scraping. File saved to:\n{self.scraper.folder_path}\n')
        self.pushButton_Continue.setEnabled(False)
        self.textBrowser_Descript.setTextColor(QColor("black")) #put in to make sure this stays as black as for an unknown reason the text can become blue
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

# get path to folder
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))

    return os.path.join(base_path, relative_path)

# execute and update the GUI window
def main():
    app = QApplication(sys.argv)
    main = MainWindow()
    app.setWindowIcon(QIcon(resource_path("Resources/favicon.ico")))
    main.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

