import os
import subprocess
import time
import sqlite3
from ppadb.client import Client as AdbClient
from ppadb.command.host import Device
import memcache


def startEmulator():
    avds = subprocess.check_output(["emulator", '-list-avds']).decode('utf-8').splitlines()

    if not avds:
        raise Exception("No AVDs found")

    # Select the first AVD
    avd_name = avds[1]

    # Start the selected AVD
    start_command = ["emulator", '-avd', avd_name, '-no-window', 'no-audio', '-skip-adb-auth', '-no-boot-anim', '-show-kernel']
    subprocess.run(start_command)


def prepare_device(device: Device, emulator_id: str):
    device.shell("su root pm disable com.google.android.googlequicksearchbox")
    device.shell("am force-stop com.circasports.co")
    if device:
        # Ensure adb is running as root
        os.system("adb -s " + emulator_id + " root")

        # Ensure app is installed
        # device.install("./com.circasports.co.apk")
        device.shell("pm grant com.circasports.co  android.permission.ACCESS_FINE_LOCATION")

        # Open app
        command = "monkey -v -p com.circasports.co -c android.intent.category.LAUNCHER 1"
        device.shell(command)
    else:
        raise Exception("Device not found")


def attempt_cookies_collection(device: Device):
    for _ in range(30):
        input_path = (
            "data/data/com.circasports.co/app_webview/Default/Cookies"
        )
        output_path = "cookies.sqlitedb"
        device.pull(input_path, output_path)

        db = sqlite3.connect(output_path)
        cookies = db.execute(
            "SELECT * FROM cookies WHERE name='ASP.NET_SessionId'"
        ).fetchall()
        if len(cookies) > 0:
            asp_net_session_id = cookies[0][4]
            memcached_client = memcache.Client(
                ['session.sxq6qr.cfg.use2.cache.amazonaws.com:11211']
            )
            memcached_client.set('circa-asp-net-session-id', asp_net_session_id)
            return cookies[0][4]

        time.sleep(1)
    raise RuntimeError("Did not find ASP.NET_SessionId cookie")


def refresh_cookies(emulator_id):
    # startEmulator()
    client = AdbClient(host="127.0.0.1", port=5037)
    device = client.device(emulator_id)
    if not device:
        raise RuntimeError("Unable to connect to android device")

    prepare_device(device, emulator_id)
    return attempt_cookies_collection(device)


if __name__ == "__main__":
    refresh_cookies("emulator-5554")
