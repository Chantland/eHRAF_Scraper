# URL generator
import re

# cultures = input("Give cultures")
# cult_and =  input("include any, all, none for cultures")
# subjects = input("Give Subjects separated by a comma")
# subjects_and = input("include any, all, none for subjects")
# concat_and = input("either or for cultures and subjects")
# keywords = input("Give keyword text separated by a comma")
# keywords_and = input("include any, all, none for subjects")

# preset
cultures = "Mao"
cult_and =  2
subjects = "spirits and gods, joiks,poppyness"
subjects_and = 1
concat_and = 1
keywords = "apple, pear"
keywords_and = 0


# 0 None
# 1 any
# 2 all
cultures_present = False
subjects_present = False
keywords_present = False

# sanitize the text input
def word_strip(string:str):
    string_list = [x.strip() for x in string.split(",")]
    return string_list

if cultures is not None:
    culture_list = word_strip(cultures)

if subjects is not None:
    subjects_list = word_strip(subjects)




