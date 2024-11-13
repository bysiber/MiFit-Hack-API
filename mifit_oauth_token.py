#!/usr/bin/env python3

import argparse
import requests
import json

def exit_with_error(message):
    """Print the error message and terminate the program."""
    print(f"Error: {message}")
    quit(1)


def get_oauth_code_help():
    """Provide OAuth login instructions."""
    return (
        "To login, visit:\n"
        "https://account.xiaomi.com/oauth2/authorize?skip_confirm=false&client_id=428135909242707968&pt=1&scope=1+6000+16001+20000&redirect_uri=https%3A%2F%2Fapi-mifit-cn.huami.com%2Fhuami.health.loginview.do_not&_locale=de_DE&response_type=code\n\n"
        "Login and copy the code after 'code=' from the redirect URL."
    )


def request_token_with_code(oauth_code):
    """Request the app token using the provided OAuth code."""
    login_url = 'https://account.huami.com/v2/client/login'
    
    # Prepare the payload for the login request
    data = {
        'app_name': 'com.xiaomi.hm.health',
        'country_code': 'DE',
        'code': oauth_code,
        'device_id': '02:00:00:00:00:00',
        'device_model': 'android_phone',
        'app_version': '4.0.9',
        'grant_type': 'request_token',
        'allow_registration': 'false',
        'dn': 'account.huami.com,api-user.huami.com,api-watch.huami.com,api-analytics.huami.com,app-analytics.huami.com,api-mifit.huami.com',
        'third_name': 'xiaomi-hm-mifit',
        'source': 'com.xiaomi.hm.health:4.0.9:8046',
        'lang': 'de',
    }

    # Send the login request
    response = requests.post(login_url, data=data, allow_redirects=False)

    # Parse the response
    result = response.json()

    # Check for errors in the response
    if 'error_code' in result:
        error_code = result['error_code']
        if error_code == '0106':
            exit_with_error("The code is invalid or was already used")
        exit_with_error(f"Failed with error code {error_code}")

    return result


def main():
    """Main function to execute the OAuth login and retrieve the token."""
    parser = argparse.ArgumentParser(
        description="Get an app token from a manual Mi account login.\n\n" + get_oauth_code_help(),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--code", required=True, help="OAuth code obtained from the login")
    args = parser.parse_args()

    # Request token using the provided OAuth code
    result = request_token_with_code(args.code)
    print(result)


if __name__ == "__main__":
    main()
