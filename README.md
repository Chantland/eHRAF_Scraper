# eHRAF_Scraper

Autonomous scraper of eHRAF webpage. More information cen be currently found within the Jupyter notebook but 
in short the scraper takes a advance search URL such as [https://ehrafworldcultures.yale.edu/search?q=text%3AApple&fq=culture_level_samples%7CPSF](https://ehrafworldcultures.yale.edu/search?q=text%3AApple&fq=culture_level_samples%7CPSF)
and runs through each of the document passages, obtaining OCM's, passage texts, year made, culture, region, and sub-region. Save them all to a data file in Data/
