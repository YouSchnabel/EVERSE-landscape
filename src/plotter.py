from surveyreader import DataSet
from IPython.display import Markdown, display
import yaml

class ReportMaker:
    def __init__(self, datasetpath = "", configpath = "", outfilepath = ""):
        self.conf = False
        self.dataset = False
        self.outpath = outfilepath.rstrip("/") + "/"
        
        if configpath:
            with open(configpath, 'r') as file:
                self.conf = yaml.safe_load(file)
        if datasetpath:
            self.dataset = DataSet(datasetpath)

    def create_report(self, output = "display"):
        """Creates the full report. Can output to notebook (display) or as markdown files (pages)."""

        if not self.conf:
            print ("You did not provide a config file!")
            return

        if output == "pages":
            indexpage = "# EVERSE software quality landscaping survey\n\n## Survey results\n\n"

        for chap in self.conf:
            elements = []
            if chap.find("chap")>-1:
                title = chap.lstrip("chap_")
                if "title" in self.conf[chap]:
                    title = self.conf[chap]["title"]
                    elements.append("## "+ title +"\n")
                if "description" in self.conf[chap]:
                    elements.append(self.conf[chap]["description"]+"\n")
                for subkey in self.conf[chap]:
                    cluster = self.conf[chap][subkey]
                    if "title" in cluster:
                        elements.append("### "+cluster["title"]+"\n")
                    if "description" in cluster:
                        elements.append(cluster["description"]+"\n")
                    if "table" in subkey:
                        if not "alttitles" in cluster:
                            elements.append(self.make_table(cluster["identifiers"])+"\n")
                        else:
                            elements.append(self.make_table(cluster["identifiers"], cluster["alttitles"])+"\n")

            if output == "display":
                for element in elements:
                    display(Markdown(element))
            elif output == "pages":
                filename = chap
                if "filename" in self.conf[chap]:
                    filename = self.conf[chap]["filename"]

                with open(self.outpath + "pages/"+ filename + ".md", "w") as f:
                    for element in elements:
                        f.write(element+"\n")
                indexpage += "- ["+title+"](pages/"+ filename +".md)\n"

        if output == "pages":
            indexpage += "\nThis site was built using [GitHub Pages](https://pages.github.com) and Jekyll.\n"
            with open(self.outpath + "index.md", "w") as f:
                f.write(indexpage)
    
    def make_table(self, questionids, alttitles = []):
        """Produces table from text answers, deleting rows without answers."""

        acceptedtypes = ["text", "enumerate", "select"]
        colnames = []
        for qid in questionids:
            if self.dataset.metadata[qid]["entrytype"] in acceptedtypes:
                colnames.append(self.dataset.metadata[qid]["question"])
            elif self.dataset.metadata[qid]["entrytype"] == "multiple":
                for colname in self.dataset.metadata[qid]["params"]["subtypes"]:
                    if self.dataset.metadata[qid]["params"]["subtypes"][colname] in acceptedtypes:
                        colnames.append(colname)
            else:
                print ("For question-ID", qid, "the type is not an accepted type ",acceptedtypes," or 'multiple', will not add type", self.dataset.metadata[qid]["entrytype"])
    
        df_all = self.dataset.data[colnames]
        df = df_all.dropna(how='all').fillna('')
    
        if alttitles and len(alttitles) == len(questionids):
            newnames = {}
            for i in range(len(alttitles)):
                newnames.setdefault(self.dataset.metadata[questionids[i]]["question"], alttitles[i])
            df = df.rename(columns=newnames)
    
        return df.to_markdown()

