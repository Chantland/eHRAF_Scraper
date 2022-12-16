# URL generator
import re
import pandas as pd

# cultures = input("Give cultures")
# cult_and =  input("include any, all, none for cultures")
# subjects = input("Give Subjects separated by a comma")
# subjects_and = input("include any, all, none for subjects")
# concat_and = input("either or for cultures and subjects")
# keywords = input("Give keyword text separated by a comma")
# keywords_and = input("include any, all, none for subjects")


# preset
cultures = "Mao, AzAnde"
cult_conj =  2
subjects = "spirits and gods, joiks, 750, 9999, PoppYnESS"
subjects_conj = 1
concat_conj = 1
keywords = "apple, pear"
keywords_conj = 0

# url=r'https://ehrafworldcultures.yale.edu/search?q=text%3AApple&fq=culture_level_samples%7CPSF'

# 0 None
# 1 any
# 2 all
cultures_present = False
subjects_present = False
keywords_present = False


# sanitize the text input
def word_strip(string:str):
    string_list = [x.lower().strip() for x in string.split(",")]
    return string_list
# Number of different search
searchVar_count = 0

conj_list = ["  ", " OR ", " AND "]
Search_dict = {'culture': {'valid':set(), 'invalid':set(), 'phrase':''},
               'subject': {'valid':set(), 'invalid':set(), 'phrase':''},
               'keyword': {'valid':set(), 'invalid':set(), 'phrase':''},}
# create search phrase chunks which will be later combined and used for the URL
if cultures is not None:
    culture_list = word_strip(cultures)
    # Match cultures with the cultures that eHRAF uses
    df_Culture = pd.read_excel('Resources/Culture_Names.xlsx')
    for culture in culture_list:
        if culture in df_Culture['Culture'].unique():
            found_culture = df_Culture[df_Culture['Culture'].isin([culture])]
            Search_dict['culture']['valid'].add(found_culture['Culture'].values[0]) #could be one line but split to reduce confusion
        else:
            Search_dict['culture']['invalid'].add(str(culture))
    # create phrase for culture (will be combined with the rest and then turned in a URL
    if len(Search_dict['culture']['valid']) > 0:
        Search_dict['culture']['phrase'] += 'cultures:('
        multi_term = False
        for search_i in Search_dict['culture']['valid']:
            # Add a conjunction if there are more than 1 search terms
            if multi_term is True:
                Search_dict['culture']['phrase'] += conj_list[cult_conj]
            else:
                multi_term = True
            # if NONE is selected for cultures, add a -
            if cult_conj == 0:
                Search_dict['culture']['phrase'] += '-'
            Search_dict['culture']['phrase'] += '\"' + search_i + '\"'
        Search_dict['culture']['phrase'] += ')'


if subjects is not None:
    subjects_list = word_strip(subjects)
    # Match OCM codes with meanings and return back a list of ones that worked and ones that didn't
    df_OCM_Codes = pd.read_excel('Resources/OCM_Codes.xlsx')
    for subject in subjects_list:
        # turn OCMs into meanings, or search for if the meanings exist
        if subject.isnumeric():
            col = 'OCM'
            sub = int(subject)
        else:
            col = 'Meaning'
            sub = subject
        if sub in df_OCM_Codes[col].unique():
            meaning = df_OCM_Codes[df_OCM_Codes[col].isin([sub])]
            Search_dict['subject']['valid'].add(meaning['Meaning'].values[0]) #could be one line but split to reduce confusion
        else:
            Search_dict['subject']['invalid'].add(str(sub))
    if len(Search_dict['subject']['valid']) > 0:
        Search_dict['subject']['phrase'] += 'subjects:('
        multi_term = False
        for search_i in Search_dict['subject']['valid']:
            # Add a conjunction if there are more than 1 search terms
            if multi_term is True:
                Search_dict['subject']['phrase'] += conj_list[subjects_conj]
            else:
                multi_term = True
            # if NONE is selected for subject, add a -
            if subjects_conj == 0:
                Search_dict['subject']['phrase'] += '-'
            Search_dict['subject']['phrase'] += '\"' + search_i + '\"'
        Search_dict['subject']['phrase'] += ')'

if keywords is not None:
    keyword_list = word_strip(keywords)
    Search_dict['keyword']['valid'] = set(keyword_list)
    #At this point, I am not sure what would be an invalid keword.
    if len(Search_dict['keyword']['valid']) > 0:
        Search_dict['keyword']['phrase'] += 'keywords:('
        multi_term = False
        for search_i in Search_dict['keyword']['valid']:
            # Add a conjunction if there are more than 1 search terms
            if multi_term is True:
                Search_dict['keyword']['phrase'] += conj_list[keywords_conj]
            else:
                multi_term = True
            # if NONE is selected for subject, add a -
            if keywords_conj == 0:
                Search_dict['keyword']['phrase'] += '-'
            Search_dict['keyword']['phrase'] += '\"' + search_i + '\"'
        Search_dict['keyword']['phrase'] += ')'

final_phrase = ''
# if Search_dict['culture']['valid'] != '' and Search_dict['keyword']['valid'] != ''