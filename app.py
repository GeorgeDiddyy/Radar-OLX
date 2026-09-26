import requests
from bs4 import BeautifulSoup
import time
import threading
import os  # <-- AM ADĂUGAT ACEST IMPORT OBLIGATORIU
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- CONFIGURARE TELEGRAMA TA ---
TOKEN_TELEGRAM = "8832312698:AAEEg1ZtTZhm0Y6JdN15cqkkKmsliNqVyiY"
ID_CHAT = "8921969479"
INTERVAL_VERIFICARE = 45 

LISTA_CAUTARI = [
    "https://www.olx.ro/electronice-si-electrocasnice/telefoane-mobile/arges-judet/q-samsung-sigilat/?currency=RON&search%5Border%5D=created_at:desc&search%5Bfilter_enum_state%5D%5B0%5D=new",
    "https://www.olx.ro/electronice-si-electrocasnice/telefoane-mobile/arges-judet/q-iphone-sigilat/?currency=RON&search%5Border%5D=created_at:desc&search%5Bfilter_enum_state%5D%5B0%5D=new"
]

anunturi_vechi = set()
prima_rulare = True

# --- SERVER PENTRU RENDER ---
class HealthCheckServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Radarul OLX ruleaza!")

def porneste_server_ping():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckServer)
    server.serve_forever()

def trimite_telegram(mesaj):
    url = f"https://telegram.org{TOKEN_TELEGRAM}/sendMessage"
    payload = {"chat_id": ID_CHAT, "text": mesaj}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

def scaneaza_olx():
    global anunturi_vechi, prima_rulare
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        for url_cautare in LISTA_CAUTARI:
            response = requests.get(url_cautare, headers=headers, timeout=15)
            if response.status_code != 200: continue
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)
            for link in links:
                url_anunt = link['href']
                if "/d/anunt/" in url_anunt and "-ID" in url_anunt:
                    url_complet = "https://olx.ro" + url_anunt if url_anunt.startswith('/') else url_anunt
                    id_anunt = url_complet.split('-ID')[-1].split('.html')[0]
                    if id_anunt not in anunturi_vechi:
                        anunturi_vechi.add(id_anunt)
                        if not prima_rulare:
                            trimite_telegram(f"🔥 PRODUS NOU PE OLX!\n\n👉 Deschide Anunțul: {url_complet}")
    except: pass

def bucla_radar():
    global prima_rulare
    scaneaza_olx()
    if prima_rulare:
        trimite_telegram("🚀 Radarul tău permanent pentru CĂUTĂRI MULTIPLE a pornit cu succes!")
        prima_rulare = False
    while True:
        time.sleep(INTERVAL_VERIFICARE)
        scaneaza_olx()

# Pornire separată server + radar
threading.Thread(target=porneste_server_ping, daemon=True).start()
bucla_radar()


