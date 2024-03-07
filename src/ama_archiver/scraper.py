#!/usr/bin/python3
"""
This module contains functions that fetch and store queries from the source.
- fetch_ama_query: Fetches text Q&A data from Reddit as text, and returns it as a dict[str, str].
- fetch_ama_queries: Iterates over index, and fetches Q&A data for each entry in the index.
- save_ama_query: Saves a given ama_query, provided it's got the right fields.
"""
# TODO: Document and touch-up
# TODO: Add unit tests to complement these functions
# TODO: Figure out what other src/* files do in the usual way.

import requests as r
from bs4 import BeautifulSoup

from pathlib import Path
import sqlite3
from typing import List
import logging

def fetch_ama_query(url: str, ama_query: dict[str, str]):
    """
    """
    # new version no longer works for scraping
    response = r.get(url.replace("www.reddit.com", "old.reddit.com"))
    soup = BeautifulSoup(response.text, "html.parser")
    ama_query.update({"url": url})
    # Note: assumes that length of query is at least three!
    #extra_lines = []
    for indexno, comment in enumerate(soup.find_all(class_="usertext-body")):
        # personal observations indicate the first is of no importance
        if indexno == 0:
            continue
        elif indexno == 1:
            question_text = comment.text
            ama_query["question_text"] = question_text
        elif indexno == 2:
            answer_text = comment.text
            ama_query["answer_text"] = answer_text
        #else:
            #extra_lines.append(comment.text)
    # Note: 'extra_text' has an indeterminate number of lines
    #ama_query["extra_text"] = "\n".join(extra_lines)
    return ama_query

def fetch_ama_queries(ama_index: List[dict]) -> List[dict]:
    """
    """
    # TODO: save ama_query as soon as it is retrieved
    # TODO: check if ama_query exists; attempt to retrieve if not; skip if yes.
    # compile entries from sqlite database
    ama_queries = []
    expected_fields = {"url", "question_text", "answer_text"}
    total_num_queries = len(ama_index)
    # should record this somewhere
    total_num_tries = 1
    # record partial retrieval results
    for recordno, record in enumerate(ama_index, start=1):
        cc_name = record['cc_name']
        fan_name = record['fan_name']
        url = record['url']
        ama_query = {}
        counter = 0
        print("Attempting to fetch data for record: %d/%d" % (recordno, total_num_queries))
        while set(ama_query.keys()) != expected_fields:
            fetch_ama_query(url, ama_query)
            # only print upon error, and without concealing the error
            total_num_tries += 1
            counter += 1
            print("Fetching from %r. Try: %d" % (url, counter))
        ama_queries.append(ama_query)
    return ama_queries

# TODO: Phase out soon.
def save_ama_queries(ama_queries: List[dict], full_dbpath: Path) -> None:
    """
    """
    #full_dbpath = Path(ODIR_NAME, LC_DBNAME + ".db")
    print("Saving queries to %s" % full_dbpath)
    with sqlite3.connect(full_dbpath) as cnxn:
        crs = cnxn.execute("CREATE TABLE IF NOT EXISTS ama_queries(url TEXT, question_text TEXT, answer_text TEXT);")
        crs.executemany("INSERT INTO ama_queries VALUES(:url, :question_text, :answer_text);", ama_queries)

if __name__ == '__main__':
    pass
