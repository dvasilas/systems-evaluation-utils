#!/usr/bin/env python

import argparse
import sys
import os
import os.path
import pickle
import json
import time
import requests
from datetime import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class ConfigError(Exception):
    pass


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def getCredentials(credFile):
    credentials = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credFile, SCOPES)
            credentials = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(credentials, token)
    return credentials


def addSheet(credentials, service, spreadsheet_id, sheetTitle):
    if sheetTitle == None:
        sheetTitle = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    addSheet_request = {
        "requests": [{"addSheet": {"properties": {"title": sheetTitle,}}}]
    }

    request = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body=addSheet_request
    )

    addSheetResp = request.execute()
    return addSheetResp["replies"][0]["addSheet"]["properties"]["sheetId"]


def pasteToSpreadsheet(
    credentials, service, spreadsheet_id, sheet_id, row, column, data
):
    import_request = {
        "requests": [
            {
                "pasteData": {
                    "coordinate": {
                        "sheetId": sheet_id,
                        "rowIndex": row,
                        "columnIndex": column,
                    },
                    "data": data,
                    "delimiter": ",",
                }
            }
        ]
    }
    request = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body=import_request
    )
    response = request.execute()
    print(response)

    parser = argparse.ArgumentParser()


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

    credentials = getCredentials(credFile)
    service = build("sheets", "v4", credentials=credentials)

    if args.create_sheet:
        sheetID = addSheet(credentials, service, spreadsheetID, None)
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

            pasteToSpreadsheet(
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
