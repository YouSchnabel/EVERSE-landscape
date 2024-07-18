"""Read info from survey export and make useable"""

import pandas as pd
import json

class DataSet:
    def __init__(self, filepath):
        self.metadata = {}
        self.data = pd.DataFrame()

        self._read_xls(filepath)

    def _read_xls(self, filepath):
        #Reading the survey results from the export from EU survey
        self.data = pd.read_excel(filepath, header = 3)
        
    def _preprocess(self):
        # Extracting metadata from the survey file
        questions = {}
        
        for colname in self.data.columns:
            # Get the ID of the question from the header
            colid = colname[colname.rfind("(")+1:-1]
            questionid = colid.split("_")[0]

            subtexts = colname.split(" : ")
            if len(subtexts)>2:
                subtexts = subtexts[-3:-1]
            else:
                subtexts = []
            
            # Get all answer options
            uniqueanswers = self.data[colname].unique()
            answers = [x for x in uniqueanswers if pd.notna(x)]

            # Try to decide which entry type it is
            if len(answers) == 0:
                entrytype = "no answers"
            elif answers[0].find(")")>0:
                entrytype = "select"
            elif len(answers[0])<6 and answers[0].find("/")>0:
                entrytype = "rating"
            elif all(len(item) == answers[0] for item in answers):
                entrytype = "ranking"
            else:
                entrytype = "text" 
            
            columninfo = {
                "subids": colid.split("_"),
                "text": colname[0:colname.rfind("(")-1],
                "subtexts": subtexts,
                "type": entrytype,
                "answers": self._get_answers_metadata(self.data[colname], entrytype)
            }
            
            questions.setdefault(questionid, [])
            questions[questionid].append(columninfo)
        self.metadata.setdefault("questions", questions)

    @staticmethod
    def _get_answers_metadata(column, columntype):
        # Adjusting entries or better evaluation
        entrymeta = {}
        return entrymeta