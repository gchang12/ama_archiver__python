#!/usr/bin/python3
"""
Tests that 'indexer' module functions work as intended.
- fetch_raw_index: Fetches HTML from the link-compendium URL, and returns it as a str.
- save_raw_index: Saves the raw index into the specified output file.
- compile_ama_index: Compiles the Q&A index into a list of dict objects.
- save_ama_index: Saves a Q&A index into a database file. 
- identify_duplicates: Identifies (cc_name, fan_name) pairs whose URLs appear more than once in the index.
- _identify_url_template: Identifies the shortest substring that is contained in all URLs. For truncating values in URL field. 
- get_urlid: Returns the url ID for a given URL.
- get_full_url: Returns full URL for the given url_id (i.e. str that completes the url template, and transforms it into a functioning URL)
"""

from ama_archiver import indexer

import requests as r

from pathlib import Path
import unittest
from unittest.mock import patch
import io
import sqlite3

class AmaIndexerTest(unittest.TestCase):
    """
    Contains tests to validate that indexer module works as intended
    """

    def setUp(self):
        """
        Contains objects that are essential to functioning of indexer module.

        source_url: To fetch data.
        start_text: To determine which node to start at in the HTML tree.
        raw_index: To provide a sample HTML tree to parse.
        ama_index: Expected index to be generated from 'raw_index'.
        url: Sample URL containing exchange from (cc_name, fan_name) = (Daron Nefcy, VeronicaMewniFan)
        url_id: Identifier in sample URL string that identifies the exchange.
        """
        self.source_url = "https://en.wikipedia.org/wiki/Guido_van_Rossum"
        self.start_text = "cc_name1"
        self.raw_index = f"""
            <p><strong>{self.start_text}:</strong></p>

            <p><a href="1">fan_name1</a></p>
            <p><a href="2">fan_name2</a></p>
            <p><a href="1">fan_name3</a></p>
            <hr />
            <p><strong>cc_name2:</strong></p>
            <p><a href="3">fan_name4</a></p>
            <p><a href="4">fan_name5</a></p>
        """
        self.ama_index = [
            {"cc_name": "cc_name1", "fan_name": "fan_name1", "url": "1"},
            {"cc_name": "cc_name1", "fan_name": "fan_name2", "url": "2"},
            {"cc_name": "cc_name1", "fan_name": "fan_name3", "url": "1"},
            {"cc_name": "cc_name2", "fan_name": "fan_name4", "url": "3"},
            {"cc_name": "cc_name2", "fan_name": "fan_name5", "url": "4"},
        ]
        self.url = "https://old.reddit.com/r/StarVStheForcesofEvil/comments/cll9u5/star_vs_the_forces_of_evil_ask_me_anything/evw3fne/?context=3"
        self.url_id = "evw3fne"

    def test_fetch_raw_index(self):
        """
        Tests that the function fetches HTML as str.
        """
        raw_index = indexer.fetch_raw_index(self.source_url)
        self.assertIsInstance(raw_index, str)
        self.assertIn("</html>", raw_index)

    @patch("pathlib.Path.write_text")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.is_dir")
    def test_save_raw_index(self, mock_isdir, mock_mkdir, mock_writetext):
        """
        Tests that raw_index str is saved to file, via mock objects.
        """
        raw_index = "<html></html>"
        odir_path = Path("")
        ofname = "test-html.html"
        vfile = io.StringIO()
        def write_to_vfile(text):
            vfile.write(text)
        mock_writetext.side_effect = write_to_vfile
        mock_isdir.return_value = False
        indexer.save_raw_index(raw_index, odir_path, ofname)
        mock_mkdir.assert_called_once_with()
        self.assertEqual(raw_index, vfile.getvalue())

    def test_compile_ama_index(self):
        """
        Tests that self.raw_index is parsed into the expected list of dict objects.

        Also tests that unexpected exceptions are accounted for.
        """
        raw_index = self.raw_index
        start_text = self.start_text
        expected_index = [
            {"cc_name": "cc_name1", "fan_name": "fan_name1", "url": "1"},
            {"cc_name": "cc_name1", "fan_name": "fan_name2", "url": "2"},
            {"cc_name": "cc_name1", "fan_name": "fan_name3", "url": "1"},
            {"cc_name": "cc_name2", "fan_name": "fan_name4", "url": "3"},
            {"cc_name": "cc_name2", "fan_name": "fan_name5", "url": "4"},
        ]
        actual_index = indexer.compile_ama_index(raw_index, start_text)
        self.assertEqual(actual_index, expected_index)
        with self.assertRaises(Exception):
            raw_index += "\n<p><em>emphasis</em></p>"
            null = indexer.compile_ama_index(raw_index, start_text)
        with self.assertRaises(UnboundLocalError):
            raw_index = raw_index.replace(":", "")
            null = indexer.compile_ama_index(raw_index, start_text)

    def test_identify_duplicates(self):
        """
        Tests that all duplicates are found from the index generated via HTML tree.
        """
        ama_index = self.ama_index
        expected = [
            {"1": [("cc_name1", "fan_name1"), ("cc_name1", "fan_name3")]},
        ]
        actual = indexer.identify_duplicates(ama_index)
        self.assertEqual(expected, actual)

    def test_get_urlid(self):
        """
        Tests that the url_id is extracted from a full url str.
        """
        url = self.url
        expected = self.url_id
        actual = indexer.get_urlid(url)
        self.assertEqual(expected, actual)

    def test_get_url(self):
        """
        Tests that given a valid url_id, a valid URL is returned.

        Also tests that the function returns the 'old' version of reddit.
        """
        url_id = self.url_id
        expected = self.url
        actual = indexer.get_url(url_id)
        self.assertEqual(expected, actual)
        # This is for the scraper module
        #response = r.get(actual)
        #self.assertEqual(response.status_code, 200)

    def test_save_ama_index(self):
        """
        Tests that ama_index is saved, and can be retrieved as it was.
        """
        ama_index = self.ama_index.copy()
        for ama_record in ama_index:
            ama_record["url_id"] = ama_record["url"]
            del ama_record["url"]
        full_dbpath = Path("ama_index-save_test.db")
        if full_dbpath.exists():
            full_dbpath.unlink()
        indexer.save_ama_index(ama_index, full_dbpath)
        with sqlite3.connect(full_dbpath) as cnxn:
            cnxn.row_factory = sqlite3.Row
            result = cnxn.execute("SELECT cc_name, fan_name, url_id FROM ama_index;")
            actual = [dict(record) for record in result.fetchall()]
        full_dbpath.unlink()
        expected = ama_index
        def original_order(element):
            """
            Function to sort dict-list by order in original self.ama_index.

            Assume: All entries in actual are contained in self.ama_index.
            """
            return self.ama_index.index(element)
        expected.sort(key=original_order)
        actual.sort(key=original_order)
        self.assertListEqual(expected, actual)
        # select from the database
        # assert selection equal to ama_index
