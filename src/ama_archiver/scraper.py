#!/usr/bin/python3
"""
This module contains functions that fetch and store queries from the source.
- fetch_ama_query: Fetches text Q&A data from Reddit as text, and returns it as a dict[str, str].
- fetch_ama_queries: Iterates over index, and fetches Q&A data for each entry in the index.
- save_ama_query: Saves a given ama_query, provided it's got the right fields.
"""

import requests as r
from bs4 import BeautifulSoup

from pathlib import Path
import sqlite3
import logging

def fetch_ama_query(url: str, ama_query: dict) -> None:
    """
    Fetches `question_text` and `answer_text` values for a given URL.

    - url: source whence data is to be fetched.
    - ama_query: dict to store fetched data. Initialize outside function.

    return: {'question_text': ..., 'answer_text': ...}
    """
    # new version no longer works for scraping
    response = r.get(url.replace("www.reddit.com", "old.reddit.com"))
    soup = BeautifulSoup(response.text, "html.parser")
    # personal observations indicate that comments are contained in HTML tags of this class
    class_ = "usertext-body"
    # Note: assumes that length of query is at least three!
    for indexno, comment in enumerate(soup.find_all(class_=class_)):
        # personal observations indicate the first is of no importance
        if indexno == 0:
            continue
        elif indexno == 1:
            question_text = comment.text
            ama_query["question_text"] = question_text
        elif indexno == 2:
            answer_text = comment.text
            ama_query["answer_text"] = answer_text

def save_ama_query_to_db(ama_query: dict, full_dbpath: Path) -> None:
    """
    Creates 'ama_queries' table in `full_dbpath`, and saves `ama_query` into the table.

    - ama_query: populated dict to be loaded into the database.
    - full_dbpath: tells the function where the database file is.
    """
    #logging.info("Saving `ama_query` to %s", full_dbpath)
    #ama_query = {field: value.replace("\\n", "") for field, value in ama_query.items()}
    with sqlite3.connect(full_dbpath) as cnxn:
        crs = cnxn.execute("""
                CREATE TABLE IF NOT EXISTS ama_queries(
                    url_id TEXT PRIMARY KEY,
                    question_text TEXT NOT NULL,
                    answer_text TEXT NOT NULL
                );
                """)
        crs.execute("INSERT INTO ama_queries VALUES(:url_id, :question_text, :answer_text);", ama_query)

