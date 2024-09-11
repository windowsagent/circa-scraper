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
    start_command = ["/opt/android-sdk/emulator/emulator", '-avd', avd_name, '-ports', '5036,5037', '-no-window', '-no-audio', '-skip-adb-auth', '-no-boot-anim', '-show-kernel',
                     '-qemu', '-cpu', 'max', '-machine', 'gic-version=max']
    

    return subprocess.Popen(start_command)


def wait_for_port(port: int, host: str = 'localhost', timeout: float = 10.0):
    start_time = time.perf_counter()
    while True:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                break
        except OSError as ex:
            time.sleep(0.01)
            if time.perf_counter() - start_time >= timeout:
                raise TimeoutError()

def prepare_device(device: Device, emulator_id: str):
    device.shell("su root pm disable com.google.android.googlequicksearchbox")
    device.shell("am force-stop com.circasports.co")
    if device:
        # Ensure adb is running as root
        os.system("adb -s " + emulator_id + " root")

        # Ensure app is installed
        device.install("./com.circasports.co.apk")
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
    # Ensure we have empty auth file
    with open(os.path.expanduser("~/.emulator_console_auth_token"), "w") as fp:
        pass

    emulator = startEmulator()
    try:
        wait_for_port(host="127.0.0.1", port=5037)
        client = AdbClient(host="127.0.0.1", port=5037)
        device = client.device(emulator_id)
        if not device:
            raise Exception
        prepare_device(device, emulator_id)
    finally:
        emulator.terminate()

    return attempt_cookies_collection(device)


if __name__ == "__main__":
    print(refresh_cookies("emulator-5554"))
