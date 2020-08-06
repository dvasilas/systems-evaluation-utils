#!/usr/bin/env python3

import argparse
import sys
import os
import os.path
import json
import time
import requests
from datetime import datetime
from googleapiclient.discovery import build

import sheetCommon

class ConfigError(Exception):
    pass

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--row", help="Row in which to import measurements")
    parser.add_argument("-c", "--column", help="Column in which to import measurements")
    parser.add_argument(
        "--create_sheet",
        action="store_true",
        help="Create a new sheet and import there",
    )
    parser.add_argument("data")

    return parser


def main():
    args = get_parser().parse_args(sys.argv[1:])

    credFile = os.getenv("CREDENTIAL_FILE")
    if credFile == None:
        raise ConfigError("No credentials file specified")

    spreadsheetID = os.getenv("SPREADSHEET_ID")
    if spreadsheetID == None:
        raise ConfigError("No spreadsheet ID specified")

    credentials = sheetCommon.getCredentials(credFile)
    service = build("sheets", "v4", credentials=credentials)

    if args.create_sheet:
        sheetID = sheetCommon.addSheet(credentials, service, spreadsheetID, None)
    else:
        sheetID = os.getenv("SHEET_ID")
        if sheetID == None:
            raise ConfigError("No sheet ID specified")

    if args.data:
        dataToImport = ""
        with open(args.data) as fpData:
            line = fpData.readline()
            while line:
                dataToImport += line
                line = fpData.readline()

            sheetCommon.pasteToSpreadsheet(
                credentials,
                service,
                spreadsheetID,
                sheetID,
                args.row,
                args.column,
                dataToImport,
            )


if __name__ == "__main__":
    main()
