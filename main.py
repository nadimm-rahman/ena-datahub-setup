#!/usr/bin/python3

import argparse
from utils import Config
from datahub_emails import emailer


def get_args():
    """
    Handle script arguments
    :return: Script arguments
    """
    parser = argparse.ArgumentParser(prog='main.py', formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""
        + =========================================================== +
        |  ENA Data Hubs Setup: main.py                               |
        |  Python tool to handle assignment and set up of a data      |
        |  hub.                                                       |
        + =========================================================== +
        """)
    # parser.add_argument('-u', '--username', help='Data Hub username to be assigned (e.g. dcc_XXXXX)', type=str, required=True)
    # parser.add_argument('-p', '--password', help='Password for the data hub to be assigned', type=str, required=True)
    parser.add_argument('-s', '--spreadsheet', help='Input spreadsheet for the data hub assignment', type=str, required=True)
    args = parser.parse_args()
    return args



if __name__ == '__main__':
    args = get_args()
    configuration = Config.read_config()        # Read in configuration

    emailer(args, configuration)        # Prepare and send emails to data providers and consumers
