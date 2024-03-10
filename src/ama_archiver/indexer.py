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

from ama_archiver.constants import URL_TEMPLATE

import requests as r
from bs4 import BeautifulSoup

from pathlib import Path
import sqlite3
from typing import List
import logging

def fetch_raw_index(url: str) -> str:
    """
    Fetches HTML from specified URL, and returns it as a str-object.

    - url: Source to get HTML from.
    """
    logging.info("url = %r", url)
    response = r.get(url)
    # Note: raises error
    #response.raise_for_status()
    logging.info("Now fetching text from requests.get(url)")
    raw_index = response.text
    logging.info("Text-fetch successful. Returning requests.get(url).text")
    return raw_index

def save_raw_index(raw_index: str, odir_path: Path, ofname: str) -> None:
    """
    Saves 'raw_index' str to the file './odir_path/ofname'.

    - raw_index: Raw HTML as str.
    - odir_path: Path of output directory.
    - ofname: Name of file to save `raw_index` to.
    """
    logging.info("raw_index = (...)")
    logging.info("odir_path = %r", odir_path)
    logging.info("ofname = %r", ofname)
    full_opath = odir_path.joinpath(ofname)
    if not odir_path.is_dir():
        logging.info("%r does not exist. Making directory.", odir_path)
        odir_path.mkdir(exist_ok=True)
    logging.info("Writing 'raw_index' to %r", full_opath)
    full_opath.write_text(raw_index)

def compile_ama_index(raw_index: str, start_text: str) -> List[dict]:
    """
    Compiles index := {cc_name: [name for name in fan_names]} from HTML of the form: <p><strong>cc_name1</strong></p>
    <p><a href=url>fan_name1</a></p>
    <p><a href=url>fan_name2</a></p>
    <p><a href=url>fan_name3</a></p>
    <hr />
    <p><strong>cc_name2</strong></p>

    - raw_index: Raw HTML as str.
    - start_text: The text to search <strong> tags for.
    """
    logging.info("raw_index = (...)")
    logging.info("start_text = %r", start_text)
    logging.info("Creating BeautifulSoup object from 'raw_index'.")
    ama_soup = BeautifulSoup(raw_index, 'html.parser')
    for strong in ama_soup.find_all("strong"):
        # find first strong node with FIRST_CC_NAME, and set to 'strong'
        if strong.text != start_text:
            continue
        current_node = strong
        cc_name = strong.text[:-1]
        logging.info("'start_text' found in tree: %r. Setting as 'cc_name'.", cc_name)
        break
    ama_index = []
    try:
        current_node
    except UnboundLocalError as ul_err:
        logging.critical("Unable to find <strong> node with: %r", start_text)
        raise ul_err
    for sibling in current_node.parent.next_siblings:
        # skipping blanks
        if str(sibling) == "\n":
            continue
        elif sibling.name == "hr":
            continue
        # Determine if cc or fan. Create tree: {cc_name -> [name for name in fan_names]}
        if sibling.find("strong") is not None:
            cc_name = sibling.strong.text[:-1]
            logging.info("New 'cc_name' found: %r", cc_name)
        elif sibling.find("a") is not None:
            a = sibling.find("a")
            fan_name = a.text
            url = a['href']
            ama_record = {
                "fan_name": fan_name,
                "cc_name": cc_name,
                "url": url,
            }
            logging.debug("New fan question found: %r. Appending to index.", ama_record)
            ama_index.append(ama_record)
        else:
            raise Exception("Unexpected tag not found. Not strong, a, hr, or NaviString: %r", sibling)
    logging.info("A total of %d record(s) were found.")
    return ama_index

def identify_duplicates(ama_index: List[dict]) -> List[dict]:
    """
    Compiles a list of duplicate URLs for a given (cc_name, fan_name) pair, and returns that list.

    - ama_index: List of ama_index records.
    """
    #sqlite> SELECT * FROM ama_index WHERE url_id IN (SELECT url_id FROM ama_index GROUP BY url_id HAVING COUNT(url_id) > 1);
    #cc_name      fan_name    url_id    
    #-----------  ----------  ----------
    #Daron Nefcy  Joe_Zt      evw8mcl       -> evw8g9o
    #Daron Nefcy  ShinySatur  evw8mcl   
    #Adam McArth  Hiofshao_Q  evwbcnk   
    #Adam McArth  sloppyjeau  evwbcnk       -> evwbgza
    url_dict = {}
    for ama_record in ama_index:
        cc_name = ama_record["cc_name"]
        fan_name = ama_record["fan_name"]
        url = ama_record["url_id"]
        if url in url_dict:
            url_dict[url].append((cc_name, fan_name))
        else:
            url_dict[url] = [(cc_name, fan_name)]
    dup_records = []
    for url, url_record in url_dict.items():
        if len(url_record) == 1:
            continue
        dup_records.append( {url: url_record} )
    for indexno, dup in enumerate(dup_records, start=1):
        logging.info("duplicate %d found: %r", indexno, dup)
    return dup_records

def get_urlid(url: str) -> str:
    """
    Extracts the URL id from a given URL string.

    - url: URL whose url_id is to be extracted.
    """
    url_id = url.split("/")[-2]
    return url_id

def get_url(url_id: str) -> str:
    """
    Forms a complete old-Reddit URL from the url_id parameter, and returns it as a str-object.

    - url_id: The part of the URL used to form a complete URL.
    """
    url_template = list(URL_TEMPLATE)
    url_template[-2] = url_id
    url = "/".join(url_template)
    #url = f"https://www.reddit.com/r/StarVStheForcesofEvil/comments/cll9u5/star_vs_the_forces_of_evil_ask_me_anything/{url_id}/?context=3"
    return url.replace("www.reddit.com", "old.reddit.com")

def save_ama_index(ama_index: List[dict], full_dbpath: Path) -> None:
    """
    Saves ama_index := [{field1: value1, field2: value2, ...}] to full_dbpath in SQL format.

    - ama_index: List of ama_index dict-records.
    - full_dbpath: Tells function where to save `ama_index`
    """
    if full_dbpath.exists():
        logging.info("%s already exists. Skipping.")
    with sqlite3.connect(full_dbpath) as cnxn:
        crs = cnxn.execute("""
            CREATE TABLE IF NOT EXISTS ama_index(
                cc_name TEXT NOT NULL,
                fan_name TEXT NOT NULL,
                url_id TEXT NOT NULL
            );
            """)
        crs.executemany("INSERT INTO ama_index VALUES(:cc_name, :fan_name, :url_id);", ama_index)

# TODO: Add test for this function
def load_ama_index(full_dbpath: Path) -> List[dict]:
    """
    Loads from `full_dbpath` the table `ama_index` as List[dict] object.

    - full_dbpath: Tells function where to find `ama_index`
    """
    with sqlite3.connect(full_dbpath) as cnxn:
        cnxn.row_factory = sqlite3.Row
        res = cnxn.execute("""
            SELECT cc_name, fan_name, url_id FROM ama_index;
        """)
        ama_index = [dict(row) for row in res.fetchall()]
    return ama_index

