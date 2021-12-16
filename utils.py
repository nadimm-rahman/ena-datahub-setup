#!/usr/bin/python3

# This script contains re-usable utilities

__author__ = 'Nadim Rahman'

import pandas as pd
import yaml

class Config:
    """Configuration"""

    @staticmethod
    def read_config():
        """
        Read in the configuration file
        :return: A dictionary referring to tool configuration
        """
        with open("config.yaml") as f:
            configuration = yaml.safe_load(f)
        return configuration


class Utilities:
    """Utilities"""

    @staticmethod
    def read_spreadsheet(spreadsheet_file):
        """
        Open the spreadsheet depending on the file-type
        :param spreadsheet_file: Path to spreadsheet
        :return: spreadsheet: Spreadsheet as a data frame to be manipulated
        """
        if spreadsheet_file.endswith(".xlsx") or spreadsheet_file.endswith(".xls"):
            spreadsheet = pd.ExcelFile(spreadsheet_file)
            sheet_to_df_map = {}
            for sheet_name in spreadsheet.sheet_names:          # Retrieve all data frames in different sheets and return a dictionary
                sheet_df = spreadsheet.parse(sheet_name, header=0, index_col=False, skiprows=2).to_dict()
                sheet_to_df_map[sheet_name] = sheet_df
            return sheet_to_df_map
        elif spreadsheet_file.endswith(".csv"):
            spreadsheet = pd.read_csv(spreadsheet_file, header=0, sep=",", index_col=False)
            return spreadsheet
        elif spreadsheet_file.endswith(".txt") or spreadsheet_file.endswith(".tsv"):
            spreadsheet = pd.read_csv(spreadsheet_file, header=0, sep="\t", index_col=False)
            return spreadsheet
