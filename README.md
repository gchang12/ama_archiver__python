<!-- These are examples of badges you might want to add to your README:
     please update the URLs accordingly

[![Built Status](https://api.cirrus-ci.com/github/<USER>/ama_archiver.svg?branch=main)](https://cirrus-ci.com/github/<USER>/ama_archiver)
[![ReadTheDocs](https://readthedocs.org/projects/ama_archiver/badge/?version=latest)](https://ama_archiver.readthedocs.io/en/stable/)
[![Coveralls](https://img.shields.io/coveralls/github/<USER>/ama_archiver/main.svg)](https://coveralls.io/r/<USER>/ama_archiver)
[![PyPI-Server](https://img.shields.io/pypi/v/ama_archiver.svg)](https://pypi.org/project/ama_archiver/)
[![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/ama_archiver.svg)](https://anaconda.org/conda-forge/ama_archiver)
[![Monthly Downloads](https://pepy.tech/badge/ama_archiver/month)](https://pepy.tech/project/ama_archiver)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/ama_archiver)
-->

[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)

# ama_archiver

> Scrapes the SVTFOE Reddit Q&A session.

Scrapes Reddit virtual Q&A session for details on lore and backstory of SVTFOE.


<!-- pyscaffold-notes -->

## Note

This project has been set up using PyScaffold 4.5. For details and usage
information on PyScaffold see https://pyscaffold.org/.

# Two tables:
ama_index
- cc_name TEXT NOT NULL
- fan_name TEXT NOT NULL
- url_id TEXT NOT NULL

ama_queries
- url_id TEXT PRIMARY KEY
- question_text TEXT NOT NULL
- answer_text TEXT NOT NULL

# to identify duplicates via SQL query.
SELECT * FROM ama_index WHERE url_id IN (SELECT url_id FROM ama_index GROUP BY url_id HAVING COUNT(url_id) > 1);

# source URLs
https://www.reddit.com/r/StarVStheForcesofEvil/comments/cll9u5/star_vs_the_forces_of_evil_ask_me_anything/
https://old.reddit.com/r/StarVStheForcesofEvil/comments/clnrdv/link_compendium_of_questions_and_answers_from_the/
