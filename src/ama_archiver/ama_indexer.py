#!/usr/bin/python3
"""
This module defines functions that will help compile and validate an index for the Q&A session exchanges.
- fetch_raw_index: Fetches HTML from the link-compendium URL, and returns it as a str.
- save_raw_index: Saves the raw index into the specified output file.
- compile_ama_index: Compiles the Q&A index into a list of dict objects.
- save_ama_index: Saves a Q&A index into a database file. 
- identify_duplicates: Identifies (cc_name, fan_name) pairs whose URLs appear more than once in the index.
- _identify_url_template: Identifies the shortest substring that is contained in all URLs. For truncating values in URL field. 
- get_urlid: Returns the url ID for a given URL.
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
    Fetches HTML from specified URL, and returns it as a str-object.
    """
    response = r.get(url)
    # Note: raises error
    #response.raise_for_status()
    raw_index = response.text
    return raw_index

def save_raw_index(raw_index: str, odir_path: Path, ofname: str) -> None:
    """
    Saves 'raw_index' str to the file './odir_path/ofname.html'.
    """
    full_opath = odir_path.joinpath(ofname + ".html")
    if not odir_path.is_dir():
        odir_path.mkdir()
    full_opath.write_text(raw_index)

def compile_ama_index(raw_index: str, start_text: str) -> List[dict]:
    """
    Compiles index := {cc_name: [name for name in fan_names]} from HTML of the form:

    <p><strong>cc_name1</strong></p>
    <p><a href=url>fan_name1</a></p>
    <p><a href=url>fan_name2</a></p>
    <p><a href=url>fan_name3</a></p>
    <hr />
    <p><strong>cc_name2</strong></p>
    """
    ama_soup = BeautifulSoup(raw_index, 'html.parser')
    for strong in ama_soup.find_all("strong"):
        # find first strong node with FIRST_CC_NAME, and set to 'strong'
        #print(strong)
        if strong.text != start_text + ":":
            continue
        current_node = strong
        #print([sibling for sibling in current_node.parent.next_siblings])
        cc_name = strong.text[:-1]
        break
    ama_index = []
    try:
        current_node
    except UnboundLocalError as ul_err:
        print(f"Unable to find <strong> node with: '{start_text}'")
        raise ul_err
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

def identify_duplicates(ama_index: List[dict]) -> List[dict]:
    """
    Compiles a list of duplicate URLs for a given (cc_name, fan_name) pair, and returns that list.
    """
    url_dict = {}
    for ama_record in ama_index:
        cc_name = ama_record["cc_name"]
        fan_name = ama_record["fan_name"]
        url = ama_record["url"]
        if url in url_dict:
            url_dict[url].append((cc_name, fan_name))
        else:
            url_dict[url] = [(cc_name, fan_name)]
    dup_records = []
    for url, url_record in url_dict.items():
        if len(url_record) == 1:
            continue
        dup_records.append( {url: url_record} )
    return dup_records

def _identify_url_template(ama_index: List[dict]):
    """
    Identifies which substring is common to all URLs in the ama_index.
    """
    # start with base.
    # compare to next. diminish if no match
    url_list = []
    for ama_record in ama_index:
        url = ama_record["url"]
        url_list.append(url)

# Note: I cheated to write these two functions.
#       I didn't formulate an algorithm to determine the longest substring common to all URLs
def get_urlid(url: str) -> str:
    """
    Extracts the URL id from a given URL string.
    """
    url_id = url.split("/")[-2]
    return url_id

def get_url(url_id: str) -> str:
    """
    Forms a complete URL from the url_id parameter, and returns it as a str-object.
    """
    url = f"https://www.reddit.com/r/StarVStheForcesofEvil/comments/cll9u5/star_vs_the_forces_of_evil_ask_me_anything/{url_id}/?context=3"
    return url

# Note: Why do we need an extra table?
# Answer: In case some duplicates are found, and we must correct the url_id's
def save_ama_index(ama_index: List[dict], full_dbpath: Path) -> None:
    """
    Saves ama_index := [{field1: value1, field2: value2, ...}] to full_dbpath in SQL format.
    """
    #full_dbpath = Path(ODIR_NAME, LC_DBNAME + ".db")
    with sqlite3.connect(full_dbpath) as cnxn:
        crs = cnxn.execute("CREATE TABLE IF NOT EXISTS ama_index(cc_name TEXT, fan_name TEXT, url_id TEXT);")
        crs.executemany("INSERT INTO ama_index VALUES(:cc_name, :fan_name, :url_id);", ama_index)

if __name__ == '__main__':
    pass