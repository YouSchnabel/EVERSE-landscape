"""Read info from survey export and make useable"""

import pandas as pd

class DataSet:
    def __init__(self, filepath):
        self.metadata = {}
        self.data = pd.DataFrame()

        self.read(filepath)
        self.preprocess()

    def read(self, filepath):
        """Reading the survey results from the export from EU survey"""

        if filepath.find("xls") > -1:
            self.data = pd.read_excel(filepath, header=3)
        elif filepath.find("h5") > -1:
            self.data = pd.read_hdf(filepath, key="survey")

    def _anonymize(self, internaluse=False, outpath=""):
        """Deleting entries with personal information.
        If internaluse = True, keeping details on affiliation.
        If outpath is provided, anonymized dataset is written to xls."""

        if "Name" in self.data.columns:
            self.data = self.data.drop(
                columns=[
                    "Name",
                    "email",
                    "Invitation number",
                    "Contribution ID",
                    "User name",
                    "Languages",
                ]
            )

        if (
            not internaluse
            and "Further description of your role or group" in self.data.columns
        ):
            self.data = self.data.drop(
                columns=[
                    "Your institution / organisation / group (for internal purposes only, information will not be public).",
                    "Further description of your role or group",
                ]
            )

        if outpath:
            self.data.to_hdf(outpath, key="survey")

    def _adapt_column_names(self):
        """Adapt entries and columns of the table"""

        for colname in self.data.columns:
            colname_new = str(colname).replace("applicable:", "applicable ")
            colname_new = str(colname).replace(": Confidence", "- Confidence")
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
                questions.setdefault(
                    "A" + str(len(questions)),
                    {
                        "question": subtexts[0],
                        "subquestions": [],
                        "colnames": [],
                        "entrytype": "undefined",
                        "params": {},
                    },
                )
                qid = "A" + str(len(questions) - 1)

            if len(subtexts) > 1:
                questions[qid]["subquestions"].append(subtexts[1 : len(subtexts)])
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

                answersall = [x for x in self.data[colname] if pd.notna(x)]
                uniqueanswers = list(set(answersall))

                dtype = self.data[colname].dtype

                if str(dtype) == "float64":
                    columntype = "undefined"

                elif str(dtype) == "datetime64[ns]":
                    columntype = "date"

                elif len(answersall) == 0:
                    columntype = "no answers"

                elif isinstance(uniqueanswers[0], str):
                    columntype = "text"

                    subanswers = []
                    samelength = True
                    entrylength = 1
                    notsingle = False

                    for answers in answersall:
                        answerssplit = answers.split(";")
                        if entrylength == 1:
                            entrylength = len(answerssplit)

                        if answers == answersall[0] and len(answerssplit) > 1:
                            notsingle = True

                        if len(answerssplit) != entrylength and samelength:
                            samelength = False

                        for subans in answerssplit:
                            if not subans.lstrip(" ") in subanswers:
                                subanswers.append(subans.lstrip(" "))

                    # see if answers contain /10 -> rating

                    if (
                        str(uniqueanswers[0]).find("/5") > 0
                        or str(uniqueanswers[0]).find("/10") > 0
                    ) and str(uniqueanswers[0]).find("ttp") < 0:
                        columntype = "rating"

                    # see if entries can be split with different length ->
                    # multichoice

                    elif entrylength > 1 and not samelength:
                        columntype = "enumerate"

                    # see if entries can be split with same length -> ranking

                    elif entrylength > 1 and samelength and notsingle:
                        columntype = "ranking"

                    # see if entries are repetitive -> select

                    elif entrylength == 1 and len(subanswers) < len(answersall):
                        columntype = "select"

                    if columntype != "text":
                        if columntype == "rating":
                            self.metadata[qid]["params"]["options"].setdefault(
                                "factor", int(str(uniqueanswers[0]).split("/")[1])
                            )
                        else:
                            self.metadata[qid]["params"]["options"].setdefault(
                                colname, subanswers
                            )

                if not columntype:
                    columntype = "undefined"

                if self.metadata[qid]["entrytype"] == "multiple":
                    self.metadata[qid]["params"]["subtypes"].setdefault(
                        colname, columntype
                    )
                else:
                    self.metadata[qid]["entrytype"] = columntype

    def _adapt_answers(self):
        """Change the entries in the data table for better processing"""
        pass

    def list_questions(self, filter_type=""):
        """Returns DataFrame with metadata of the questions.
        If filter_type provides type of question, only matching entries are listed
        """

        meta_df = pd.DataFrame(self.metadata).T
        if filter_type:
            meta_df = meta_df[meta_df["entrytype"] == filter_type]
        return meta_df

    def get_question_data(self, questionid):
        """Returns dataframe according to question identifier"""
        colnames = []
        if len(self.metadata[questionid]["colnames"]) > 0:
            colnames = self.metadata[questionid]["colnames"]
        else:
            colnames = [self.metadata[questionid]["question"]]

        return self.data.loc[:, colnames]

    def _get_colnames(self, questionids, acceptedtypes=[]):
        """Returns column names for given question IDs, facilitating filtering for specific types."""

        colnames = []

        for qid in questionids:
            if (
                acceptedtypes
                and self.metadata[qid]["entrytype"] in acceptedtypes
                or not acceptedtypes
            ):
                colnames.append(self.metadata[qid]["question"])
            elif self.metadata[qid]["entrytype"] == "multiple":
                for colname in self.metadata[qid]["params"]["subtypes"]:
                    if (
                        self.metadata[qid]["params"]["subtypes"][colname]
                        in acceptedtypes
                    ):
                        colnames.append(colname)
            else:
                print(
                    "For question-ID",
                    qid,
                    "the type is not an accepted type ",
                    acceptedtypes,
                    " or 'multiple', will not add type",
                    self.metadata[qid]["entrytype"],
                )

        return colnames

    def extract_subset(self, questionids, acceptedtypes=[]):
        """Returns dataframe with subset of data according to questionids, and filters for provided types of questions."""
        colnames = self._get_colnames(questionids, acceptedtypes)

        return self.data[colnames]
