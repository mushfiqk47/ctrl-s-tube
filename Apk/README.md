# Building the Android APK

This project uses **Buildozer** to compile the Python code into an Android APK.

## Prerequisites

**Buildozer currently only works on Linux or macOS.**
If you are on Windows, you must use **WSL (Windows Subsystem for Linux)** or a Linux Virtual Machine.

### 1. Install WSL (if on Windows)
Open PowerShell as Administrator and run:
```powershell
wsl --install
```
Restart your computer if prompted. Then open "Ubuntu" from your Start menu.

### 2. Install Dependencies (inside Linux/WSL)
Run the following commands in your Linux terminal:

```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
pip3 install --user --upgrade buildozer Cython virtualenv
```

### 3. Prepare the Project
Navigate to your project folder. If you are using WSL, your Windows drives are mounted at `/mnt/c/`.
```bash
cd /mnt/c/Users/MUSHFIQ/Desktop/New\ folder/Yt\ downloader_v7.0\ \(2\)/Yt\ downloader_v7.0
```

**Important:** Buildozer expects the main file to be named `main.py`.
You should rename `main_kivy.py` to `main.py` temporarily, or copy it:
```bash
cp main_kivy.py main.py
```

### 4. Build the APK
Run the build command:
```bash
buildozer android debug
```
This process will take a while (15-30 minutes) the first time as it downloads the Android SDK and NDK.

### 5. Locate the APK
Once finished, the APK will be in the `bin/` directory:
```bash
ls bin/
```
You can then copy this `.apk` file to your phone and install it.

## Troubleshooting
- **Missing permissions**: Ensure `android.permissions` in `buildozer.spec` includes `INTERNET` and `WRITE_EXTERNAL_STORAGE`.
- **Build failures**: Check the logs. Often it's due to missing system dependencies (step 2).
