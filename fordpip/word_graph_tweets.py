#!/usr/bin/env python3

import os
import os.path as osp
from argparse import ArgumentParser
from string import punctuation
from typing import Optional, Union

import networkx as nx
import pandas as pd

from .lib_stopwords import STOPWORDS

ACCENT_REPLACEMENTS = {
    ord("á"): "a", ord("ã"): "a", ord("â"): "a",
    ord("à"): "a", ord("è"): "e", ord("ê"): "e",
    ord("é"): "e", ord("í"): "i", ord("ì"): "i",
    ord("ñ"): "n", ord("ò"): "o", ord("ó"): "o",
    ord("ô"): "o", ord("õ"): "o", ord("ù"): "u",
    ord("ú"): "u", ord("ü"): "u", ord("ç"): "c"}

VALID_CHARACTERS = "_@#" # '
INVALID_CHARACTERS = punctuation
INVALID_CHARACTERS += "'\\\"–—¡¿…‘’“”„,•·|"

INVALID_CHARACTERS = "".join(
    set(INVALID_CHARACTERS) - set(VALID_CHARACTERS)
)


def wordgraph_tweets(
    path: str,
    words: Optional[Union[int, str, list]] = None,
    insert_words: Optional[list] = [],
    exclude_words: Optional[list] = [],
    columns: list = ["Tweet Text"],
    skiprows: int = 6
) -> None:
    """
    Generate word graph from ExportComments tweet datasets.
    """
    assert osp.exists(path), f"Path '{path}' is not a valid file or folder."

    if osp.isfile(osp.abspath(path)):
        filenames = [path]
    elif osp.isdir(osp.abspath(path)):
        filenames = [osp.join(path, f)
                     for f in os.listdir(path)
                     if f.endswith(".csv")
                     or f.endswith(".xlsx")]
        print(f"Selected {len(filenames)} files: {[osp.basename(f) for f in filenames]}")

    df = pd.concat([pd.read_excel(filename, skiprows=skiprows)\
                   if filename.endswith(".xlsx") else\
                   pd.read_csv(filename, skiprows=skiprows)
                   for filename in filenames])

    df.drop_duplicates(
        subset=["Tweet ID (click to view url)"],
        keep="last",
        inplace=True
    )

    if not words or (type(words) == str and words.isnumeric()):
        words = df.loc[:, columns]\
                  .astype(str)\
                  .apply(" ".join, axis=1)\
                  .apply(lambda x: [x.strip(INVALID_CHARACTERS) for x in x.lower().split()])\
                  .explode()\
                  .value_counts()\
                  .drop(STOPWORDS, errors="ignore")\
                  .drop(exclude_words or [], errors="ignore")\
                  .drop("", errors="ignore")\
                  .head(words or 5)
        print(f"Top words: {words.to_dict()}")
        words = words.index.tolist()

    if type(words) == str:
        words = [_.strip() for _ in words.split(",")]

    if type(insert_words) == str:
        insert_words = [_.strip() for _ in insert_words.split(",")]
    elif insert_words is None:
        insert_words = []

    if type(exclude_words) == str:
        exclude_words = [_.strip() for _ in exclude_words.split(",")]
    elif exclude_words is None:
        exclude_words = []

    users = pd.DataFrame(
        {
            "tweets": 1,
            "retweets": df["Retweets"].fillna(0).astype(int).values.tolist(),
            "comments": df["Comments"].fillna(0).astype(int).values.tolist(),
            "favorites": df["Favorites"].fillna(0).astype(int).values.tolist(),
        },
        index=df["Username"].values.tolist()
    )\
    .fillna(0)\
    .groupby(df["Username"].values.tolist())\
    .sum(0)

    tweets = pd.DataFrame(
        {
            "text": df["Tweet Text"].values.tolist(),
            "retweets": df["Retweets"].fillna(0).astype(int).values.tolist(),
            "comments": df["Comments"].fillna(0).astype(int).values.tolist(),
            "favorites": df["Favorites"].fillna(0).astype(int).values.tolist(),
        },
        index=df["Tweet ID (click to view url)"].values.tolist()
    )

    G, edges = nx.Graph(), {}

    for index, row in df.iterrows():
        for word in words + insert_words:
            if word in insert_words\
            or word.lower() in row["Tweet Text"].lower():
                G.add_node(row["Username"],
                           tweets=users.loc[row["Username"], "tweets"],
                           retweets=users.loc[row["Username"], "retweets"],
                           comments=users.loc[row["Username"], "comments"],
                           favorites=users.loc[row["Username"], "favorites"],
                           author_followers=row["Author Followers"],
                           author_friends=row["Author Friends"],
                           author_statuses=row["Author Statuses"],
                           author_verified=row["Author Verified"])

                edges[(row["Username"], word.lower())] = edges.get((row["Username"], word.lower()), []) +\
                                                         [row["Tweet ID (click to view url)"]]

    top_favorite = {k: sorted(v, key=lambda x: tweets.loc[x, "favorites"], reverse=True)[0]
                    for k, v in edges.items()}

    G.add_edges_from([
        (edge[0], edge[1], {"weight": len(ids),
                            "top_favorite_id": top_favorite[edge],
                            "top_favorite_text": tweets.loc[top_favorite[edge], "text"]})
        for edge, ids in edges.items()
        if edge[0] != edge[1]
    ])

    nx.write_graphml(G, "word_graph.graphml")

def parse_args():
    parser = ArgumentParser(description="Generate a graph from a csv or xls file.")

    parser.add_argument("filename",
                        help="The filename of the csv or xls file.")

    parser.add_argument("--words",
                        type=lambda x: [x.strip() for x in x.split(",")],
                        help="The number of words or the expressions to filter (comma separated). "
                             "Default: 5 most frequent words.")

    parser.add_argument("--columns",
                        type=lambda x: [x.strip() for x in x.split(",")],
                        default=["Tweet Text"],
                        help="The columns to filter (comma separated). "
                             "Default: 'Tweet Text'.")

    parser.add_argument("--skiprows",
                        type=int,
                        default=6,
                        help="The number of rows to skip. Default: 6.")

    return parser.parse_args()


if __name__ == "__main__":
    args = vars(parse_args())
    word_graph_tweets(**args)
