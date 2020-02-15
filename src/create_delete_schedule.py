from __future__ import print_function

# import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pandas as pd

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_diff():
    df_new = pd.read_csv("cancel_new.csv")

    df_old = pd.read_csv("cancel_old.csv")
    df_old["start_date"] = pd.to_datetime(df_old["start_date"])
    # print(datetime.datetime.now().date())
    # df_old = df_old[df_old["start_date"] >= datetime.datetime.now()]
    # df_old = df_old[df_old["start_date"] >= pd.Timestamp(2018, 2, 1)]
    # print(pd.Timestamp.now(tz="Asia/Tokyo").date())
    df_old = df_old[df_old["start_date"] >= pd.Timestamp.now().date()]

    df_create = df_new[~df_new.id.isin((df_old.id))]
    df_delete = df_old[~df_old.id.isin((df_new.id))]
    print(df_create)
    print(df_delete)
    # print(pd.merge(df_my, df_cancel, how="inner"))
    return df_create, df_delete


def main():
    # 差分を取得
    df_create, df_delete = get_diff()

    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
            # print("refresh")
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "secret/client_secret.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("calendar", "v3", credentials=creds)

    df_calendar = pd.read_csv("calendar.csv")
    # fmt: off
    # create
    for index, row in df_create.iterrows():
        for index, calendar_row in df_calendar.iterrows():
            if calendar_row["name"] in row["summary"]:
                body = {
                    "summary": row["summary"],
                    "start": {"date": row["start_date"], "timeZone": "Asia/Tokyo"},
                    "end": {"date": row["end_date"], "timeZone": "Asia/Tokyo"},
                    # "colorId": "5",
                }

                event = service.events().insert(calendarId=calendar_row["calendarid"], body=body).execute()
                print("Event created: %s" % (event.get("htmlLink")))

    # delete
    for index, delete_row in df_delete.iterrows():
        for index, calendar_row in df_calendar.iterrows():
            if calendar_row["name"] in delete_row["summary"]:
                df_my = pd.read_csv(calendar_row["name"] + "_info.csv")
                for index, myinfo_row in df_my.iterrows():
                    # print(delete_row["summary"] == myinfo_row["summary"])
                    # print(delete_row["start_date"] == pd.to_datetime(myinfo_row["start_date"]))
                    if (
                        delete_row["summary"] == myinfo_row["summary"]
                        and delete_row["start_date"] == pd.to_datetime(myinfo_row["start_date"])
                    ):
                        service.events().delete(
                            calendarId=calendar_row["calendarid"], eventId=myinfo_row["id"]
                        ).execute()
                        print("Event deleted")
    # fmt: on
    pd.read_csv("cancel_new.csv").to_csv("cancel_old.csv", index=False)


if __name__ == "__main__":
    main()
