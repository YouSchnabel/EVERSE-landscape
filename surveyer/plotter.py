import subprocess
import shutil
import yaml
import os

from IPython.display import Markdown, display
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import re

from surveyer.surveyreader import DataSet

class ReportMaker:
    def __init__(self, datasetpath="", configpath="", outfilepath=""):
        self.conf = False
        self.dataset = False
        if outfilepath:
            self.outpath = outfilepath.rstrip("/") + "/"
        else:
            self.outpath = outfilepath

        if configpath:
            with open(configpath, "r") as file:
                self.conf = yaml.safe_load(file)
        if datasetpath:
            self.dataset = DataSet(datasetpath)

    def create_report(self, output="display", writepdf=False):
        """Creates the full report from the provided configuration (structure.yml) file.
        Can output to notebook (display) or as markdown files (pages).
        If 'writepdf' is set, a summary markdown and pdf is produced. You can set the pdfname in the configuration file."""

        if not self.conf:
            print("You did not provide a config file!")
            return

        if output == "pages":
            indexpage = (
                "# EVERSE software quality landscaping survey\n\n## Survey results\n\n"
            )

            if not os.path.exists(self.outpath + "pages/"):
                os.makedirs(self.outpath + "pages/")

            if not os.path.exists(self.outpath + "pages/figures/"):
                os.makedirs(self.outpath + "pages/figures/")

        if writepdf:
            alltext = (
                "# EVERSE software quality landscaping survey\n\n## Survey results\n\n"
            )

        # write pages for all "chapters" defined in the configuration
        for chap in self.conf:
            elements = []
            title = ""
            if chap.find("chap") > -1:
                title = chap.lstrip("chap_")
                if "title" in self.conf[chap]:
                    title = self.conf[chap]["title"]
                    elements.append("## " + title + "\n")
                if "description" in self.conf[chap]:
                    elements.append(self.conf[chap]["description"] + "\n")
                for subkey in self.conf[chap]:
                    cluster = self.conf[chap][subkey]
                    if "title" in cluster:
                        elements.append("### " + cluster["title"] + "\n")
                    if "description" in cluster:
                        elements.append(cluster["description"] + "\n")
                    if "table" in subkey:
                        if not "alttitles" in cluster:
                            elements.append(
                                self.make_table(cluster["identifiers"]) + "\n"
                            )
                        else:
                            elements.append(
                                self.make_table(
                                    cluster["identifiers"], cluster["alttitles"]
                                )
                                + "\n"
                            )

                    if "count" in subkey:
                        charttype = "bar"
                        title = "Counts"
                        altanswers = []
                        if "altoptions" in cluster:
                            altanswers = cluster["altoptions"]
                        if "title" in cluster:
                            title = cluster["title"]
                        if "charttype" in cluster:
                            charttype = cluster["charttype"]
                        plotname = self.make_count_chart(
                            cluster["identifier"], charttype, title, altanswers
                        )
                        if plotname:
                            if os.path.exists(
                                self.outpath + "pages/figures/" + plotname
                            ):
                                os.remove(self.outpath + "pages/figures/" + plotname)
                            shutil.move(plotname, self.outpath + "pages/figures/")
                        elements.append("![" + title + "](figures/" + plotname + ")")

                    if "compare" in subkey:
                        selector = ""
                        altanswers = []
                        if "title" in cluster:
                            title = cluster["title"]
                        if "altoptions" in cluster:
                            altanswers = cluster["altoptions"]
                        plotname = self.make_compare_likert(
                            cluster["identifier"],
                            cluster["selectedparts"],
                            title,
                            altanswers,
                        )
                        if plotname:
                            if os.path.exists(
                                self.outpath + "pages/figures/" + plotname
                            ):
                                os.remove(self.outpath + "pages/figures/" + plotname)
                            shutil.move(plotname, self.outpath + "pages/figures/")
                        elements.append("![" + title + "](figures/" + plotname + ")")

                    if "rating" in subkey:
                        if "title" in cluster:
                            title = cluster["title"]
                        plotname = self.make_rating(cluster["identifier"], title)
                        if plotname:
                            if os.path.exists(
                                self.outpath + "pages/figures/" + plotname
                            ):
                                os.remove(self.outpath + "pages/figures/" + plotname)
                            shutil.move(plotname, self.outpath + "pages/figures/")
                        elements.append("![" + title + "](figures/" + plotname + ")")

                    if "multirate" in subkey:
                        exclusion = ""
                        if "title" in cluster:
                            title = cluster["title"]
                        if "exclude" in cluster:
                            exclusion = cluster["exclude"]
                        plotname = self.make_multirating(
                            cluster["identifier"], title, exclusion
                        )
                        if plotname:
                            if os.path.exists(
                                self.outpath + "pages/figures/" + plotname
                            ):
                                os.remove(self.outpath + "pages/figures/" + plotname)
                            shutil.move(plotname, self.outpath + "pages/figures/")
                        elements.append("![" + title + "](figures/" + plotname + ")")

                if output == "display":
                    for element in elements:
                        display(Markdown(element))
                elif output == "pages":
                    filename = chap
                    if "filename" in self.conf[chap]:
                        filename = self.conf[chap]["filename"]
                    title = chap.lstrip("chap_")
                    if "title" in self.conf[chap]:
                        title = self.conf[chap]["title"]
                        elements.append("## " + title + "\n")

                    with open(self.outpath + "pages/" + filename + ".md", "w") as f:
                        for element in elements:
                            f.write(element + "\n")
                    print("Title:", title)
                    indexpage += "- [" + str(title) + "](pages/" + filename + ".md)\n"

                if writepdf:
                    alltext += "\n\n".join(
                        [el.replace("figures/", "pages/figures/") for el in elements]
                    )

        if output == "pages":
            indexpage += "\nBack to the [repository](https://github.com/YouSchnabel/EVERSE-landscape), or look up the [code documentation](https://youschnabel.github.io/EVERSE-landscape/pydocs/surveyer.html)!\n"
            indexpage += "\nThis site was built using [GitHub Pages](https://pages.github.com) and Jekyll.\n"
            with open(self.outpath + "index.md", "w") as f:
                f.write(indexpage)

        if writepdf:
            pdffilepath = self.outpath + "EVERSEsurveyresults.pdf"
            if "pdfname" in self.conf:
                pdffilepath = self.outpath + self.conf["pdfname"]
            mdfilepath = self.outpath + pdffilepath.rstrip(".pdf") + ".md"
            with open(mdfilepath, "w") as temp_md_file:
                temp_md_file.write(alltext)
            try:
                # Call Pandoc to convert the Markdown file to PDF
                subprocess.run(
                    [
                        "pandoc",
                        mdfilepath,
                        "--from=markdown",
                        "--to=pdf",
                        "--output",
                        pdffilepath,
                        "--template=template.tex",
                    ],
                    check=True,
                )
                print(f"PDF generated successfully: {pdffilepath}")
            except subprocess.CalledProcessError:
                print("Error: Pandoc failed to convert Markdown to PDF.")

    def make_table(self, questionids, alttitles=[]):
        """Produces table from text answers, deleting rows without answers."""

        acceptedtypes = ["text", "enumerate", "select"]

        df_all = self.dataset.extract_subset(questionids, acceptedtypes)
        df = df_all.dropna(how="all").fillna("")
        df = df.applymap(_format_urls_in_text)

        if alttitles and len(alttitles) == len(questionids):
            newnames = {}
            for i in range(len(alttitles)):
                newnames.setdefault(
                    self.dataset.metadata[questionids[i]]["question"], alttitles[i]
                )
            df = df.rename(columns=newnames)

        return df.to_markdown()

    def make_count_chart(self, questionid, charttype="bar", title="", altanswers=[]):
        """Produces a graphic to show basic statistic of selection or enumeration questions.
        Chart type can be 'bar', 'pie' or 'line', and you can provide alternative title and answer lables."""

        acceptedtypes = ["select", "enumerate"]

        if not title:
            title = "Count of responses"

        df_extract = self.dataset.extract_subset([questionid], acceptedtypes)

        if self.dataset.metadata["A2"]["entrytype"] == "enumerate":
            df_nona = df_extract.dropna()
            df_enlisted = [
                entry.split("; ") for entry in df_nona[df_extract.columns[0]]
            ]
            df_extract = pd.DataFrame(
                {
                    df_extract.columns[0]: [
                        item for sublist in df_enlisted for item in sublist
                    ]
                }
            )

        answer_counts = df_extract.value_counts()

        # create the bar chart
        plt.figure(figsize=(6, 4))
        if charttype != "pie":
            answer_counts.plot(kind=charttype)
            plt.xlabel("Response")
            plt.ylabel("Frequency")
            plt.xticks(rotation=40, ha="right")
        else:
            plt.xlabel("Number of entries: " + str(answer_counts.sum()))

        plt.title(title)

        if altanswers:
            if len(answer_counts) == len(altanswers):
                if charttype != "pie":
                    plt.xticks(
                        ticks=range(len(altanswers)),
                        labels=altanswers,
                        rotation=40,
                        ha="right",
                    )
                else:
                    plt.pie(
                        answer_counts,
                        labels=altanswers,
                        autopct="%1.1f%%",
                        startangle=90,
                    )
            else:
                print(
                    "Alternative options length",
                    len(altanswers),
                    "does not match required length",
                    len(answer_counts),
                )

        filename = (
            "plot_"
            + charttype
            + "_"
            + str(questionid)
            .replace("[", "")
            .replace("]", "")
            .replace(",", "_")
            .replace("'", "")
            + ".png"
        )

        plt.tight_layout()
        # Save the chart as an image
        plt.savefig(filename)

        return filename

    def make_compare_likert(self, questionid, subquestion, title="", altanswers=[]):
        """Displays several Likert-scale type answers for comparison.
        Needs subquestion to select all subquestions which contain the provided string.
        Can be passed title for the plot and answer options to replace the original ones.
        Scales can be provided under the 'scales' entry in the configuration file.
        """
        acceptedtypes = ["select"]

        if not title:
            title = "Estimate"

        # df_extract = self.dataset.extract_subset(questionids, acceptedtypes)
        # # also extract subquestion

        columns = []
        altnames = []
        for i in range(len(self.dataset.metadata[questionid]["subquestions"])):
            otherpart = []
            foundpart = ""
            for entry in self.dataset.metadata[questionid]["subquestions"][i]:
                if entry.find(subquestion) > -1:
                    foundpart = self.dataset.metadata[questionid]["colnames"][i]
                else:
                    otherpart.append(entry)
            if foundpart:
                columns.append(foundpart)
                altnames.append(otherpart)

        if altanswers:
            altnames = altanswers
        else:
            altnames = [
                str(ent).replace("['", "").replace("']", "").replace("','", " : ")
                for ent in altnames
            ]

        plottype = ""
        options = ""

        for col in columns:
            if col in self.dataset.metadata[questionid]["params"]["options"]:
                if not options:
                    options = self.dataset.metadata[questionid]["params"]["options"][
                        col
                    ]
                else:
                    newopts = self.dataset.metadata[questionid]["params"]["options"][
                        col
                    ]
                    for opt in newopts:
                        if not opt in options:
                            options.append(opt)

            if col in self.dataset.metadata[questionid]["params"]["subtypes"]:
                if not plottype:
                    plottype = self.dataset.metadata[questionid]["params"]["subtypes"][
                        col
                    ]
                else:
                    if (
                        self.dataset.metadata[questionid]["params"]["subtypes"][col]
                        != plottype
                    ):
                        print(
                            "Question types don't match!",
                            self.dataset.metadata[questionid]["params"]["subtypes"][
                                col
                            ],
                            plottype,
                        )
                        plottype = "mismatch"

        scale = []

        if "scales" in self.conf:
            for skey in self.conf["scales"]:
                if sorted(self.conf["scales"][skey]["options"]) == sorted(options):
                    scale = self.conf["scales"][skey]["options"]

        if not scale:
            scale = options

        df = self.dataset.data[columns]

        df_melted = df.melt(var_name=subquestion, value_name="Response")

        # Plot the grouped bar chart
        plt.figure(figsize=(12, 6))
        sns.countplot(
            data=df_melted,
            x=subquestion,
            hue="Response",
            order=df.columns,
            hue_order=scale,
            palette="coolwarm",
        )

        # Add titles and labels
        plt.title(title)
        plt.xlabel("Question")
        plt.ylabel("Count")
        plt.legend(
            title=subquestion, bbox_to_anchor=(1.05, 1), loc="upper left"
        )  # Move the legend outside
        # Rotate x-axis labels if neede
        plt.xticks(ticks=range(len(altnames)), labels=altnames)

        plt.tight_layout()  # Adjust layout for readability

        filename = (
            "plot_" + subquestion.replace(" ", "_") + "_" + str(questionid) + ".png"
        )

        plt.savefig(filename)

        return filename

    def make_rating(self, questionid, title=""):
        """Displays distribution of a rating question."""

        acceptedtypes = ["rating", "select"]

        df_extract_all = self.dataset.extract_subset([questionid])
        df_extract = df_extract_all[df_extract_all.columns[0]]

        all_ratings = list(
            range(
                1, self.dataset.metadata[questionid]["params"]["options"]["factor"] + 1
            )
        )

        df_extract = pd.DataFrame(
            {
                df_extract_all.columns[0]: [
                    int(entry.split("/")[0]) for entry in df_extract
                ]
            }
        ).dropna()
        df_extract = pd.to_numeric(
            df_extract[df_extract_all.columns[0]], errors="coerce"
        )
        rating_counts = df_extract.value_counts().reindex(all_ratings, fill_value=0)

        # Calculate Mean and RMS
        mean_rating = df_extract.mean()

        # Plot the distribution of ratings
        plt.figure(figsize=(8, 6))
        ax = sns.barplot(
            x=rating_counts.index, y=rating_counts.values, palette="viridis"
        )

        # Add Mean and RMS to the legend
        mean_label = f"Mean: {mean_rating:.2f}"
        handles, labels = ax.get_legend_handles_labels()
        handles.extend([plt.Line2D([0], [0], color="none", label=mean_label)])
        ax.legend(handles=handles, loc="upper right")

        if not title:
            title = df_extract_all.columns[0]

        # Adding titles and labels
        plt.title(title)
        plt.xlabel("Rating")
        plt.ylabel("Count")

        filename = "plot_rating_" + str(questionid) + ".png"

        plt.savefig(filename)

        return filename

    def make_multirating(self, questionid, title="", excludeterms=[]):
        """Displays distribution of several rating question."""

        columnsall = self.dataset.metadata[questionid]["colnames"]

        columns = []
        for col in columnsall:
            dontuse = False
            for term in excludeterms:
                if col.find(term) > -1:
                    dontuse = True
            if not excludeterms or not dontuse:
                columns.append(col)

        df = self.dataset.data[columns].dropna()
        df[columns] = df[columns].applymap(lambda x: int(x.split("/")[0]))

        altnames = [
            str(entry[0]) for entry in self.dataset.metadata[questionid]["subquestions"]
        ]

        renamemap = {}
        for i in range(len(columnsall)):
            dontuse = False
            for term in excludeterms:
                if columnsall[i].find(term) > -1:
                    dontuse = True
            if not excludeterms or not dontuse:
                renamemap.setdefault(columnsall[i], altnames[i])
        df = df.rename(columns=renamemap)

        # Calculate mean and standard deviation for each question
        means = df.mean()
        stds = df.std()

        # Plot each question as a horizontal bar with error bars for standard
        # deviation
        plt.figure(figsize=(8, 6))
        plt.barh(
            y=means.index, width=means, xerr=stds, color="skyblue", edgecolor="gray"
        )

        # Add mean values next to bars for clarity
        for index, value in enumerate(means):
            plt.text(value + 0.1, index, f"{value:.2f}", va="center", color="black")

        if not title:
            title = "Mean and Spread of Ratings by Question"
        # Add labels and title
        plt.xlabel(
            "Rating out of "
            + str(self.dataset.metadata[questionid]["params"]["options"]["factor"])
        )
        plt.title(title)
        plt.grid(axis="x", linestyle="--", alpha=0.7)

        plt.tight_layout()

        filename = (
            "plot_multirating_"
            + str(questionid)
            + "_"
            + str(excludeterms).lstrip("['").rstrip("']").replace("', '", "_")
            + ".png"
        )

        plt.savefig(filename)

        return filename


def _format_urls_in_text(text):
    # Regular expression to match URLs
    url_pattern = r"(https?://[^\s]+)"
    # Replace each URL with Markdown formatted link
    return re.sub(url_pattern, r"[\1](\1)", text)
