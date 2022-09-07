import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests
import scrapy
import sys
import logging
import boto3
from botocore.exceptions import ClientError

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Globals
# - - - -

# enable filtering on a subset of data (frozen as default inputs must be immutable)
YEARS_OF_INTEREST = ['2018']

# the index of the download page has been collected upfront.
INDEX_FILE = 'data/download-page-index.html'

S3_BUCKET = "snowflake-f28c31-3e92-9edc-c7f2-aab9-9a0c-889436"
FOLDER = "wergstatt/citibike/tripdata"


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Classes
# - - - -

class Collector:

    def __init__(self):
        self.links = extract_links_from_index_file()
        self.links = filter_link_list(links=self.links, keywords=YEARS_OF_INTEREST)

        self.files = None
        self.pq_files = None
        self.upload_responses = None

    def download_files(self):
        self.files = download_list_of_raw_files_from_link_list(self.links)
        return self

    def prep_base_files(self):
        self.pq_files = transform_zipped_files_into_parquet(self.files)
        return self

    def upload_files(self):
        self.upload_responses = upload_parquet_files_to_s3(self.pq_files)
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
        filepath = os.path.join('data', '0_raw', os.path.basename(link))
        download_file(link, filepath)
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


def download_file(link: str, file: str) -> str:
    """https://stackoverflow.com/questions/15644964/python-progress-bar-and-downloads"""
    with open(file, "wb") as f:
        print(f"\nDownloading {file}")
        response = requests.get(link, stream=True)
        total_length = response.headers.get('content-length')

        if total_length is None:  # no content length header
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / total_length)
                sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                sys.stdout.flush()

    return file


def upload_parquet_files_to_s3(files: list[str]) -> list[requests.Response]:
    responses, response = list(), False
    for file in files:
        response = upload_file(
            file_name=file,
            bucket=S3_BUCKET,
            object_name=os.path.join(FOLDER, os.path.basename(file)),
        )
    responses.append(response)
    return responses


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False

    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        return response
    except ClientError as e:
        logging.error(e)
        return False
