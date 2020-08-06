import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

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