#!/usr/bin/env python3

import re
import string
import warnings
from argparse import ArgumentParser
from collections import defaultdict
from datetime import datetime
from itertools import combinations
from os import listdir, mkdir
from os.path import isdir, splitext
from typing import Union

import networkx as nx
import nltk
import pandas as pd
import plotly.express as px
import plotly.io as pio

try:
    from .lib_stopwords import STOPWORDS
except:
    from lib_stopwords import STOPWORDS

pio.templates.default = "none"

warnings.filterwarnings("ignore", category=FutureWarning)

COLUMN_DATE = ["Date", "Date created"]
COLUMN_NAME = ["Name", "Username"]
COLUMN_COMMENTS = "Comments"
COLUMN_LIKES = "Likes"
COLUMN_TEXT = ["Comment", "Caption"]

ENGINE = "c"
EXTENSIONS = [".csv", ".xls", ".xlsx"]
GRAPH_FORMAT = "gml"
MAX_WORD_NODES = 100
N_GRAMS = 2
N_REPLIES = 10
N_THREADS = 10
NODE_ZERO = "0"
OUTPUT_FORMAT = "csv"
OUTPUT_NAME = "RESULTS"
QUICK_PARSE = False
REMOVE_SELFLOOPS = True
SKIPROWS = None

DATETIME_SOURCE = "%Y-%m-%d %H:%M:%S"
DATETIME_TARGET = "%Y-%m-%d %H:%M:%S"

ACCENT_REPLACEMENTS = {
    ord('á'): 'a', ord('ã'): 'a', ord('â'): 'a',
    ord('à'): 'a', ord('è'): 'e', ord('ê'): 'e',
    ord('é'): 'e', ord('í'): 'i', ord('ì'): 'i',
    ord('ñ'): 'n', ord('ò'): 'o', ord('ó'): 'o',
    ord('ô'): 'o', ord('õ'): 'o', ord('ù'): 'u',
    ord('ú'): 'u', ord('ü'): 'u', ord('ç'): 'c'}

VALID_CHARACTERS = "@#"
INVALID_CHARACTERS = "\\\"'’…|–—“”‘„•¿¡"

CHARACTER_REPLACEMENTS = str.maketrans('', '', ''.join(
    set(string.punctuation + INVALID_CHARACTERS) - set(VALID_CHARACTERS)))

IGNORE_STARTS_WITH = ['http', 'www', 'kkk']

class ParseComments():

    def __init__(self, engine=ENGINE):
        self.engine = ENGINE

    def parse_comments(
        self,
        input_name,
        column_name=COLUMN_NAME,
        column_comments=COLUMN_COMMENTS,
        column_date=COLUMN_DATE,
        column_likes=COLUMN_LIKES,
        column_text=COLUMN_TEXT,
        datetime_source=DATETIME_SOURCE,
        datetime_target=DATETIME_TARGET,
        extensions=EXTENSIONS,
        graph_format=GRAPH_FORMAT,
        max_word_nodes=MAX_WORD_NODES,
        n_grams=N_GRAMS,
        n_replies=N_REPLIES,
        n_threads=N_THREADS,
        node_zero=NODE_ZERO,
        output_format=OUTPUT_FORMAT,
        output_name=OUTPUT_NAME,
        remove_selfloops=REMOVE_SELFLOOPS,
        quick_parse=QUICK_PARSE,
        skiprows=SKIPROWS,
        stop_words=STOPWORDS,
    ) -> None:
        tokenizer = Tokenizer(stop_words=stop_words)
        stop_words = stop_words = ["photo"]

        threads = list()
        dates = defaultdict(int)
        hours = defaultdict(int)
        profiles = defaultdict(lambda:defaultdict(int))
        times = defaultdict(int)
        statistics = defaultdict(lambda:defaultdict(str))

        G_ngrams = nx.Graph()
        G_profiles = nx.DiGraph()
        G_words = nx.Graph()

        for f in self.__list_files(input_name, extensions):

            if skiprows is None:
                skiprows = 0
                sample = self._load_comments(f, nrows=10, skiprows=0)
                if "Unnamed" in sample.columns[-1]:
                    skiprows = 5
                    sample = self._load_comments(f, nrows=10, skiprows=5)
                    if "Unnamed" in sample.columns[-1]:
                        skiprows = 6

            df = self._load_comments(f, skiprows=skiprows)
            print(f"Loaded {df.shape} objects from '{f}' (rows skipped: {skiprows}).")

            for column in column_date:
                if column in df.columns:
                    column_date = column
                    break

            for column in column_name:
                if column in df.columns:
                    column_name = column
                    break

            for column in column_text:
                if column in df.columns:
                    column_text = column
                    break

            print(f"Processing rows...")
            text = df\
                .loc[:, column_text]\
                .apply(str)\
                .apply(lambda x: x.split("\n"))\
                .apply(lambda x: x if x else None)\
                .dropna()\
                .explode()

            print(f"Processing hashtags...")
            hashtags = text\
                .apply(lambda x: self.__find_hashtags(x))\
                .explode()\
                .value_counts()

            print(f"Processing tokens...")
            tokens = text\
                .apply(lambda x: tokenizer.tokenize(x) or None)\
                .dropna()

            if not quick_parse:
                print(f"Generating word graph...")
                self.__add_edges_to_graph(
                    G_words,
                    edges=pd.Series([list(combinations(_, 2)) for _ in tokens]).explode().dropna(),
                    remove_selfloops=remove_selfloops,
                )

            words = tokens\
                .explode()\
                .value_counts()

            print(f"Processing n-grams...")
            ngrams = tokens\
                .apply(lambda x: tokenizer.ngrams(x, n=n_grams) or None)\
                .dropna()\
                .apply(lambda x: [" ".join(_) for _ in x])

            if not quick_parse:
                print(f"Generating n-gram graph...")
                self.__add_edges_to_graph(
                    G_ngrams,
                    edges=pd.Series([list(combinations(_, 2)) for _ in ngrams]).explode().dropna(),
                    remove_selfloops=remove_selfloops,
                )

            ngrams = ngrams\
                .explode()\
                .value_counts()

            print(f"Processing threads...")
            try:
                thread_profiles = {
                    int(k): y
                    for k, x, y in zip(
                        df.iloc[:, 0],
                        df.iloc[:, 1],
                        df.loc[:, column_name],
                    )
                    if type(x) != str
                }
            except:
                column_name = column_name.split()[0]

            thread_ids = pd.Series({
                k: str(y if type(y) == str else x)
                for k, x, y in zip(
                    df.index,
                    df.iloc[:, 0],
                    df.iloc[:, 1],
                )
            })

            datetimes = df\
                .loc[:, column_date]\
                .apply(lambda x: (datetime.strptime(x, datetime_source) if type(x) == str else x).strftime(datetime_target))

            for k, v in datetimes.apply(lambda x: x[:10]).value_counts().items():
                dates[k] += v
            for k, v in datetimes.apply(lambda x: f"{x[:14]}00:00").value_counts().items():
                hours[k] += v
            for k, v in datetimes.apply(lambda x: f"{x[:18]}0").value_counts().items():
                times[k] += v

            replies = df\
                .loc[thread_ids.apply(lambda x: x if "-" in x else None).dropna().index]

            print(f"Generating profile graph...")

            self.__add_edges_to_graph(
                G_profiles,
                edges=[
                    [s, node_zero]
                    for s in
                        df.loc[thread_ids.apply(lambda x: x if "-" not in x else None).dropna().index, column_name]
                ],
                remove_selfloops=remove_selfloops
            )

            self.__add_edges_to_graph(
                G_profiles,
                edges=[
                    [s, thread_profiles[int(t)]]
                    for s, t in zip(
                        replies.loc[:, column_name],
                        replies.iloc[:, 1].apply(lambda x: x.split("-")[0]))
                    ],
                remove_selfloops=remove_selfloops
            )

            print(f"Generating statistics...")

            for i, thread in enumerate(
                replies
                .iloc[:, 1]
                .apply(lambda x: float(x.split("-")[0]))
                .value_counts()
                .head(n_threads)
                .items()
            ):
                loc = df.loc[df[df[df.columns[0]] == thread[0]].index[0]]
                threads.append({
                    "#": f"{i+1}",
                    "profile": loc[column_name],
                    "text": loc[column_text],
                    "likes": loc[column_likes],
                    "comments": loc[column_comments] if column_comments in df.columns else "",
                    "replies": thread[1],
                    "source": f
                })

                for j, reply in enumerate(
                    replies[replies.iloc[:, 1].apply(lambda x: True if float(x.split("-")[0]) == thread[0] else False)]
                    .sort_values(column_likes, ascending=False).index[:n_replies]
                ):
                    loc = replies.loc[reply]
                    threads.append({
                        "#": f"{i+1}-{j+1}",
                        "profile": loc[column_name],
                        "text": loc[column_text],
                        "likes": loc[column_likes],
                        "comments": loc[column_comments] if column_comments in df.columns else "",
                        "replies": "",
                        "source": f
                    })

            top_posts = df\
                .loc[:, column_name]\
                .value_counts()

            top_comments = df\
                .groupby(column_name)[column_comments]\
                .sum()\
                .sort_values(ascending=False)\
                if column_comments in df.columns else pd.Series()

            top_liked = df\
                .groupby(column_name)[column_likes]\
                .sum()\
                .sort_values(ascending=False)

            top_replies_sent = replies\
                [column_name]\
                .value_counts()

            top_replies_received = replies\
                .iloc[:, 1]\
                .apply(lambda x: x.split("-")[0])\
                .apply(lambda x: thread_profiles[int(x)])\
                .value_counts()

            for k, v in top_posts.items():
                profiles["posts"][k] += v
            for k, v in top_comments.items():
                profiles["comments"][k] += v
            for k, v in top_liked.items():
                profiles["likes"][k] += v
            for k, v in top_replies_sent.items():
                profiles["replies_sent"][k] += v
            for k, v in top_replies_received.items():
                profiles["replies_received"][k] += v

            statistics[f]["replies_total"] = thread_ids.shape[0]
            statistics[f]["replies_ancestors"] = thread_ids.apply(lambda x: x if "-" not in x else None).dropna().shape[0]
            statistics[f]["replies_replies"] = thread_ids.apply(lambda x: x if "-" in x else None).dropna().shape[0]
            statistics[f]["profiles"] = df.loc[:, column_name].unique().shape[0]

            if len(top_posts):
                statistics[f]["top_profile_in_posts"] = f"{top_posts.index[0]} ({top_posts.values[0]} comments)"

            if len(top_comments):
                statistics[f]["top_profile_in_comments"] = f"{top_posts.index[0]} ({top_posts.values[0]} comments)"

            if len(top_liked):
                statistics[f]["top_profile_in_likes"] = f"{top_liked.index[0]} ({top_liked.values[0]} likes)"

            if len(top_replies_sent):
                statistics[f]["top_profile_in_replies_sent"] = f"{top_replies_sent.index[0]} ({top_replies_sent.values[0]} replies)"

            if len(top_replies_received):
                statistics[f]["top_profile_in_replies_received"] = f"{top_replies_received.index[0]} ({top_replies_received.values[0]} replies)"

        if max_word_nodes:
            G_ngrams = nx.subgraph(G_ngrams, pd.Series(dict(G_ngrams.degree())).sort_values(ascending=False).index[:max_word_nodes])
            G_words = nx.subgraph(G_words, pd.Series(dict(G_words.degree())).sort_values(ascending=False).index[:max_word_nodes])

        print("Generating output files...")

        if not isdir(output_name):
            mkdir(output_name)

        getattr(nx, f"write_{graph_format}")(G_ngrams, f"{output_name}/graph_ngrams.{graph_format}")
        getattr(nx, f"write_{graph_format}")(G_profiles, f"{output_name}/graph_profiles.{graph_format}")
        getattr(nx, f"write_{graph_format}")(G_words, f"{output_name}/graph_words.{graph_format}")

        self.__write_file(pd.DataFrame(statistics),
                          f"{output_name}/statistics",
                          output_format=output_format)

        self.__write_file(pd.DataFrame(profiles).fillna(0).astype(int),
                          f"{output_name}/profiles",
                          index_label="profile",
                          output_format=output_format)

        self.__write_file(pd.DataFrame(threads),
                          f"{output_name}/threads",
                          index=False,
                          output_format=output_format)

        self.__write_file(pd.Series(dates).sort_index(),
                          f"{output_name}/dates_days",
                          index_label="datetime",
                          name="replies",
                          output_format=output_format,
                          plot=True)

        self.__write_file(pd.Series(hashtags),
                          f"{output_name}/hashtags",
                          index_label="hashtag",
                          name="total",
                          output_format=output_format,
                          plot=True,
                          plot_type="bar",
                          plot_n=10)

        self.__write_file(pd.Series(hours).sort_index(),
                          f"{output_name}/dates_hours",
                          index_label="datetime",
                          name="replies",
                          output_format=output_format,
                          plot=True)

        self.__write_file(pd.Series(ngrams),
                          f"{output_name}/ngrams",
                          index_label="n-gram",
                          name="total",
                          output_format=output_format,
                          plot=True,
                          plot_type="bar",
                          plot_n=10)

        self.__write_file(pd.Series(profiles["replies"]),
                          f"{output_name}/profiles_comments",
                          name="replies",
                          output_format=output_format,
                          plot=True,
                          plot_type="bar",
                          plot_n=10,
                          write=False)

        self.__write_file(pd.Series(profiles["likes"]),
                          f"{output_name}/profiles_likes",
                          name="likes",
                          output_format=output_format,
                          plot=True,
                          plot_type="bar",
                          plot_n=10,
                          write=False)

        self.__write_file(pd.Series(profiles["replies_sent"]),
                          f"{output_name}/profiles_replies_sent",
                          name="replies_sent",
                          output_format=output_format,
                          plot=True,
                          plot_type="bar",
                          plot_n=10,
                          write=False)

        self.__write_file(pd.Series(profiles["replies_received"]),
                          f"{output_name}/profiles_replies_received",
                          name="replies_received",
                          output_format=output_format,
                          plot=True,
                          plot_type="bar",
                          plot_n=10,
                          write=False)

        self.__write_file(pd.Series(times).sort_index(),
                          f"{output_name}/dates_seconds",
                          index_label="datetime",
                          name="replies",
                          output_format=output_format,
                          plot=True)

        self.__write_file(pd.Series(words),
                          f"{output_name}/words",
                          index_label="word",
                          name="total",
                          output_format=output_format,
                          plot=True,
                          plot_type="bar",
                          plot_n=10)

        print(f"Total of {G_profiles.order()} profiles and {G_profiles.size()} connections.")

    def _load_comments(self, name: str, skiprows: int = 0, nrows: int = None):
        return (
            pd.read_excel(
                name,
                nrows=nrows,
                skiprows=skiprows
            )
            if splitext(name)[1] in (".xls", ".xlsx")
            else pd.read_table(
                name,
                delimiter=self.__get_delimiter(name),
                nrows=nrows,
                skiprows=skiprows
            )
        )

    @staticmethod
    def __add_edges_to_graph(
        G: nx.Graph,
        edges: list,
        remove_selfloops: bool = False,
        weights: Union[bool, dict, pd.Series] = True,
    ) -> nx.Graph:

        if type(weights) == bool and weights is True:
            weights = pd.Series(edges).astype(str).value_counts()

        if type(weights) in (dict, pd.Series):
            weights = pd\
                .Series(weights)\
                .add(
                    pd.Series({f"{[x[0], x[1]]}": x[2]["weight"] for x in G.edges(data=True)}, dtype=float),
                    fill_value=0
                )\
                .astype(float)

            G.add_weighted_edges_from([
                [e[0], e[1], weights[str(e)]]
                for e in edges
                if (e[0] != e[1] or (e[0] == e[1] and not remove_selfloops))
            ])

            return G

        G.add_edges_from([
            [e[0], e[1]]
            for e in edges
            if e[0] != e[1]
            or (e[0] == e[1] and not remove_selfloops)
        ])
        return G

    @staticmethod
    def __find_hashtags(x) -> list:
        hashtags = re.findall(r"#[a-zA-Z0-9_]{0,30}", x.lower()) if isinstance(x, str) else []
        return [hashtag for hashtag in hashtags if len(hashtag)>1 ]

    @staticmethod
    def __get_delimiter(input_name: str) -> str:
        with open(input_name, 'rt') as f:
            header = f.readline()
        for d in ['|', '\t', ';', ',']:
            if d in header: # \\t != \t
                return d
        return '\n'

    @staticmethod
    def __list_files(input_name: Union[str, list], extensions: list) -> list:
        files = []

        for x in ([input_name] if type(input_name) == str else input_name):
            list(
                files.append(f"{x}/{f}")
                for f in sorted(listdir(x))
                if not isdir(f)
            )\
            if isdir(x)\
            else files.append(x)

        return [
            f for f in files if splitext(f)[1] in extensions
        ]

    @staticmethod
    def __write_file(
        df: Union[pd.DataFrame, pd.Series],
        output_name: str,
        output_format: str,
        header=True,
        index=True,
        index_label="",
        name="",
        plot=False,
        plot_type="line",
        plot_n=None,
        write=True,
    ) -> None:

        if name:
            df.name = name

        if write is True:
            getattr(df, f"to_{output_format}")(
                "%s.%s" % (output_name, "xlsx" if output_format == "excel" else "csv"),
                header=header,
                index=index,
                index_label=index_label,
            )

        if plot is True:
            getattr(px, plot_type)(df[:plot_n]).write_html(f"{output_name}.html")
            getattr(px, plot_type)(df[:plot_n]).write_image(f"{output_name}.png")


class Tokenizer():

    def __init__(self, stop_words: list, **kwargs):
        self.stop_words = stop_words

    def tokenize(self, sentence: str):
        return [
            x
            .translate(ACCENT_REPLACEMENTS)
            .translate(CHARACTER_REPLACEMENTS)
            for x in
                self.clear_emojis(sentence)
                .lower()
                .split()
            if
                len(x) > 2
            and
                x.strip(VALID_CHARACTERS) not in self.stop_words
            and
                not self.is_number(x)
            and
                not any(x.startswith(_) for _ in IGNORE_STARTS_WITH)
        ]

    @staticmethod
    def is_number(str_word):
        try:
            int(str_word)
        except:
            try:
                float(str_word)
            except:
                return False
        return True

    @staticmethod
    def clear_emojis(str_text, replace_with=r' '):
        return re\
            .compile("["
                u"\U0001F600-\U0001F64F"  # emoticons
                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                u"\U00002702-\U000027B0"  # extra (1)
                u"\U000024C2-\U0001F251"  # extra (2)
                u"\U0000200B-\U0000200D"  # zero width
                "]+", flags=re.UNICODE)\
            .sub(replace_with, str_text)

    @staticmethod
    def ngrams(tokens: list, n=2):
        return [
            g
            for g in list(nltk.ngrams(tokens, n))
            if len(set(g)) == n
        ]


def argsparse() -> dict:
    '''
    Returns dictionary of parameters for execution.
    '''
    argparser = ArgumentParser()

    argparser.add_argument("input_name",
                           help=f"List of files or folder to parse comments from",
                           nargs="+")

    argparser.add_argument("-o", "--output-name",
                           default=OUTPUT_NAME,
                           help=f"Output folder name (default: {OUTPUT_NAME})")

    argparser.add_argument("--allow-selfloops",
                           action="store_false",
                           dest="remove_selfloops",
                           help="Allow node connections to itself in graphs")

    argparser.add_argument("--datetime-source",
                           default=DATETIME_SOURCE,
                           help=f"Datetime format to convert string from (default: 'DD/MM/YYYY HH:MM:SS')")

    argparser.add_argument("--datetime-target",
                           default=DATETIME_TARGET,
                           help=f"Datetime format to convert string to (default: 'YYYY-MM-DD HH:MM:SS')")

    argparser.add_argument("--engine",
                           default=ENGINE,
                           help="Pandas engine: 'c' (default), 'python' or 'python-fwf'")

    argparser.add_argument("--extensions",
                           default=EXTENSIONS,
                           help=f"Accepted extensions (default: '{EXTENSIONS}')")

    argparser.add_argument("--graph-format",
                           default=GRAPH_FORMAT,
                           help="from NetworkX: 'gexf' (default), 'gml', 'graphml', 'pajek', 'shp'")

    argparser.add_argument("--max-word-nodes",
                           default=MAX_WORD_NODES,
                           help=f"Maximum number of nodes in word and n-gram graphs (default: {MAX_WORD_NODES})",
                           type=int)

    argparser.add_argument("--n-grams",
                           default=N_GRAMS,
                           help=f"Number of grams to consider (default: {N_GRAMS})",
                           type=int)

    argparser.add_argument("--n-replies",
                           default=N_REPLIES,
                           help=f"Number of top replies per threads to consider (default: {N_REPLIES})",
                           type=int)

    argparser.add_argument("--n-threads",
                           default=N_THREADS,
                           help=f"Number of top threads per file to consider (default: {N_THREADS})",
                           type=int)

    argparser.add_argument("--node-zero",
                           default=NODE_ZERO,
                           help=f"Origin node name to use (default: {NODE_ZERO})")

    argparser.add_argument("--output-format",
                           default=OUTPUT_FORMAT,
                           help="Output format: 'csv' (default) or 'excel'")

    argparser.add_argument("--skiprows",
                           default=SKIPROWS,
                           help=f"Number of rows to skip when loading file (default: {SKIPROWS})",
                           type=int)

    return vars(argparser.parse_args())


if __name__ == "__main__":
    args = argsparse()
    ParseComments(engine=args.pop("engine")).parse_comments(**args)