from rest_framework.response import Response
from rest_framework.decorators import api_view
from googleapiclient.discovery import build
import google_auth_oauthlib.flow
from django.shortcuts import redirect
import os
import os.path
from datetime import datetime

OAUTH_CREDENTIALS_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

@api_view(['GET'])
def GoogleCalendarInitView(request):

    GATE = google_auth_oauthlib.flow.Flow.from_client_secrets_file(OAUTH_CREDENTIALS_FILE, scopes=SCOPES)
    GATE.redirect_uri = 'http://localhost:8000/rest/v1/calendar/redirect/'

    authorization_url, state = GATE.authorization_url(include_granted_scopes='true',access_type='offline')
    request.session['state'] = state

    return redirect(authorization_url)

@api_view(['GET'])
def GoogleCalendarRedirectView(request):

    state = request.session.get('state')
    
    GATE = google_auth_oauthlib.flow.Flow.from_client_secrets_file(OAUTH_CREDENTIALS_FILE, scopes=SCOPES, state=state)
    GATE.redirect_uri = 'http://localhost:8000/rest/v1/calendar/redirect/'
    authorization_response = request.get_full_path()
    GATE.fetch_token(authorization_response=authorization_response)

    credentials = GATE.credentials

    try:
        service = build('calendar', 'v3', credentials=credentials)
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' denotes UTC time
        events_result = service.events().list(calendarId='primary').execute()
        events = events_result.get('items', [])
        future_events_result = service.events().list(calendarId='primary',timeMin=now,singleEvents=True,orderBy='startTime').execute()
        future_events = future_events_result.get('items', [])

        if not events:
            return Response({'MESSAGE': 'The User has no events in their Calendar!'})
        else:
            events_list = []
            for event in events:
                event_dict = {
                    'EVENT ID': event['id'],
                    'NAME': event['summary'],
                    'CREATOR': event['creator'],
                    'ORGANIZER': event['organizer'],
                    'START TIME': event['start'],
                    'END TIME': event['end']
                }
                events_list.append(event_dict)
            future_events_list = []
            for event in future_events:
                event_dict = {
                    'EVENT ID': event['id'],
                    'NAME': event['summary'],
                    'CREATOR': event['creator'],
                    'ORGANIZER': event['organizer'],
                    'START TIME': event['start'],
                    'END TIME': event['end']
                }
                future_events_list.append(event_dict)
            combined_list = [{'FUTURE EVENTS': future_events_list, 'ALL EVENTS': events_list}]
            return Response(combined_list)

    except Exception as error:
        return Response({'ERROR': error})

    
