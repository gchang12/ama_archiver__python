#!/usr/bin/python3
"""
This module defines constants for web-scraping and saving.
- FIRST_CC_NAME: The first content-creator name to appear on the HTML compendium.
- LC_URL: The URL to the link compendium.
- LC_FNAME: The filename that will contain the scraped HTML.
- LC_DBNAME: The database filename that will contain the scraped Q&A data.
- ODIR_NAME: The name of the directory where all data will be stored.
"""

FIRST_CC_NAME = "Daron Nefcy"
OG_URL = "https://www.reddit.com/r/StarVStheForcesofEvil/comments/cll9u5/star_vs_the_forces_of_evil_ask_me_anything/"
LC_URL = "https://old.reddit.com/r/StarVStheForcesofEvil/comments/clnrdv/link_compendium_of_questions_and_answers_from_the/"
LC_FNAME = "link-compendium"
AMA_DBNAME = "ama_database"
ODIR_NAME = "output"
URL_TEMPLATE = tuple("https://www.reddit.com/r/StarVStheForcesofEvil/comments/cll9u5/star_vs_the_forces_of_evil_ask_me_anything//?context=3".split("/"))

