#!/usr/bin/python3

# This script contains class objects and functions involved in assigning a data hub.

__author__ = 'Nadim Rahman'

import argparse, cx_Oracle, os, sys
import pandas as pd
from getpass import getpass
from utils import Config, Utilities

def get_args():
    """
    Handle script arguments
    :return: Script arguments
    """
    parser = argparse.ArgumentParser(prog='main.py', formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""
        + =========================================================== +
        |  ENA Data Hubs Setup: assigner.py                           |
        |  Python tool to assign a data hub.                          |
        + =========================================================== +
        """)
    parser.add_argument('-s', '--spreadsheet', help='Input spreadsheet for the data hub assignment', type=str, required=True)
    parser.add_argument('-d', '--datahub_name', help='Name of data hub to be assigned', type=str, required=True)
    parser.add_argument('-p', '--datahub_password', help='Password for data hub to be assigned', type=str, required=True)
    args = parser.parse_args()
    return args


class MetadataFromDatabase:
    # Class object which handles obtaining metadata from ERAPRO database
    def __init__(self, sql_query, host, port, service):
        self.query = sql_query          # SQL query to obtain metadata
        self.host = host            # Host name for the database connection
        self.port = port            # Port number for the database connection
        self.service = service          # Service name for the database connection

    def get_oracle_usr_pwd(self):
        """
        Obtain credentials to create an SQL connection
        :return: Username and password for a valid SQL database account
        """
        self.usr = input("Username: ")  # Ask for username
        self.pwd = getpass()  # Ask for password and handle appropriately

    def setup_connection(self):
        """
        Set up the database connection
        :return: Database connection object
        """
        client_lib_dir = os.getenv('ORACLE_CLIENT_LIB')
        #client_lib_dir = ''
        if not client_lib_dir or not os.path.isdir(client_lib_dir):
            sys.stderr.write("ERROR: Environment variable $ORACLE_CLIENT_LIB must point at a valid directory\n")
            exit(1)
        cx_Oracle.init_oracle_client(lib_dir=client_lib_dir)
        self.connection = None
        try:
            dsn = cx_Oracle.makedsn(self.host, self.port,
                                    service_name=self.service)  # Try connection to ERAPRO with credentials
            self.connection = cx_Oracle.connect(self.usr, self.pwd, dsn, encoding="UTF-8")
        except cx_Oracle.Error as error:
            print(error)

    def fetch_metadata(self):
        """
        Obtain metadata from ERAPRO database
        :return: Dataframe of metadata
        """
        self.get_oracle_usr_pwd()  # Obtain credentials from script operator
        self.setup_connection()  # Set up the database connection using the credentials
        if self.connection is not None:
            cursor = self.connection.cursor()
            search_query = cursor.execute(self.query)  # Query the database with the SQL query
            if 'SELECT' in self.query:
                df = pd.DataFrame(search_query.fetchall())  # Fetch all results and save to dataframe
            else:
                df = "Ran SQL query:\n " \
                     "{}".format(self.query)
                print(df)
            return df


def extract_datahub_info(datahub_info):
    general = list(datahub_info['General'].items())[1]
    general_datahub = general[1]
    description = general_datahub[3]
    abstract = general_datahub[4]
    print('-' * 100)
    print('*To be assigned*')
    print('Data Hub Description: {}'.format(description))
    print('Data Hub Abstract: {}'.format(abstract))
    print('-' * 100)
    return description, abstract



def assign_datahub(dh, pw, description, abstract, configuration):
    assign_string = """begin
        era.PORTAL_DCC_PKG.add_dcc_account('{}', '{}', '{}', '{}', '{}', 'ACTIVE', null);
    end;""".format(dh, pw, configuration['WEBIN'], description, abstract)
    return assign_string


if __name__ == '__main__':
    args = get_args()
    configuration = Config.read_config()

    setup_spreadsheet = Utilities.read_spreadsheet(args.spreadsheet)
    description, abstract = extract_datahub_info(setup_spreadsheet)

    assign_sql = assign_datahub(args.datahub_name, args.datahub_password, description, abstract, configuration)

    assign_dh_config = MetadataFromDatabase(assign_sql, configuration['HOST'], configuration['PORT'], configuration['SERVICE'])
    assign_dh = assign_dh_config.fetch_metadata()
