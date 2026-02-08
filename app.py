from flask import Flask, render_template, request, jsonify
import requests
import sys
import json
import random
import time

app = Flask(__name__)

# --- Configuration ---
CHECK_PHAT_NGUOI_API = "https://api.checkphatnguoi.vn/phatnguoi"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search_fines():
    data = request.json
    license_plate = data.get('plate', '').upper().replace('-', '').replace('.', '').strip()
    vehicle_type = data.get('type', '1') # Default to 1 (Car)
    
    if not license_plate:
        return jsonify({"success": False, "message": "Vui lòng nhập biển số xe"}), 400

    print(f"DEBUG: Received search request for: {license_plate}, Type: {vehicle_type}", flush=True)

    start_time = time.time()

    # Try external API (checkphatnguoi.vn)
    try:
        # API returned "Chưa hỗ trợ định dạng biển số này" with "20H-021.85"
        # So we revert to sending CLEAN plate: "20H02185"
        formatted_plate = license_plate
        print(f"DEBUG: Formatted plate for API: {formatted_plate}", flush=True)

        # CHANGE: Try sending as FORM DATA instead of JSON
        # Some PHP/older backends ignore JSON body
        payload = {
            "bienso": formatted_plate,
            "loaixe": vehicle_type
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            # "Content-Type": "application/x-www-form-urlencoded" # requests handles this automatically with 'data='
        }
        
        print(f"\n--- API CALL START (Form Data) ---")
        print(f"TARGET: {CHECK_PHAT_NGUOI_API}")
        print(f"PAYLOAD: {payload}")

        # Use data=payload for application/x-www-form-urlencoded
        response = requests.post(CHECK_PHAT_NGUOI_API, data=payload, headers=headers, timeout=15)
        
        print(f"STATUS: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"RESPONSE DATA:\n{json.dumps(result, indent=2, ensure_ascii=False)}") 
            print(f"--- API CALL END ---\n")
            
            # Logic to detecting valid data vs null
            # If data is null, it might mean "No violation" OR "Invalid format"
            # But usually existing apps show "No violation" for null data.
            final_data = []
            if result and isinstance(result, dict) and result.get('data'):
                # Map API keys (Vietnamese) to Frontend keys (English/Snake_case)
                for item in result['data']:
                    try:
                        # Handle 'Nơi giải quyết vụ việc' which can be a list or string
                        contact_info = item.get("Nơi giải quyết vụ việc", [])
                        if isinstance(contact_info, list):
                            contact_info = ". ".join(contact_info)
                        
                        mapped_item = {
                            "bien_so": item.get("Biển kiểm soát", ""),
                            "thoi_gian": item.get("Thời gian vi phạm", ""),
                            "dia_diem": item.get("Địa điểm vi phạm", ""),
                            "hanh_vi": item.get("Hành vi vi phạm", ""),
                            "trang_thai": item.get("Trạng thái", ""),
                            "don_vi": item.get("Đơn vị phát hiện vi phạm", ""),
                            "lien_he": contact_info
                        }
                        final_data.append(mapped_item)
                    except Exception as e:
                        print(f"Error mapping item: {e}")
            
            return jsonify({"success": True, "source": "external", "data": final_data})
            
    except Exception as e:
        print(f"External API failed: {e}")
        return jsonify({"success": False, "message": "Lỗi kết nối đến server dữ liệu. Vui lòng thử lại sau."}), 500


    # Default: No violation found (if API failed or returned nothing)
    return jsonify({
        "success": True,
        "source": "empty",
        "data": [] 
    })

if __name__ == '__main__':
    app.run(debug=True)
