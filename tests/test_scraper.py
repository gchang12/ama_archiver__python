#!/usr/bin/python3
"""
Contains tests for the functions defined in the 'scraper' module.
- fetch_ama_query
- fetch_ama_queries
"""

from ama_archiver import scraper

from pathlib import Path
import sqlite3
import logging
import unittest
from unittest.mock import patch

class AmaScraperTest(unittest.TestCase):
    """
    Contains tests to see that 'scraper' module works as intended.
    """

    def setUp(self):
        """
        Contains objects meant as essential parameters for 'scraper' module.

        url: Sample of URL to scrape Q&A from.
        url_id: Substring of URL that identifies a URL.
        question_text: First item to be scraped.
        answer_text: Second item to be scraped.
        ama_query: Sample record of what is to be returned from scraping operations.
        """
        self.url = "https://old.reddit.com/r/StarVStheForcesofEvil/comments/cll9u5/star_vs_the_forces_of_evil_ask_me_anything/evw3fne/?context=3"
        self.url_id = "spongebob"
        self.question_text = "Do androids dream of electric sheep?"
        self.answer_text = "Ask Philip K. Dick, guy."
        self.ama_query = {
            "url_id": self.url_id,
            "question_text": self.question_text,
            "answer_text": self.answer_text,
        }
        self.odir_path = Path("tests", "mock-output")
        self.odir_path.mkdir(exist_ok=True)

    @patch("requests.get")
    def test_fetch_ama_query(self, mock_rget):
        """
        Tests that function loads expected parameters into dict parameter.
        """
        url = self.url
        url_id = self.url_id
        actual = {}
        mock_rget.return_value.text = \
        f"""
            <div class='usertext-body may-blank-within md-container'>
                <p>Nothing to see here, folks. This is skipped.</p>
            </div>
            <div class='usertext-body may-blank-within md-container'>
                <p>{self.question_text}</p>
            </div>
            <div class='usertext-body may-blank-within md-container'>
                <p>{self.answer_text}</p>
            </div>
        """.strip()
        while set(actual) != {"question_text", "answer_text"}:
            scraper.fetch_ama_query(url, actual)
        actual["url_id"] = url_id
        expected = self.ama_query
        self.assertDictEqual(actual, expected)

    def test_save_ama_query_to_db(self):
        """
        Tests that save-operation is successful, and that saved query matches loaded query.
        """
        ama_query = self.ama_query
        full_dbpath = self.odir_path.joinpath("ama_queries-save_test.db")
        if full_dbpath.exists():
            full_dbpath.unlink()
        scraper.save_ama_query_to_db(ama_query, full_dbpath)
        actual = {}
        with sqlite3.connect(full_dbpath) as cnxn:
            cnxn.row_factory = sqlite3.Row
            result = cnxn.execute("SELECT url_id, question_text, answer_text FROM ama_queries;")
            test_record = result.fetchone()
            for field in test_record.keys():
                actual[field] = test_record[field]
        full_dbpath.unlink()
        expected = self.ama_query
        self.assertDictEqual(actual, expected)

    def test_load_ama_queries_from_db(self):
        """
        Tests that load-operation is successful, and that loaded query matched saved query.
        """
        generic_query = {
            "url_id": "url_id",
            "question_text": "question_text",
            "answer_text": "answer_text",
            }
        expected = [
            self.ama_query,
            generic_query,
            ]
        full_dbpath = self.odir_path.joinpath("ama_queries-load_test.db")
        full_dbpath.unlink(missing_ok=True)
        with sqlite3.connect(full_dbpath) as cnxn:
            crs = cnxn.execute("""
                    CREATE TABLE IF NOT EXISTS ama_queries(
                        url_id TEXT PRIMARY KEY,
                        question_text TEXT NOT NULL,
                        answer_text TEXT NOT NULL
                    );
                    """)
            crs.executemany("INSERT INTO ama_queries VALUES(:url_id, :question_text, :answer_text);", expected)
        actual = scraper.load_ama_queries_from_db(full_dbpath)
        full_dbpath.unlink()
        def original_order(record: dict):
            """
            For ordering the dict-list in the order per `expected`.
            """
            return expected.index(record)
        actual.sort(key=original_order)
        self.assertListEqual(expected, actual)

