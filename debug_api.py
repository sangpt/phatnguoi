import requests
import json
import sys

# Target Plate that SHOULD have violations
PLATE = "20H02185"

ENDPOINTS = [
    {
        "url": "https://api.phatnguoi.com/api/search", 
        "method": "POST",
        "payloads": [
            {"plate": PLATE}, 
            {"bienso": PLATE}, 
            {"keyword": PLATE},
            {"license_plate": PLATE},
            {"bs": PLATE}
        ]
    },
    {
        "url": "https://api.phatnguoi.com/api/search", 
        "method": "GET",
        "payloads": [{"plate": PLATE}, {"bienso": PLATE}, {"keyword": PLATE}]
    }
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Origin": "https://phatnguoi.com",
    "Referer": "https://phatnguoi.com/"
}

print(f"Testing plate: {PLATE}")

def safe_print(prefix, text):
    try:
        print(f"{prefix}: {text}")
    except Exception as e:
        try:
            print(f"{prefix}: {text.encode('utf-8')}")
        except:
            print(f"{prefix}: [Encoding Error]")

for ep in ENDPOINTS:
    print(f"\n--- Testing Endpoint: {ep['url']} [{ep.get('method', 'POST')}] ---")
    for p in ep['payloads']:
        try:
            print(f"Payload: {p}")
            
            if ep.get('method') == 'GET':
                 try:
                    r = requests.get(ep['url'], params=p, headers=headers, timeout=5)
                    if r.status_code == 200:
                        safe_print("[GET] 200 OK", r.text[:300])
                    else:
                        print(f"[GET] {r.status_code}")
                 except Exception as e:
                    print(f"[GET] Error: {e}")
                 continue

            try:
                r = requests.post(ep['url'], json=p, headers=headers, timeout=5)
                if r.status_code == 200:
                    safe_print("[JSON] 200 OK", r.text[:300])
                else:
                    print(f"[JSON] {r.status_code}")
            except Exception as e:
                print(f"[JSON] Error: {e}")
                
        except Exception as e:
            print(f"Setup Error: {e}")
