"""
Helper function to download data
"""

import requests
from pathlib import Path


def get_file_data(filename: str = "Food_Inspections.csv",
                  url: str = 'https://data.cityofchicago.org/api/views/4ijn-s7e5/rows.csv?accessType=DOWNLOAD'):
    """
    Download a a file from a given url and save to a given filename
    does not exist already.
    Returns
    -------
    """
    csv_file = Path(filename)

    if not csv_file.is_file():
        with open(csv_file, 'wb') as writer, \
                requests.get(url, stream=True) as reader:
            for line in reader.iter_lines():
                writer.write(line)


if __name__ == '__main__':
    get_file_data()
