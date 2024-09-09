import traceback

from authenticator import refresh_cookies


def handler(event, context):
    try:
        emulator_id = "testDevice"
        asp_net_session_id = refresh_cookies(emulator_id=emulator_id)
        print(asp_net_session_id)
        return {
            'statusCode': 200,
            'body': "ASP.NET_SessionId: " + asp_net_session_id
        }
    except:
        return {
            'statusCode': 500,
            'body': "Error scraping ASP.NET_SessionId\n" + traceback.format_exc()
        }


if __name__ == "__main__":
    handler(None, None)
