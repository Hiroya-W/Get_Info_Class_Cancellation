from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pandas as pd

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def main():
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

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    print("Getting the upcoming 10 events")
    df_calendar = pd.read_csv("calendar.csv")
    for index, row in df_calendar.iterrows():
        # print(index, row["name"], row["calendarid"])
        events_result = (
            service.events()
            .list(
                calendarId=row["calendarid"],
                timeMin=now,
                maxResults=20,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        df = pd.DataFrame(columns=["id", "summary", "start_date", "end_date"])
        if not events:
            print("No upcoming events found.")
        for event in events:
            # start = event["start"].get("dateTime", event["start"].get("date"))
            # print(start, event["summary"])
            # print(event)
            sr = pd.Series(
                [
                    event["id"],
                    event["summary"],
                    event["start"].get("dateTime", event["start"].get("date")),
                    event["end"].get("dateTime", event["end"].get("date")),
                ],
                index=df.columns,
            )
            df = df.append(sr, ignore_index=True)

        df.to_csv(row["name"] + "_info.csv", index=False)


if __name__ == "__main__":
    main()
