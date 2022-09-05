import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests
import scrapy

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Globals
# - - - -

# enable filtering on a subset of data (frozen as default inputs must be immutable)
YEARS_OF_INTEREST = ['2018']

# the index of the download page has been collected upfront.
INDEX_FILE = 'data/download-page-index.html'


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Classes
# - - - -

class Collector:

    def __init__(self):
        self.links = extract_links_from_index_file()
        self.links = filter_link_list(links=self.links, keywords=YEARS_OF_INTEREST)

        self.files = None
        self.pq_files = None

    def download_files(self):
        self.files = download_list_of_raw_files_from_link_list(self.links)
        return self

    def prep_base_files(self):
        self.pq_files = transform_zipped_files_into_parquet(self.files)
        return self


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Functionspace
# - - - - - - -


def extract_links_from_index_file(index_file: str = INDEX_FILE) -> list[str]:
    # get download page content and extract download links.
    with open(index_file) as f:
        html_page_content = ''.join(f.readlines())
        selector = scrapy.Selector(text=html_page_content)
        download_links = selector.css('a').css('a::attr(href)').extract()

    return download_links


def filter_link_list_on_keyword(links: list[str], keyword: str) -> list[str]:
    return [link for link in links if keyword in link]


def filter_link_list(links: list[str], keywords: list[str]) -> list[str]:
    for keyword in keywords:
        links = filter_link_list_on_keyword(links, keyword)
    return links


def download_list_of_raw_files_from_link_list(links: list[str]) -> list[str]:
    """Take a list of links and dump the raw content into the local file system"""

    # download files to data/raw folder.
    links_of_interest = [link for link in links if '2018' in link]
    local_files = list()
    for link in links_of_interest:
        response = requests.get(link)
        filepath = os.path.join('data', '0_raw', os.path.basename(link))
        with open(filepath, 'wb') as f:
            f.write(response.content)
        local_files.append(filepath)

    return local_files


def transform_zipped_files_into_parquet(files: list[str]) -> list[str]:
    """Take a list of zipped csv files and transform them into parquet ones."""

    parquet_files = list()
    for file in files:
        # derive target path from local source file path.
        pq_tgt_path = file.split('.')[0].replace('0_raw', '1_base') + '.parquet'

        # read zipped file and dump as parquet file to base-camp folder.
        df = pd.read_csv(file, sep=',', compression='zip')
        table = pa.Table.from_pandas(df, preserve_index=False)
        pq.write_table(table, pq_tgt_path, compression='zstd')
        parquet_files.append(pq_tgt_path)

    return parquet_files
