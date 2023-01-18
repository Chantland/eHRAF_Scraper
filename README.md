# eHRAF_Scraper

To use this Scraper, please click on Scraper_GUI and follow GUI_Instructions.docx 



Autonomous scraper of eHRAF webpage that through URL_generator.py can mimic the search parameters in eHRAF and through eHRAF_Scraper.py can extract document information from the website, systematically scraping each culture's defined documents.
In short the scraper takes a advance search URL such as [https://ehrafworldcultures.yale.edu/search?q=text%3AApple&fq=culture_level_samples%7CPSF](https://ehrafworldcultures.yale.edu/search?q=text%3AApple&fq=culture_level_samples%7CPSF)
and runs through each of the document passages, obtaining OCM's, passage texts, year made, culture, region, and sub-region. Save them all to a data file in Data/.

Currently, you should run the Scraper_GUI as this is the most up to date and friendly version of the scraper. If you wish to run the other applications THEY MUST BE OUTSIDE OF THE "Build" FOLDER. the "Build" folder was used to help to declutter but is not where the build files should actually be localized (as to build the GUI they need to be in the same place that the GUI will be ran)

Scraper_GUI (the executable) must be ran on a mac (currently) and must have the subfolder "resources" in its path. Do not change any file within resources.




To use the eHRAF_Scraper.py, consider using main_demo.py which has preset commented out demos to try.

## eHRAF_Scraper initial inputs:
url =         <string: eHRAF URL>
user =        <string: your name>
rerun =       <bool: disregard any previously ran files (TRUE) or try to start from last crashed (FALSE)>
headless =    <bool: do not show the scraped chrome browser (TRUE) or show the scraped Chrome Browser (FALSE)>

## Doc_Scraper inputs:
saveRate =    <int: iteration of files scraped before a routine "safety save" occurs>



## Packages requirements

If you are loading this for the first time (AND THE VENV IS MISSING), you will need the packages used in the file. The best way is to use a virtual environment or use anaconda (which might save on space but some package may not be available through there). For a virtual environment (venv) type into the terminal:

        python - m venv venv
        
When venv is created, select it as your preferred kernal (in VS code, it should give you a prompt to do so, otherwise, select it in the to right corner). Then create a new terminal (should be able to do so at the top of the mac screen under "terminal"). Each line in your terminal should start with "venv" or whatever you named the environment if you called it something else. Now you can install the requirments in the terminal using:

        pip install -r requirements.txt -v
        
NOTE: It is likely the requirements file is bloated with packages you do not need. I have not tried to slim it down so feel free to just install packages as you see fit with

        pip install <your package name>


## Installing