#!/usr/bin/env python3

import argparse
import requests
import urllib.parse
import json
import base64
import datetime


def fail(message):
    """Exit the program with an error message."""
    print(f"Error: {message}")
    quit(1)


def authenticate_with_email(email, password):
    """Authenticate the user with the provided email and password."""
    print(f"Logging in with email {email}")
    auth_url = f'https://api-user.huami.com/registrations/{urllib.parse.quote(email)}/tokens'
    data = {
        'state': 'REDIRECTION',
        'client_id': 'HuaMi',
        'redirect_uri': 'https://s3-us-west-2.amazonws.com/hm-registration/successsignin.html',
        'token': 'access',
        'password': password,
    }

    response = requests.post(auth_url, data=data, allow_redirects=False)
    response.raise_for_status()
    
    redirect_url = urllib.parse.urlparse(response.headers.get('location'))
    response_args = urllib.parse.parse_qs(redirect_url.query)

    if 'access' not in response_args:
        fail('No access token in response')

    if 'country_code' not in response_args:
        fail('No country_code in response')

    print("Obtained access token")
    access_token = response_args['access']
    country_code = response_args['country_code']
    
    return login_with_token({
        'grant_type': 'access_token',
        'country_code': country_code,
        'code': access_token,
    })


def login_with_token(login_data):
    """Login using the access token."""
    login_url = 'https://account.huami.com/v2/client/login'
    data = {
        'app_name': 'com.xiaomi.hm.health',
        'dn': 'account.huami.com,api-user.huami.com,api-watch.huami.com,api-analytics.huami.com,app-analytics.huami.com,api-mifit.huami.com',
        'device_id': '02:00:00:00:00:00',
        'device_model': 'android_phone',
        'app_version': '4.0.9',
        'allow_registration': 'false',
        'third_name': 'huami',
    }
    data.update(login_data)
    
    response = requests.post(login_url, data=data, allow_redirects=False)
    return response.json()


def format_minutes_as_time(minutes):
    """Convert minutes to a formatted time string."""
    return f"{(minutes // 60) % 24:02d}:{minutes % 60:02d}"


def display_sleep_data(day, sleep_data):
    """Display the sleep data for a specific day."""
    print(f"Total sleep: {format_minutes_as_time(sleep_data['lt'] + sleep_data['dp'])}, "
          f"Deep sleep: {format_minutes_as_time(sleep_data['dp'])}, "
          f"Light sleep: {format_minutes_as_time(sleep_data['lt'])}, "
          f"Slept from {datetime.datetime.fromtimestamp(sleep_data['st'])} until "
          f"{datetime.datetime.fromtimestamp(sleep_data['ed'])}")

    if 'stage' in sleep_data:
        for stage in sleep_data['stage']:
            sleep_type = {
                4: 'light sleep',
                5: 'deep sleep'
            }.get(stage['mode'], f"Unknown sleep type: {stage['mode']}")
            print(f"{format_minutes_as_time(stage['start'])} - {format_minutes_as_time(stage['stop'])} {sleep_type}")


def display_step_data(day, step_data):
    """Display the step data for a specific day."""
    print(f"Total steps: {step_data['ttl']}, Calories used: {step_data['cal']} kcals, Distance walked: {step_data['dis']} meters")
    
    if 'stage' in step_data:
        for activity in step_data['stage']:
            activity_type = {
                1: 'slow walking',
                3: 'fast walking',
                4: 'running',
                7: 'light activity'
            }.get(activity['mode'], f"Unknown activity type: {activity['mode']}")
            print(f"{format_minutes_as_time(activity['start'])} - {format_minutes_as_time(activity['stop'])} "
                  f"{activity['step']} steps {activity_type}")


def fetch_band_data(auth_info):
    """Fetch the band data for the authenticated user."""
    print("Retrieving Mi Band data...")
    band_data_url = 'https://api-mifit.huami.com/v1/data/band_data.json'
    headers = {'apptoken': auth_info['token_info']['app_token']}
    params = {
        'query_type': 'summary',
        'device_type': 'android_phone',
        'userid': auth_info['token_info']['user_id'],
        'from_date': '2019-01-01',
        'to_date': '2019-12-31',
    }

    response = requests.get(band_data_url, params=params, headers=headers)

    for day_data in response.json()['data']:
        day = day_data['date_time']
        print(day)
        summary = json.loads(base64.b64decode(day_data['summary']))
        
        for key, value in summary.items():
            if key == 'stp':
                display_step_data(day, value)
            elif key == 'slp':
                display_sleep_data(day, value)
            else:
                print(f"{key} = {value}")


def main():
    """Main function to parse arguments and fetch band data."""
    parser = argparse.ArgumentParser(description="Mi Fit Band Data Fetcher")
    parser.add_argument("--email", required=True, help="Email address for login")
    parser.add_argument("--password", required=True, help="Password for login")
    args = parser.parse_args()

    auth_info = authenticate_with_email(args.email, args.password)
    fetch_band_data(auth_info)


if __name__ == "__main__":
    main()
