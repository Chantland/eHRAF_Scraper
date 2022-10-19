import csv
import nltk
import pandas as pd


columns = []
rows = []

def create_rows(rows):
    with open('test.csv', newline='') as csvfile:
        #change <'Downloads/test.csv'> to the working directory of the csv file
        #change <testculture> to desired name of the culture
        testculture = csv.reader(csvfile, delimiter=',', quotechar='"')
        columns = next(testculture) #extracting column names
        for row in testculture:
            rows.append(row) #extracting all the rows


rows_original = []
create_rows(rows)
#create_rows(rows_original)