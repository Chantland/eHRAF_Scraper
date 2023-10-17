# eHRAF_Scraper

To use this Scraper, please click on Scraper_GUI and follow GUI_Instructions.docx 
Note that currently there is only a MAC version of the GUI application. If you want Windows or Linux, consider installing it on your desired Machine (check installing below).


Autonomous scraper of eHRAF webpage that through URL_generator.py can mimic the search parameters in eHRAF and through eHRAF_Scraper.py can extract document information from the website, systematically scraping each culture's defined documents.
In short the scraper takes an Advance Search URL such as [https://ehrafworldcultures.yale.edu/search?q=text%3AApple&fq=culture_level_samples%7CPSF](https://ehrafworldcultures.yale.edu/search?q=text%3AApple&fq=culture_level_samples%7CPSF)
and runs through each of the document passages, obtaining OCM's, passage texts, year made, culture, region, and sub-region. At completion, this saves all packages extracted to a data file in Data/.

Currently, you should run the Scraper_GUI as this is the most up to date and friendly version of the scraper. If you wish to run the other applications THEY MUST BE OUTSIDE OF THE "Build" FOLDER. the "Build" folder was used to help to declutter but is not where the build files should actually be localized (as to build the GUI they need to be in the same place that the GUI will be ran)

Scraper_GUI (the executable) should be able to be ran anywhere regardless of its location. However, in the past it required to have the subfolder 'resources' in its path (like how it is on GitHub). If you see that the scraper crashes because it is missing certain files, this may be a solution. Running the scraper as a python file will always require the resources folder which is why you must take it out of the build folder should you choose to use that instead.




To use the eHRAF_Scraper.py, consider using main_demo.py which has preset commented out demos to try.

## eHRAF_Scraper.py 
Autonomous scraper which takes in a url input and scrapes eHRAF. Outputs and saves excel file(s). Again, this is all optional and it is recommended to use the Scraper_GUI executable instead.
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

If you are loading this for the first time (AND THE VENV IS MISSING), you will need the packages used in the file. The best way is to use a virtual environment or use anaconda (which might save on space but some package may not be available through there). For a virtual environment (venv) type into the terminal while within the folder of the scraper:

        python3 -m venv venv
        
When venv is created, select it as your preferred kernal (in VS code, it should give you a prompt to do so, otherwise, use `source /your/path/here/venv/bin/activate`). You may need to create a new terminal (should be able to do so with mac at the top under "terminal"). Each line in your terminal should start with "venv" or whatever you named the environment if you called it something else. Now you can install the requirements in the terminal using:

        pip install -r requirements.txt -v
        
NOTE: In some circumstances packages may be missed. To manually add packages, consider using:

        pip install <your package name>


## Installing
If you would like to reinstall the GUI for whatever reason, the files URL_generator.py, Scraper_GUI.py, and eHRAF_Scraper.py MUST be in the main folder outside of "Build". This is where the Scraper_GUI is located. You may install the application through PYinstaller using this prompt: 
        
        
        pyinstaller  --onefile --add-data 'Resources:Resources'  --icon=Resources/favicon.icns Scraper_GUI.py
        
Note that you must input this prompt in a terminal which currently has activated the virtual environment (venv) mentioned above. Usually activation is something like `source /path/to/your/venv/bin/activate`
        
        
You may need to change the file's icon manually if it does not set.



## Troubleshooting

**Partial saving** - If your scraping crashes for whatever reason (there are a lot of ways it can, this is somewhat unavoidable) it will usually save a partial file of your scraping before ending and giving an error message telling you some info of how it crashed. Sometimes, however, the crash is so severe that the scraper does not know what happened and is unable to save everything. A routine partial saving will still occur during the scraping (default is 5,000 passages but you can reduce this) so you will probably still get a partial file. If you do have a partial file (you usually will) just reenter the same scraping queries you had before and it will start off where the last save ended! It will tell you how many passages were loaded so make sure you see "partial saving loaded" to make sure you made entered in again the correct query. This also means that if you try to scrape something that already has been scraped before, it will NOT scrape any new passages unless eHRAF suddenly gets a new culture. 

**Overwriting unrelated scrapings** - The scraper is able to find scrapings by matching folder names with your queries. If your queries are complex, the folder name will be truncated as there are only so many characters that can be saved to a folder's name. This truncation can become and issue if you have two very long queries which look nearly identical but differ in small details found in the truncated section as the scraper may think the two queries are the same an treat them as such (like adding to the wrong partial file. Though rare, it is important to be cognizant of it. I the future we might make a simple text line allowing you to enter in your now optional file name.

**Chromium not found** - There are cases where the Chromium that is being loaded may not longer exist or be outdated. You may need to update the packages directly and reinstall the GUI using the above prompt or try "pyinstaller Scraper_GUI.spec" although this has not been corroborated. Future versions of the scraper may try to preinstall a chrome browser so it does not need to download each time yet this is a future project. 

**No active subscription** - eHRAF requires having an active subscription to access its files. When we, the authors, run the code, we do so using the university internet which has an active subscription allowing us to scrape merely by having valid internet credential. This can be an issue if you need to log in to supply your credentials as the scraper will not wait for you to do so. If neither you or your university/wifi have a subscription, you may be unable to use the scraper

**Long start up** - The GUI start-up sequence is slow and could take up to 5 minutes. This may be due to the scraper needing to download the chromium browser (this is something we want to eventually fix). 

**Crash from monitor size** - Because of the nature of web scraping, the website as well as your computer itself may affect its success. In the past, monitor window/browser size negatively affected what items could be scraped as eHRAF hides items if the window is too small. We have done workarounds to fix these problems on our end but we cannot test every monitor size especially small ones. If an issue, try using a larger monitor or manually stretch the window size within the code. 

**Changed website layout** - If eHRAF changes their website layout or design, there is no immediate fix to this and it will crash. This will eventually happen and this scraper will become unusable. Be warned, this is the nature of all scrapers.

