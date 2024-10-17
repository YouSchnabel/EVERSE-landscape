"""Read info from survey export and make useable"""

import pandas as pd
import json

mapperfile = "../data/survey_transform.json"

idmapping = {}

class DataSet:
    def __init__(self, filepath):
        self.metadata = {}
        self.data = pd.DataFrame()

        self._read_xls(filepath)
        self._preprocess()

    def _read_xls(self, filepath):
        #Reading the survey results from the export from EU survey
        self.data = pd.read_excel(filepath, header = 3)
        
    def _preprocess(self):
        # Extracting metadata from the survey file
        
        # First, identify all questions and relations
        questions = {}
        
        for colname in self.data.columns:
            nicename = colname.replace("applicable:", "applicable ")
            subtexts = nicename.split(":")
            questionid = False
            for qid in questions:
                if questions[qid]["question"] == subtexts[0]:
                    questionid = qid
            if not questionid:
                if len(subtexts) == 1:
                    subtexts[0] = colname
                questions.setdefault("A"+str(len(questions)), {
                    "question": subtexts[0], 
                    "subtexts": [], 
                    "colnames": [], 
                    "entrytype": "undefined",
                    "params": {}
                })
                qid = "A"+str(len(questions)-1)
            if len(subtexts)>1:
                questions[qid]["subtexts"].append(subtexts[1:len(subtexts)])
                questions[qid]["colnames"].append(colname)
        self.metadata = questions

        # Then, preprocess
        for qid in self.metadata:
            if len(self.metadata[qid]["subtexts"]) == 0:
                uniqueanswers = self.data[self.metadata[qid]["question"]].unique()
                answers = [x for x in uniqueanswers if pd.notna(x)]

                # Try to decide which entry type it is
                if len(answers) == 0:
                    self.metadata[qid]["entrytype"] = "no answers"
                elif type(answers[0]) is str:
                    self.metadata[qid]["entrytype"] = "textlist"

            else:
                uniqueanswers = self.data[self.metadata[qid]["colnames"][0]].unique()
                answers = [x for x in uniqueanswers if pd.notna(x)]
                if len(answers) == 0:
                    self.metadata[qid]["entrytype"] = "no answers"
                elif str(answers[0]).find("/5")>0 or str(answers[0]).find("/10")>0:
                    self.metadata[qid]["entrytype"] = "rating"

            # Get the ID of the question from the header
            '''
            colid = colname[colname.rfind("(")+1:-1]
            questionid = colid.split("_")[0]

            subtexts = colname.split(":")
            if len(subtexts)>2:
                subtexts = subtexts[1][-3:-1]
                if not subtexts[0] in idmapping:
                    idmapping.setdefault(subtexts[0], "A"+str(len(idmapping)))
                questionid = idmapping[subtexts[0]]
            else:
                subtexts = []
            '''
            # figure out which entry type it is
            

            # cluster
            
            # Get all answer options
        '''
            uniqueanswers = self.data[colname].unique()
            answers = [x for x in uniqueanswers if pd.notna(x)]

            # Try to decide which entry type it is
            if len(answers) == 0:
                entrytype = "no answers"
            elif str(answers[0]).find(")")>0:
                entrytype = "select"
            elif len(str(answers[0]))<6 and str(answers[0]).find("/")>0:
                entrytype = "rating"
            elif all(len(str(item)) == answers[0] for item in answers):
                entrytype = "ranking"
            else:
                entrytype = "text" 

            columninfo = {
                "subids": colid.split("_"),
                "text": colname[0:colname.rfind("(")-1],
                "subtexts": subtexts,
                "type": entrytype,
                "answers": self._get_answers_metadata(answers, entrytype)
            }

            questions.setdefault(questionid, [])
            questions[questionid].append(columninfo)
        self.metadata.setdefault("questions", questions)'''

    def list_questions(self):
        # Returns list of identifiers and questions in the form ID - question (type)
        for key in self.metadata:
            print (key, "-", self.metadata[key]["question"], "("+self.metadata[key]["entrytype"]+")")    

    @staticmethod
    def _get_answers_metadata(uniqueanswers, columntype):
        # Adjusting entries for better evaluation
        if len(uniqueanswers) > 10 and columntype == "text":
            entrymeta = {"type": "individual", "enum": []}
        elif columntype == "ranking":
            print ("ranking:", uniqueanswers)
        elif columntype == "rating":
            print ("RATE:", uniqueanswers)
            entrymeta = {"type": "rate", "total": float(uniqueanswers[0].split("/")[1])}
        else:
            entrymeta = {}
        return entrymeta