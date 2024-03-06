#!/usr/bin/python3
"""
This module defines functions that will help compile and validate an index for the Q&A session exchanges.
- fetch_raw_index: Fetches HTML from the link-compendium URL, and returns it as a str.
- save_raw_index: Saves the raw index into the specified output file.
- compile_ama_index: Compiles the Q&A index into a list of dict objects.
- save_ama_index: Saves a Q&A index into a database file. 
- identify_duplicates: Identifies (cc_name, fan_name) pairs whose URLs appear more than once in the index.
- identify_url_template: Identifies the shortest substring that is contained in all URLs. For truncating values in URL field. 
- get_full_url: Returns full URL for the given url_id (i.e. str that completes the url template, and transforms it into a functioning URL)
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

def fetch_raw_index(url: str) -> str:
    """
    """
    response = r.get(url)
    response.raise_for_status()
    raw_index = response.text
    return raw_index

def save_raw_index(raw_index: str, odir_path: str, ofname: str) -> None:
    """
    """
    full_opath = odir_path.joinpath(ofname + ".html")
    if not odir_path.is_dir():
        odir_path.mkdir()
    full_opath.write_text(raw_index)

def compile_ama_index(raw_index: str, stop_text: str) -> List[dict]:
    """
    """
    ama_soup = BeautifulSoup(raw_index, 'html.parser')
    for strong in ama_soup.find_all("strong"):
        # find first strong node with FIRST_CC_NAME, and set to 'strong'
        #print(strong)
        if strong.text != stop_text + ":":
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

def save_ama_index(ama_index: List[dict], full_dbpath: Path) -> None:
    """
    """
    #full_dbpath = Path(ODIR_NAME, LC_DBNAME + ".db")
    with sqlite3.connect(full_dbpath) as cnxn:
        crs = cnxn.execute("CREATE TABLE IF NOT EXISTS ama_index(cc_name TEXT, fan_name TEXT, url TEXT);")
        crs.executemany("INSERT INTO ama_index VALUES(:cc_name, :fan_name, :url);", ama_index)

def identify_duplicates(ama_index: List[dict]):
    """
    Identifies duplicate URLs for a given (cc_name, fan_name) pair.
    """
    pass

def identify_url_template(ama_index: List[dict]):
    """
    """
    pass

if __name__ == '__main__':
    odir_path = Path(ODIR_NAME)
    full_opath = odir_path.joinpath(LC_FNAME + ".html")
    if not full_opath.exists():
        raw_index = fetch_raw_index(LC_URL)
    else:
        raw_index = full_opath.read_text()
    save_raw_index(raw_index, odir_path, LC_FNAME)
    ama_index = compile_ama_index(raw_index, FIRST_CC_NAME)
    full_dbpath = odir_path.joinpath(LC_DBNAME + ".db")
    #save_ama_index(ama_index)
    ama_queries = fetch_ama_queries(ama_index)
    save_ama_queries(ama_queries, full_dbpath)
