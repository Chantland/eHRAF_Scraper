# eHRAF_Scraper


Autonomous scraper of eHRAF webpage. More information cen be currently found within the Jupyter notebook but 
in short the scraper takes a advance search URL such as [https://ehrafworldcultures.yale.edu/search?q=text%3AApple&fq=culture_level_samples%7CPSF](https://ehrafworldcultures.yale.edu/search?q=text%3AApple&fq=culture_level_samples%7CPSF)
and runs through each of the document passages, obtaining OCM's, passage texts, year made, culture, region, and sub-region. Save them all to a data file in Data/.

The current Scraper you should consider using if you do not know what you are doing is eHRAF_Scraper.ipynb in a jupyter notebook, however, this will not be updated as time goes on and may become unrelaible. regardless, it explains in more detail the project and what is occurring. Otherwise use eHRAF_Scraper.py

To use the eHRAF_Scraper.py, consider using main_demo.py which has preset commented out demos to try.


## Scraper inputs:
url =         <string: eHRAF URL>
user =        <string: your name>
rerun =       <bool: disregard any previously ran files (TRUE) or try to start from last crashed (FALSE)>
headless =    <bool: do not show the scraped chrome browser (TRUE) or show the scraped Chrome Browser (FALSE)>




## Packages requirements

If you are loading this for the first time (AND THE VENV IS MISSING), you will need the packages used in the file. The best way is to use a virtual environment or use anaconda (which might save on space but some package may not be available through there). For a virtual environment (venv) type into the terminal:

        python - m venv venv
        
When venv is created, select it as your prefered kernal (in VS code, it should give you a prompt to do so, otherwise, select it in the to right corner). Then create a new terminal (should be able to do so at the top of the mac screen under "terminal"). Each line in your terminal should start with "venv" or whatever you named the environment if you called it something else. Now you can install the requirments in the terminal using:

        pip install -r requirements.txt -v
        
NOTE: It is likely the requirements file is bloated with packages you do not need. I have not tried to slim it down so feel free to just install packages as you see fit with

        pip install <your package name>