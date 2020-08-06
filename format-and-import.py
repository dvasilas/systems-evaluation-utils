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
    parser.add_argument('-r', '--row', help='Row in which to import measurements.')
    parser.add_argument("--desc",action='store_true',help="Import the template description")
    parser.add_argument(
        "--create_sheet",
        action="store_true",
        help="Create a new sheet and import there",
    )
    parser.add_argument("template")
    parser.add_argument("data", nargs='?')

    return parser

def makeMatchTemplateFilter(prefix):
    def matchesTemplate(s):
      return s.startswith(prefix)
    return matchesTemplate

def main():
    args = get_parser().parse_args(sys.argv[1:])

    credFile = os.getenv("CREDENTIAL_FILE")
    if credFile == None:
        raise ConfigError('No credentials file specified')

    spreadsheetID = os.getenv("SPREADSHEET_ID")
    if spreadsheetID == None:
        raise ConfigError('No spreadsheet ID specified')

    credentials = sheetCommon.getCredentials(credFile)
    service = build("sheets", "v4", credentials=credentials)

    if args.create_sheet:
        sheetID = sheetCommon.addSheet(credentials, service, spreadsheetID, None)
    else:
        sheetID = os.getenv("SHEET_ID")
        if sheetID == None:
            raise ConfigError("No sheet ID specified")

    dataDescription = ''
    if args.desc:
      with open(args.template) as fpTemplate:
          line = fpTemplate.readline()
          while line:
              dataDescription += line.strip() + ", "
              line = fpTemplate.readline()
    else:
        with open(args.data) as fpData:
            measurements = fpData.readlines()
        dataDescription = ''
        dataToImport = ''
        with open(args.template) as fpTemplate:
            line = fpTemplate.readline()
            while line:
                entry = list(filter(makeMatchTemplateFilter(line.strip()), measurements))
                if len(entry) != 1:
                    dataToImport += "0, "
                else:
                    dataToImport += entry[0].strip().split(":")[1].strip() + ", "

                dataDescription += line.strip() + ", "
                line = fpTemplate.readline()

    if args.desc:
        sheetCommon.pasteToSpreadsheet(credFile, service, spreadsheetID, sheetID, args.row, 0, dataDescription)
    else:
        sheetCommon.pasteToSpreadsheet(credFile, service, spreadsheetID, sheetID, args.row, 0, dataToImport)

if __name__ == "__main__":
    main()
