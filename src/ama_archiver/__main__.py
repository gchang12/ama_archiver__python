#!/usr/bin/python3
"""
Defines functions to compile the Reddit SVTFOE AMA session.
- make_ama_index: Scrapes index from web, reports duplicates, and saves to database.
- validate_urls: Checks database for duplicates in `url_id` column.
- make_ama_queries: Scrapes web for `question_text` and `answer_text`
"""
l
from ama_archiver import indexer, scraper, constants

from pathlib import Path
import logging
from typing import List

FULL_DBPATH = Path(constants.ODIR_NAME, constants.AMA_DBNAME + ".db")

def make_ama_index() -> None:
    """
    Generates SQL database from HTML.

    1. Checks if '{ODIR_NAME}/{LC_FNAME}.html' exists.
    -  If not, it scrapes it off the web, and saves it.
    2. Compiles `ama_index` from output.
    3. Reports the number of duplicate records.
    4. Saves `ama_index` to '{ODIR_NAME}/{LC_DBNAME}.db'
    """
    lc_dirpath = Path(constants.ODIR_NAME)
    lc_filepath = lc_dirpath.joinpath(constants.LC_FNAME + ".html")
    if not lc_filepath.exists():
        logging.info("%s does not exist. Fetching raw index from web.", lc_filepath)
        raw_index = indexer.fetch_raw_index(constants.LC_URL)
        indexer.save_raw_index(raw_index, lc_dirpath, constants.LC_FNAME + ".html")
    raw_index = lc_filepath.read_text()
    ama_index = indexer.compile_ama_index(raw_index, constants.FIRST_CC_NAME + ":")
    for ama_record in ama_index:
        url_id = indexer.get_urlid(ama_record.pop("url"))
        ama_record["url_id"] = url_id
    indexer.identify_duplicates(ama_index)
    indexer.save_ama_index(ama_index, FULL_DBPATH)

def validate_urls() -> None:
    """
    Scans database for duplicate URL strings.

    1. Checks if `url_id` column contains no duplicates in the database.
    2. Reports either absence or presence of duplicates.
    """
    ama_index = indexer.load_ama_index(FULL_DBPATH)
    dup_records = indexer.identify_duplicates(ama_index)
    if dup_records:
        for dup in dup_records:
            print("Duplicate found: %r" % dup)
        raise Exception
    else:
        print("No duplicates found!")

def make_ama_queries() -> None:
    """
    Pings Reddit, and scrapes for `question_text` and `answer_text`

    1. Fetches list of `ama_queries` records fetched so far.
    2. Fetches list of `ama_index` records to iterate over.
    3. For each `ama_record`, fetch and save.
    """
    ama_index = indexer.load_ama_index(FULL_DBPATH)
    ama_queries = scraper.load_ama_queries_from_db(FULL_DBPATH)
    queried_urls = set(row["url_id"] for row in ama_queries)
    num_records = len(ama_index)
    num_pings = 0
    for recordno, ama_record in enumerate(ama_index, start=1):
        url_id = ama_record["url_id"]
        if url_id in queried_urls:
            continue
        ama_query = {}
        url = indexer.get_url(url_id)
        cc_name = ama_record["cc_name"]
        fan_name = ama_record["fan_name"]
        logging.info("Fetching record %d/%d: {cc_name: %s, fan_name: %s}", recordno, num_records, cc_name, fan_name)
        attempt_no = 1
        while set(ama_query) != {"question_text", "answer_text"}:
            try:
                scraper.fetch_ama_query(url, ama_query)
            except r.exceptions.ConnectionError:
                logging.info("Max number of Reddit pings reached for today. Number of pings: %d. Terminating...", num_pings)
            logging.info("Tried to fetch record. Attempt: %d", attempt_no)
            attempt_no += 1
            num_pings += 1
        ama_query["url_id"] = url_id
        scraper.save_ama_query_to_db(ama_query, FULL_DBPATH)
        queried_urls.add(url_id)
    logging.info("All Q&A records successfully scraped. Find output in %r", FULL_DBPATH)

# Run functions here.

logging.basicConfig(level=logging.INFO)

make_ama_index()
validate_urls()
make_ama_queries()
