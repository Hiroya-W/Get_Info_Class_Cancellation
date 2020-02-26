from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def main(sheetname):
    # test
    creds = None
    SCOPES = "https://www.googleapis.com/auth/spreadsheets"
    if os.path.exists("sheet_token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) crsecret/edentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "secret/credentials.json", SCOPES
            )

            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("sheets", "v4", credentials=creds)

    spreadsheet_id = "1fQ5QohND7-A0wrULEgiUOmT_2hChRQjhkTZe3TqqRwM"

    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=sheetname)
        .execute()
    )
    # print(result["values"])
    return result["values"]


if __name__ == "__main__":
    sheetname = "cancel_new"
    main(sheetname)
