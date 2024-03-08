#!/usr/bin/python3
"""
"""

from ama_archiver import scraper

# TODO: Shouldn't this belong in __main__.py, since it depends on previous two functions?
def compile_ama_queries(ama_index: List[dict]) -> List[dict]:
    """
    """
    # TODO: save ama_query as soon as it is retrieved
    # TODO: check if ama_query exists; attempt to retrieve if not; skip if yes.
    # compile entries from sqlite database
    ama_queries = []
    expected_fields = {"url_id", "question_text", "answer_text"}
    total_num_queries = len(ama_index)
    # should record this somewhere
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
            scraper.fetch_ama_query(url, ama_query)
            # only print upon error, and without concealing the error
            total_num_tries += 1
            counter += 1
            print("Fetching from %r. Try: %d" % (url, counter))
        ama_queries.append(ama_query)
    return ama_queries
