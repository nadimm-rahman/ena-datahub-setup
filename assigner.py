#!/usr/bin/python3

# This script contains class objects and functions involved in assigning a data hub.

__author__ = 'Nadim Rahman'

import argparse, cx_Oracle, os, sys
import pandas as pd
from getpass import getpass
from utils import Config, Utilities


# Configure and initialise with cx_Oracle:
# client_lib_dir = os.getenv('ORACLE_CLIENT_LIB')
client_lib_dir = '/pathto/instantclient_XX_X'
if not client_lib_dir or not os.path.isdir(client_lib_dir):
    sys.stderr.write("ERROR: Environment variable $ORACLE_CLIENT_LIB must point at a valid directory\n")
    exit(1)
cx_Oracle.init_oracle_client(lib_dir=client_lib_dir)


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
        self.connection = None
        try:
            dsn = cx_Oracle.makedsn(self.host, self.port,
                                    service_name=self.service)  # Try connection to database with credentials
            self.connection = cx_Oracle.connect(self.usr, self.pwd, dsn, encoding="UTF-8")
        except cx_Oracle.Error as error:
            print(error)

    def fetch_metadata(self):
        """
        Obtain metadata from database
        :return: Dataframe of metadata
        """
        self.get_oracle_usr_pwd()  # Obtain credentials from script operator
        self.setup_connection()  # Set up the database connection using the credentials
        if self.connection is not None:
            cursor = self.connection.cursor()
            search_query = cursor.execute(self.query)  # Query the database with the SQL query
            print('*' * 100)
            print("Ran SQL query:\n{}".format(self.query))
            print('*' * 100)
            if 'SELECT' in self.query:
                df = pd.DataFrame(search_query.fetchall())  # Fetch all results and save to dataframe
            else:
                df = ""
            self.connection.close()
            return df


class AssignConfigure:
     # Class object to assign a data hub and configure Webin accounts to it
    def __init__(self, datahub_info, dh, pw, configuration):
        """
        :param datahub_info: Data object corresponding to input spreadsheet for data hub setup
        :param dh: Unassigned data hub name
        :param pw: Unassigned data hub password
        :param configuration: Dictionary of tool configuration settings
        """
        self.datahub_info = datahub_info
        self.dh = dh
        self.pw = pw
        self.configuration = configuration

    def extract_datahub_info(self):
        """
        Extract general data hub information
        :return: Data hub description and abstract
        """
        general = list(self.datahub_info['General'].items())[1]
        general_datahub = general[1]
        description = general_datahub[3]
        abstract = general_datahub[4]
        print('-' * 100)
        print('*To be assigned*')
        print('Data Hub Description: {}'.format(description))
        print('Data Hub Abstract: {}'.format(abstract))
        print('-' * 100)
        return description, abstract

    def assign_datahub(self, description, abstract):
        """
        Create query to assign data hub
        :param description: Data hub description
        :param abstract: Data hub abstract
        :return: SQL string for data hub assignment
        """
        assign_string = """begin\n\tera.PORTAL_DCC_PKG.add_dcc_account('{}', '{}', '{}', '{}', '{}', 'ACTIVE', null);\nend;\n""".format(self.dh, self.pw, self.configuration['WEBIN'], description, abstract)
        return assign_string

    def extract_webin_accounts(self):
        """
        Extract all Webin accounts from data provider information
        :return: List of Webin accounts to link to assigned data hub
        """
        providers = list(self.datahub_info['Data_Providers'].items())[4][1]          # Extract dictionary of Webin account ID's from 'Webin Accounts' tuple of the data object
        webin_accounts = list(set(list(providers.values())))            # Get all Webin account IDs from the dictionary, and remove all duplicates
        return webin_accounts

    def assign_webin_accounts(self, webin_accounts):
        """
        Create query to assign all Webin accounts to the assigned data hub
        :param webin_accounts: List of all Webin accounts to be linked with the assigned data hub
        :return: SQL string for Webin account linking
        """
        add_string = ""
        for account in webin_accounts:
            add_string = add_string + "\tera.PORTAL_DCC_PKG.add_dcc_to_submission_account('{}', '{}');\n".format(account, self.dh)
        add_string = "begin\n" + add_string + "end;\n"
        return add_string

    def assign_configure(self):
        """
        Assign and configure the data hub - runner function
        """
        description, abstract = self.extract_datahub_info()     # Extract the general data hub information, required for data hub assignment
        assign_sql = self.assign_datahub(description, abstract)     # Obtain SQL string for data hub assignment

        assign_dh_config = MetadataFromDatabase(assign_sql, self.configuration['HOST'], self.configuration['PORT'], self.configuration['SERVICE'])      # Configure and run the SQL query to assign the data hub
        assign_dh = assign_dh_config.fetch_metadata()

        webin_accounts = self.extract_webin_accounts()  # Extract all Webin accounts, required to link Webin accounts to data hub
        webin_sql = self.assign_webin_accounts(webin_accounts)  # Obtain a string for the linking of Webin accounts to the data hub

        webin_dh_config = MetadataFromDatabase(webin_sql, self.configuration['HOST'], self.configuration['PORT'], self.configuration['SERVICE'])  # Configure and run the SQL query to link the Webin accounts to the data hub
        webin_dh_config = webin_dh_config.fetch_metadata()



if __name__ == '__main__':
    args = get_args()
    configuration = Config.read_config()
    setup_spreadsheet = Utilities.read_spreadsheet(args.spreadsheet)

    configure_dh = AssignConfigure(setup_spreadsheet, args.datahub_name, args.datahub_password, configuration)      # Instantiate class object with data hub setup information
    configure_dh.assign_configure()     # Run the configuration and assign the data hub
