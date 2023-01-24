# eHRAF_Scraper

To use this Scraper, please click on Scraper_GUI and follow GUI_Instructions.docx 
Note that currently there is only a MAC version of the GUI application. If you want Windows or Linux, consider installing it on your desired Machine.


Autonomous scraper of eHRAF webpage that through URL_generator.py can mimic the search parameters in eHRAF and through eHRAF_Scraper.py can extract document information from the website, systematically scraping each culture's defined documents.
In short the scraper takes an Advance Search URL such as [https://ehrafworldcultures.yale.edu/search?q=text%3AApple&fq=culture_level_samples%7CPSF](https://ehrafworldcultures.yale.edu/search?q=text%3AApple&fq=culture_level_samples%7CPSF)
and runs through each of the document passages, obtaining OCM's, passage texts, year made, culture, region, and sub-region. At completion, this saves all packages extracted to a data file in Data/.

Currently, you should run the Scraper_GUI as this is the most up to date and friendly version of the scraper. If you wish to run the other applications THEY MUST BE OUTSIDE OF THE "Build" FOLDER. the "Build" folder was used to help to declutter but is not where the build files should actually be localized (as to build the GUI they need to be in the same place that the GUI will be ran)

Scraper_GUI (the executable) must be ran on a mac (currently) and must have the subfolder "resources" in its path. Do not change any file within resources.




To use the eHRAF_Scraper.py, consider using main_demo.py which has preset commented out demos to try.

## eHRAF_Scraper.py 
Autonomous scraper which takes in a url input and scrapes eHRAF. Outputs and saves excel file(s).
### Initial inputs:
        url =                   <string: eHRAF URL>
        user =                  <string: your name>
        rerun =                 <bool: disregard any previously ran files (TRUE) or try to start from last crashed (FALSE)>
        headless =              <bool: do not show the scraped chrome browser (TRUE) or show the scraped Chrome Browser (FALSE)>
        cultureFiles =          <bool: create separate files for each culture scraped>
	
### Doc_Scraper function inputs:
        saveRate =              <int: iteration of files scraped before a routine "safety save" occurs>

## URL_Generator.py
Extract a URL based on Advanced Search which is able to be inputted into the URL of eHRAF_Scraper.py. Include the following optional inputs. Note that all string defaults are ‘’ while all int defaults are 1:
### Initial inputs
        none
### URL_generator function inputs
	cultures =              <string: Culture names separated by a comma>
        cult_conj =             <int: Decide how the cultures will be included using values 0 for none or 1 for any/OR >
        subjects =              <string: Subject names and/or OCM numbers separated by a comma>
        subjects_conj =         <int: Decide how the Subjects will be included using values 0 for none, 1 for any/OR, or  2 for all/AND >
        concat_conj =           <int: Decide how the subjects and keyword search terms will be paired. Would you like either the subjects OR (Value 1) the keywords to be searched or would you like both (Value 2)>
        keywords =              <string: Lexical search keywords separated by a comma>
        keywords_conj =         <int: Decide how the Keywords will be included using values 0 for none, 1 for any/OR, or  2 for all/AND >
        cultural_level_samples =<list: include a list of “Cultural Level Sample” strings like “PSF”, “EA”, SCCS”, and/or “SRS”>
### 

## Packages requirements

If you are loading this for the first time (AND THE VENV IS MISSING), you will need the packages used in the file. The best way is to use a virtual environment or use anaconda (which might save on space but some package may not be available through there). For a virtual environment (venv) type into the terminal:

        python - m venv venv
        
When venv is created, select it as your preferred kernal (in VS code, it should give you a prompt to do so, otherwise, select it in the to right corner). Then create a new terminal (should be able to do so at the top of the mac screen under "terminal"). Each line in your terminal should start with "venv" or whatever you named the environment if you called it something else. Now you can install the requirements in the terminal using:

        pip install -r requirements.txt -v
        
NOTE: In some circumstances packages may be missed. To manually add packages, consider using:

        pip install <your package name>


## Installing
If you would like to reinstall the GUI for whatever reason, the files URL_generator.py, Scraper_GUI.py, and eHRAF_Scraper.py MUST be in the main folder outside of "Build". This is where the Scraper_GUI is located. You may install the application through PYinstaller using this prompt: 

        'Resources/favicon.icns:.' --add-data 'Resources/eHRAF_Scraper_Creator:eHRAF_Scraper_Creator'  --icon=Resources/favicon.icns Scraper_GUI.py

You may need to change the file's icon manually if it does not set.
