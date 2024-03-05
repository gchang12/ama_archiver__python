#!/usr/bin/python3
"""
"""

FIRST_CC_NAME = "Daron Nefcy"
LC_URL = "https://old.reddit.com/r/StarVStheForcesofEvil/comments/clnrdv/link_compendium_of_questions_and_answers_from_the/"
LC_FNAME = "link-compendium"
LC_DBNAME = "ama_database"
ODIR_NAME = "output"

import requests as r
from bs4 import BeautifulSoup


from pathlib import Path
import sqlite3
from typing import List

def fetch_raw_index() -> str:
    response = r.get(LC_URL)
    response.raise_for_status()
    raw_index = response.text
    return raw_index

def save_raw_index(raw_index: str) -> None:
    odir_path = Path(ODIR_NAME)
    full_opath = odir_path.joinpath(LC_FNAME + ".html")
    if not odir_path.is_dir():
        odir_path.mkdir()
    full_opath.write_text(raw_index)

def compile_ama_index(raw_index: str) -> List[dict]:
    ama_soup = BeautifulSoup(raw_index, 'html.parser')
    for strong in ama_soup.find_all("strong"):
        # find first strong node with FIRST_CC_NAME, and set to 'strong'
        #print(strong)
        if strong.text != FIRST_CC_NAME + ":":
            continue
        current_node = strong
        #print([sibling for sibling in current_node.parent.next_siblings])
        cc_name = strong.text[:-1]
        break
    ama_index = []
    for sibling in current_node.parent.next_siblings:
        # skipping blanks
        if str(sibling) == "\n":
            continue
        elif sibling.name == "hr":
            continue
        # Determine if cc or fan. Create tree: {cc_name -> [name for name in fan_names]}
        if sibling.find("strong") is not None:
            cc_name = sibling.strong.text
        elif sibling.find("a") is not None:
            a = sibling.find("a")
            fan_name = a.text
            url = a['href']
            ama_index.append(
                {
                    "fan_name": fan_name,
                    "cc_name": cc_name,
                    "url": url,
                }
            )
        else:
            raise Exception("Unexpected tag not found. Not strong, a, hr, or NaviString: %r", sibling)
    return ama_index

def save_ama_index(ama_index: List[dict]) -> None:
    full_dbpath = Path(ODIR_NAME, LC_DBNAME + ".db")
    with sqlite3.connect(full_dbpath) as cnxn:
        crs = cnxn.execute("CREATE TABLE IF NOT EXISTS ama_index(cc_name TEXT, fan_name TEXT, url TEXT);")
        crs.executemany("INSERT INTO ama_index VALUES(:cc_name, :fan_name, :url);", ama_index)

def fetch_ama_query(url: str, ama_query):
    # new version no longer works for scraping
    response = r.get(url.replace("www.reddit.com", "old.reddit.com"))
    soup = BeautifulSoup(response.text, "html.parser")
    ama_query.update({"url": url})
    # Note: assumes that length of query is at least three!
    extra_lines = []
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
        else:
            extra_lines.append(comment.text)
    ama_query["extra_text"] = "\n".join(extra_lines)
    return ama_query

def fetch_ama_queries(ama_index: List[dict]) -> None:
    # compile entries from sqlite database
    ama_queries = []
    expected_fields = {"url", "question_text", "answer_text", "extra_text"}
    total_num_queries = len(ama_index)
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

def save_ama_queries(ama_queries: List[dict]) -> None:
    full_dbpath = Path(ODIR_NAME, LC_DBNAME + ".db")
    print("Saving queries to %s" % full_dbpath)
    with sqlite3.connect(full_dbpath) as cnxn:
        crs = cnxn.execute("CREATE TABLE IF NOT EXISTS ama_queries(url TEXT, question_text TEXT, answer_text TEXT, extra_text TEXT);")
        crs.executemany("INSERT INTO ama_queries VALUES(:url, :question_text, :answer_text, :extra_text);", ama_queries)

if __name__ == '__main__':
    odir_path = Path(ODIR_NAME)
    full_opath = odir_path.joinpath(LC_FNAME + ".html")
    if not full_opath.exists():
        raw_index = fetch_raw_index()
    else:
        raw_index = full_opath.read_text()
    save_raw_index(raw_index)
    ama_index = compile_ama_index(raw_index)
    #save_ama_index(ama_index)
    ama_queries = fetch_ama_queries(ama_index)
    save_ama_queries(ama_queries)
