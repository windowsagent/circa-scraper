#!/bin/sh
git clone https://github.com/windowsagent/circa-scraper
cd circa-scraper
sudo apt update && sudo apt upgrade
sudo apt install default-jdk python3-pip repo python-is-python3 unzip libpcre2-dev adb
wget https://dl.google.com/android/repository/commandlinetools-linux-8512546_latest.zip 
unzip commandlinetools-linux-8512546_latest.zip -d android-sdk
sudo mv android-sdk /opt/
mkdir /opt/android-sdk/cmdline-tools/latest
mv /opt/android-sdk/cmdline-tools/* /opt/android-sdk/cmdline-tools/latest
echo "export ANDROID_SDK_ROOT=/opt/android-sdk" >> ~/.bashrc
echo "export ANDROID_HOME=/opt/android-sdk" >> ~/.bashrc
echo "export ANDROID_EMULATOR_WAIT_TIME_BEFORE_KILL=60" >> ~/.bashrc
echo "export PATH=$PATH:/opt/android-sdk/cmdline-tools/latest/bin" >> ~/.bashrc
source ~/.bashrc
sdkmanager --update
yes | sdkmanager --licenses
cd /opt/android-sdk/
wget -O emulator.zip "https://storage.googleapis.com/android-build/builds/aosp-emu-master-dev-linux-emulator-linux_aarch64/12342982/81de3b9a965cd9189ae975056189696ec8f805dce39a5d9d2afec58ca24e6a21/sdk-repo-linux_aarch64-emulator-12342982.zip?GoogleAccessId=gcs-sign%40android-builds-project.google.com.iam.gserviceaccount.com&Expires=1725943450&Signature=iPNUJ%2F5PHUySRjcmWv%2BCkJ%2FF9dSFypALe77w7yxnNu%2BEYIftBRlc14v1QccXB5AuT39MrLiBLJhdZL9vj02oDmwz6qcN1g%2B%2BHmkeYPdEZm%2Bu7NIVsCsCOxqdrKqe640hyPzKh2eT9mrMHWTorGOsXTIMlnbJasiU9L7KYCAEZsKWhwGGL2zOK5yenS%2BlG6qHEKV9vqusYQhUPD3RtU8xfMhdHEpIfy56Oy%2Bq1oqwexlCS6vdzWWC0TlbxRGMMCKF8HTpQye3hrbtTOIX9kBWSYY1LPdpu9kA2jcvKxLHjSsu%2F1A%2FPzSnPkIfRrKFvJRqGgxuM5DtDyQiL6asZAr5Zw%3D%3D&response-content-disposition=attachment"
unzip emulator.zip
curl "https://chromium.googlesource.com/android_tools/+/refs/heads/main/sdk/emulator/package.xml?format=TEXT" | base64 --decode > /opt/android-sdk/emulator/package.xml

sed -i "s/<major>[0-9]*<\/major>/<major>35<\/major>/" /opt/android-sdk/emulator/package.xml
sed -i "s/<minor>[0-9]*<\/minor>/<minor>3<\/minor>/" /opt/android-sdk/emulator/package.xml
sed -i "s/<micro>[0-9]*<\/micro>/<micro>2<\/micro>/" /opt/android-sdk/emulator/package.xml

sdkmanager "system-images;android-31;google_apis;arm64-v8a"
echo -ne '\n' | avdmanager -v create avd -f -n MyAVD -k "system-images;android-31;google_apis;arm64-v8a" -p "/opt/android-sdk/avd" 
mkdir /opt/android-sdk/platforms
mkdir /opt/android-sdk/platform-tools
echo "Vulkan = off" >> ~/.android/advancedFeatures.ini
echo "GLDirectMem = on" >> ~/.android/advancedFeatures.ini
sudo ln -sf /opt/android-sdk/emulator/emulator /usr/bin/
