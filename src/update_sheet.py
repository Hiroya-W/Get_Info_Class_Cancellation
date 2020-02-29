from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def main(dataframe, sheetname):
    # test
    creds = None
    SCOPES = "https://www.googleapis.com/auth/spreadsheets"
    if os.path.exists("sheet_token.pickle"):
        with open("sheet_token.pickle", "rb") as token:
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
        with open("sheet_token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("sheets", "v4", credentials=creds)

    spreadsheet_id = "1fQ5QohND7-A0wrULEgiUOmT_2hChRQjhkTZe3TqqRwM"

    # クリア
    clear_values_request_body = {
        # empty
    }
    result = (
        service.spreadsheets()
        .values()
        .clear(
            spreadsheetId=spreadsheet_id,
            range=sheetname,
            body=clear_values_request_body,
        )
        .execute()
    )

    value_input_option = "USER_ENTERED"
    values = {}
    values["range"] = sheetname
    values["majorDimension"] = "ROWS"
    values["values"] = dataframe

    result = (
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=spreadsheet_id,
            range=sheetname,
            valueInputOption=value_input_option,
            body=values,
        )
        .execute()
    )


if __name__ == "__main__":
    sheetname = "test"
    dataframe = [[1, 2, 3], [4, 5, 6]]
    main(dataframe, sheetname)
