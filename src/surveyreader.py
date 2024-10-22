"""Read info from survey export and make useable"""

import pandas as pd
import json

class DataSet:
    def __init__(self, filepath):
        self.metadata = {}
        self.data = pd.DataFrame()

        self.read(filepath)
        self.preprocess()

    def read(self, filepath):
        """ Reading the survey results from the export from EU survey"""

        if filepath.find("xls")>-1:
            self.data = pd.read_excel(filepath, header = 3)
        elif filepath.find("h5")>-1:
            self.data = pd.read_hdf(filepath, key = "survey")

    def _anonymize(self, internaluse = False, outpath = ""):
        """Deleting entries with personal information. 
               If internaluse = True, keeping details on affiliation.
               If outpath is provided, anonymized dataset is written to xls."""

        if "Name" in self.data.columns:
            self.data = self.data.drop(columns=['Name', 'email', 'Invitation number', 
                                            'Contribution ID', 'User name', 'Languages'])

        if not internaluse and "Further description of your role or group" in self.data.columns:
            self.data = self.data.drop(columns=[
                'Your institution / organisation / group (for internal purposes only, information will not be public).',
                'Further description of your role or group'
            ])

        if outpath:
            self.data.to_hdf(outpath, key = "survey")

    def _adapt_column_names(self):
        """Adapt entries and columns of the table"""

        for colname in self.data.columns:
            colname_new = str(colname).replace("applicable:", "applicable ")
            self.data = self.data.rename(columns={colname: colname_new})

    def _create_question_metadata(self):
        """Extracting metadata from the survey file. 
        For each question, an identifier (A...) is defined, and subquestions grouped."""
        questions = {}
        
        for colname in self.data.columns:
            subtexts = colname.split(":")
            questionid = False
            for qid in questions:
                if questions[qid]["question"] == subtexts[0]:
                    questionid = qid
            if not questionid:
                if len(subtexts) == 1:
                    subtexts[0] = colname
                questions.setdefault("A"+str(len(questions)), {
                    "question": subtexts[0], 
                    "subquestions": [], 
                    "colnames": [], 
                    "entrytype": "undefined",
                    "params": {}
                })
                qid = "A"+str(len(questions)-1)
            if len(subtexts)>1:
                questions[qid]["subquestions"].append(subtexts[1:len(subtexts)])
                questions[qid]["colnames"].append(colname)
        self.metadata = questions
        
    def preprocess(self):
        """Preprocessing the survey data for use"""
        
        self._anonymize()
        self._adapt_column_names()
        self._create_question_metadata()

        self._identify_question_types()

        self._adapt_answers()

    def _identify_question_types(self):
        """Identifying question types according to metadata"""

        for qid in self.metadata:
            
            columns = []
            self.metadata[qid]["params"].setdefault("subtypes", {})
            self.metadata[qid]["params"].setdefault("options", {})
            
            if len(self.metadata[qid]["colnames"]) == 0:
                columns = [self.metadata[qid]["question"]]
            else:
                columns = self.metadata[qid]["colnames"]
                self.metadata[qid]["entrytype"] = "multiple"
                
            for colname in columns:
                columntype = ""

                uniqueanswers = self.data[colname].unique()
                answers = [x for x in uniqueanswers if pd.notna(x)]
                
                dtype = self.data[colname].dtype
                
                if str(dtype) == "float64":
                    columntype = "undefined"
                    
                elif str(dtype) == "datetime64[ns]":
                    columntype = "date"
                    
                elif len(answers) == 0:
                    columntype = "no answers"
                    
                elif type(answers[0]) is str:
                    columntype = "text"
                    
                    subanswers = []
                    totallength = 0
                    for answer in answers:
                        totallength += len(answer.split(";"))
                        for subans in answer.split(";"):
                            if not subans.lstrip(" ") in subanswers:
                                subanswers.append(subans.lstrip(" "))

                    if totallength > len(subanswers):
                        columntype = "enumerate"
    
                        self.metadata[qid]["params"]["options"].setdefault(colname, subanswers)

                    if str(answers[0]).find("http")>-1:
                        columntype = "URL"

                    elif str(answers[0]).find("/5")>0 or str(answers[0]).find("/10")>0:
                        columntype = "rating"

                        self.metadata[qid]["params"]["options"].setdefault(colname, float(str(answers[0]).split("/")[1]))
    
                if not columntype:
                    columntype = "undefined"

                if self.metadata[qid]["entrytype"] == "multiple":
                    self.metadata[qid]["params"]["subtypes"].setdefault(colname, columntype)
                else:
                    self.metadata[qid]["entrytype"] = columntype

    def _adapt_answers(self):
        """Change the entries in the data table for better processing
        """
        pass

    def list_questions(self, filter_type = ""):
        """Returns DataFrame with metadata of the questions.
            If filter_type provides type of question, only matching entries are listed
        """

        meta_df = pd.DataFrame(self.metadata).T
        if filter_type:
            meta_df = meta_df[meta_df["entrytype"]==filter_type]
        return meta_df

    def get_question_data(self, questionid):
        """Returns dataframe according to question identifier
        """
        colnames = []
        if len(self.metadata[questionid]["colnames"]) > 0:
            colnames = self.metadata[questionid]["colnames"]
        else:
            colnames = [self.metadata[questionid]["question"]]
            
        return self.data.loc[:, colnames]
