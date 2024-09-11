import os
import subprocess
import time
import sqlite3
from ppadb.client import Client as AdbClient
from ppadb.command.host import Device
import memcache
import socket
import os

def startEmulator():
    avds = subprocess.check_output(["emulator", '-list-avds']).decode('utf-8').splitlines()

    if not avds:
        raise Exception("No AVDs found")

    # Select the first AVD
    avd_name = avds[0]

    # Start the selected AVD
    start_command = ["/opt/android-sdk/emulator/emulator", '-avd', avd_name, '-no-window', '-no-audio', '-skip-adb-auth', '-no-boot-anim',
                     '-qemu', '-cpu', 'max', '-machine', 'gic-version=max']
    

    return subprocess.Popen(start_command)

def check_adb_devices_down():
    try:
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
        if "offline" in result.stdout:
            return True
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return True
    

def prepare_device(device: Device):
    print("Installing circasports")   
    device.install("./com.circasports.co")
    device.shell("pm grant com.circasports.co  android.permission.ACCESS_FINE_LOCATION")
# Open app
    print("Opening circasports")
    command = "monkey -v -p com.circasports.co -c android.intent.category.LAUNCHER 1"
    device.shell(command)


def attempt_cookies_collection(device: Device):
    for _ in range(30):
        input_path = (
            "data/data/com.circasports.co/app_webview/Default/Cookies"
        )
        output_path = "cookies.sqlitedb"
        print(f"Saving cookies to {output_path}")
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
    # Ensure we have empty auth file
    with open(os.path.expanduser("~/.emulator_console_auth_token"), "w") as fp:
        pass

    emulator = startEmulator()
    time.sleep(30)
    try:
        client = AdbClient(host="127.0.0.1", port=5037)
        device = client.device(emulator_id)
        if not device:
            raise Exception
        while check_adb_devices_down():
            time.sleep(10)
        prepare_device(device)
        return attempt_cookies_collection(device)
    finally:
        emulator.terminate()

if __name__ == "__main__":
    print(refresh_cookies("emulator-5554"))
