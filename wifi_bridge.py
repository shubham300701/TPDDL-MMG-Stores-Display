"""
Real-Time Hardware Wi-Fi Bridge & Store Inventory Sync Service
MMG Stores (KPM) - Tata Power Delhi Distribution Limited
Cross-Platform: Windows (netsh) & Raspberry Pi / Linux (nmcli / iwlist / wpa_cli)

Provides live REST API endpoints with CORS support for index.html & store_entry_portal.html:
  GET  /api/wifi/status       - Real current connection, IP, SSID, Signal
  GET  /api/wifi/scan         - Live physical hardware scan of nearby wireless networks
  POST /api/wifi/connect      - Connect to a network with SSID and password
  POST /api/wifi/disconnect   - Disconnect active wireless connection
  GET  /api/inventory         - Current live inventory array with stock & forecasts
  POST /api/inventory/update  - Direct update of inventory state
  GET  /api/portal/pending    - List of pending storekeeper requests
  POST /api/portal/submit     - Storekeeper submits inward/issue request
  POST /api/portal/approve    - Manager approves/rejects request (updates stock instantly)
  GET  /api/portal/audit      - Immutable transaction audit log
Also serves static files on http://localhost:8765
"""

import sys
import os
import json
import re
import socket
import subprocess
import platform
import time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import urllib.parse

PORT = int(os.environ.get('PORT', 8765))
IS_WINDOWS = platform.system().lower() == 'windows'

INVENTORY_FILE = "inventory_state.json"
PENDING_FILE = "pending_queue.json"
AUDIT_FILE = "audit_log.json"

DEFAULT_INVENTORY = [
    { "id": 1,  "code": "TPDDL-MTR-01", "name": "LTCT Meter (Single Phase)", "opening": 500, "issued": 180, "low": 25, "high": 60, "d1": 20, "d2": 18, "d3": 16, "lastUpdated": "18.10.2026, 12:15 PM" },
    { "id": 2,  "code": "TPDDL-MTR-02", "name": "PP WC Meter (Poly Phase)",  "opening": 300, "issued": 12,  "low": 20, "high": 50, "d1": 11, "d2": 10, "d3": 9,  "lastUpdated": "18.10.2026, 10:45 AM" },
    { "id": 3,  "code": "TPDDL-MTR-03", "name": "HT Meter (High Tension)",   "opening": 150, "issued": 152, "low": 15, "high": 35, "d1": 6,  "d2": 5,  "d3": 4,  "lastUpdated": "18.10.2026, 11:30 AM" },
    { "id": 4,  "code": "TPDDL-MTR-04", "name": "Net Meter (Solar Rooftop)", "opening": 400, "issued": 247, "low": 30, "high": 70, "d1": 16, "d2": 14, "d3": 13, "lastUpdated": "18.10.2026, 12:12 PM" },
    { "id": 5,  "code": "TPDDL-MTR-05", "name": "Prepaid Smart Meter",       "opening": 250, "issued": 215, "low": 20, "high": 50, "d1": 24, "d2": 21, "d3": 20, "lastUpdated": "18.10.2026, 09:40 AM" },
    { "id": 6,  "code": "TPDDL-MTR-06", "name": "CT Ratio Meter",           "opening": 180, "issued": 88,  "low": 20, "high": 45, "d1": 10, "d2": 9,  "d3": 8,  "lastUpdated": "17.10.2026, 05:30 PM" },
    { "id": 7,  "code": "TPDDL-MTR-07", "name": "Smart Grid AMI Meter",     "opening": 600, "issued": 310, "low": 40, "high": 90, "d1": 30, "d2": 28, "d3": 26, "lastUpdated": "18.10.2026, 09:15 AM" },
    { "id": 8,  "code": "TPDDL-MTR-08", "name": "Whole Current Meter",      "opening": 350, "issued": 140, "low": 25, "high": 60, "d1": 15, "d2": 14, "d3": 13, "lastUpdated": "17.10.2026, 04:50 PM" },
    { "id": 9,  "code": "TPDDL-MTR-09", "name": "Energy Meter 1-Phase",     "opening": 800, "issued": 420, "low": 50, "high": 120, "d1": 45, "d2": 40, "d3": 38, "lastUpdated": "18.10.2026, 08:30 AM" },
    { "id": 10, "code": "TPDDL-MTR-10", "name": "Energy Meter 3-Phase",     "opening": 450, "issued": 210, "low": 30, "high": 75, "d1": 22, "d2": 20, "d3": 19, "lastUpdated": "17.10.2026, 03:20 PM" }
]

def load_json(filepath, default_val):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(default_val, f, indent=2)
    return default_val

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def get_inventory():
    inv = load_json(INVENTORY_FILE, DEFAULT_INVENTORY)
    defaults = {d["code"]: d.get("lastUpdated", "18.10.2026, 09:30 AM") for d in DEFAULT_INVENTORY}
    changed = False
    for row in inv:
        if not row.get("lastUpdated"):
            row["lastUpdated"] = defaults.get(row.get("code"), "18.10.2026, 09:30 AM")
            changed = True
    if changed:
        save_json(INVENTORY_FILE, inv)
    return inv

def get_pending():
    return load_json(PENDING_FILE, [
        {
            "reqId": "REQ-20261018-104512",
            "time": "18-Oct-2026 10:45 AM",
            "type": "ISSUE",
            "meter": "HT Meter (High Tension)",
            "qty": 10,
            "staff": "P. K. Verma (JE-8491)",
            "site": "Pitampura 66kV Grid",
            "remarks": "Line augment"
        },
        {
            "reqId": "REQ-20261018-111005",
            "time": "18-Oct-2026 11:10 AM",
            "type": "ISSUE",
            "meter": "Net Meter (Solar Rooftop)",
            "qty": 25,
            "staff": "R. K. Sharma (AE-1022)",
            "site": "Civil Lines Feeder 4",
            "remarks": "PM Surya Ghar Yojana"
        }
    ])

def get_audit():
    return load_json(AUDIT_FILE, [
        { "time": "18-Oct-2026 09:30 AM", "reqId": "REQ-20261018-093011", "meter": "LTCT Meter", "qty": 30, "staff": "A. Gupta", "status": "APPROVED", "manager": "Store Manager (Auth-999)" },
        { "time": "17-Oct-2026 04:15 PM", "reqId": "REQ-20261017-161522", "meter": "Prepaid Smart Meter", "qty": 50, "staff": "V. Mehra", "status": "APPROVED", "manager": "Store Manager (Auth-999)" }
    ])

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def get_real_wifi_status():
    if IS_WINDOWS:
        try:
            res = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], capture_output=True, text=True, timeout=5)
            out = res.stdout
            state_match = re.search(r'State\s*:\s*(.+)', out)
            ssid_match = re.search(r'SSID\s*:\s*(.+)', out)
            signal_match = re.search(r'Signal\s*:\s*(\d+)%', out)
            auth_match = re.search(r'Authentication\s*:\s*(.+)', out)
            bssid_match = re.search(r'BSSID\s*:\s*(.+)', out)

            is_connected = bool(state_match and 'connected' in state_match.group(1).lower())
            ssid = ssid_match.group(1).strip() if (is_connected and ssid_match) else "None"
            signal_val = signal_match.group(1).strip() + "%" if (is_connected and signal_match) else "0%"
            auth_val = auth_match.group(1).strip() if (is_connected and auth_match) else "None"
            bssid_val = bssid_match.group(1).strip() if (is_connected and bssid_match) else ""

            return {
                "hardware": "Windows WLAN Interface",
                "connected": is_connected,
                "ssid": ssid,
                "signal": signal_val,
                "security": auth_val,
                "bssid": bssid_val,
                "ip": get_local_ip() if is_connected else "0.0.0.0",
                "isEnterprise": "802.1x" in auth_val.lower() or "enterprise" in auth_val.lower()
            }
        except Exception as e:
            return {"hardware": "Error", "connected": False, "ssid": "Error", "error": str(e), "ip": "0.0.0.0", "signal": "0%"}
    else:
        try:
            res = subprocess.run(['nmcli', '-t', '-f', 'DEVICE,TYPE,STATE,CONNECTION', 'dev'], capture_output=True, text=True, timeout=5)
            lines = res.stdout.splitlines()
            wifi_conn = None
            for l in lines:
                parts = l.split(':')
                if len(parts) >= 4 and parts[1] == 'wifi' and parts[2] == 'connected':
                    wifi_conn = parts[3]
                    break
            
            if wifi_conn:
                sig_res = subprocess.run(['nmcli', '-t', '-f', 'SSID,SIGNAL,SECURITY', 'dev', 'wifi'], capture_output=True, text=True, timeout=5)
                sig = "85%"
                sec = "WPA2"
                for sl in sig_res.stdout.splitlines():
                    sp = sl.split(':')
                    if len(sp) >= 2 and sp[0] == wifi_conn:
                        sig = sp[1] + "%"
                        if len(sp) >= 3: sec = sp[2]
                        break
                return {
                    "hardware": "Linux wlan0",
                    "connected": True,
                    "ssid": wifi_conn,
                    "signal": sig,
                    "security": sec,
                    "ip": get_local_ip(),
                    "isEnterprise": "enterprise" in sec.lower() or "802.1x" in sec.lower()
                }
            else:
                return {
                    "hardware": "Linux wlan0",
                    "connected": False,
                    "ssid": "None",
                    "signal": "0%",
                    "security": "None",
                    "ip": "0.0.0.0",
                    "isEnterprise": False
                }
        except Exception as e:
            return {"hardware": "Linux Error", "connected": False, "ssid": "Error", "error": str(e), "ip": "0.0.0.0", "signal": "0%"}

def scan_real_wifi_networks():
    networks = []
    if IS_WINDOWS:
        try:
            res = subprocess.run(['netsh', 'wlan', 'show', 'networks', 'mode=bssid'], capture_output=True, text=True, timeout=8)
            current_net = None
            for line in res.stdout.splitlines():
                line = line.strip()
                m_ssid = re.match(r'^SSID\s+\d+\s*:\s*(.*)$', line)
                if m_ssid:
                    if current_net and current_net.get('ssid'):
                        networks.append(current_net)
                    ssid_val = m_ssid.group(1).strip()
                    current_net = {
                        'ssid': ssid_val if ssid_val else '[Hidden Network]',
                        'security': 'Open',
                        'signal': 50,
                        'bssid': '',
                        'channel': '',
                        'isEnterprise': False
                    }
                    continue
                if not current_net:
                    continue
                m_auth = re.match(r'^Authentication\s*:\s*(.*)$', line)
                if m_auth:
                    auth_val = m_auth.group(1).strip()
                    current_net['security'] = auth_val
                    if 'enterprise' in auth_val.lower() or '802.1x' in auth_val.lower():
                        current_net['isEnterprise'] = True
                m_bssid = re.match(r'^BSSID\s+\d+\s*:\s*(.*)$', line)
                if m_bssid:
                    current_net['bssid'] = m_bssid.group(1).strip()
                m_sig = re.match(r'^Signal\s*:\s*(\d+)%', line)
                if m_sig:
                    current_net['signal'] = int(m_sig.group(1))
                m_chan = re.match(r'^Channel\s*:\s*(\d+)', line)
                if m_chan:
                    current_net['channel'] = m_chan.group(1)

            if current_net and current_net.get('ssid'):
                networks.append(current_net)
        except Exception as e:
            print(f"Error scanning Windows wifi: {e}")
    else:
        try:
            subprocess.run(['nmcli', 'dev', 'wifi', 'rescan'], capture_output=True, timeout=5)
            res = subprocess.run(['nmcli', '-t', '-f', 'SSID,BSSID,SIGNAL,SECURITY,CHAN', 'dev', 'wifi', 'list'], capture_output=True, text=True, timeout=6)
            for line in res.stdout.splitlines():
                parts = line.split(':')
                if len(parts) >= 4:
                    ssid = parts[0].strip() or "[Hidden Network]"
                    bssid = parts[1].strip()
                    try:
                        sig = int(parts[2].strip())
                    except ValueError:
                        sig = 50
                    sec = parts[3].strip() if len(parts) >= 4 else "Open"
                    chan = parts[4].strip() if len(parts) >= 5 else ""
                    networks.append({
                        'ssid': ssid,
                        'bssid': bssid,
                        'signal': sig,
                        'security': sec if sec else "Open",
                        'channel': chan,
                        'isEnterprise': "enterprise" in sec.lower() or "802.1x" in sec.lower()
                    })
        except Exception as e:
            print(f"Error scanning Linux wifi: {e}")

    dedup = {}
    for n in networks:
        ssid = n['ssid']
        if ssid not in dedup or n['signal'] > dedup[ssid]['signal']:
            dedup[ssid] = n

    result = list(dedup.values())
    result.sort(key=lambda x: x['signal'], reverse=True)
    return result

def connect_to_wifi(ssid, password):
    if not ssid:
        return {"success": False, "error": "SSID cannot be empty"}

    if IS_WINDOWS:
        try:
            profile_xml = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>manual</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""
            tmp_file = os.path.join(os.environ.get('TEMP', '.'), f"wifi_prof_{re.sub(r'[^a-zA-Z0-9]', '', ssid)}.xml")
            with open(tmp_file, 'w', encoding='utf-8') as f:
                f.write(profile_xml)

            subprocess.run(['netsh', 'wlan', 'add', 'profile', f'filename={tmp_file}'], capture_output=True, text=True, timeout=5)
            res = subprocess.run(['netsh', 'wlan', 'connect', f'name={ssid}'], capture_output=True, text=True, timeout=8)
            
            try:
                os.remove(tmp_file)
            except OSError:
                pass

            return {"success": True, "message": f"Connection initiated to {ssid}", "output": res.stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}
    else:
        try:
            cmd = ['nmcli', 'dev', 'wifi', 'connect', ssid]
            if password:
                cmd.extend(['password', password])
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if res.returncode == 0:
                return {"success": True, "message": f"Connected to {ssid}", "output": res.stdout}
            else:
                return {"success": False, "error": res.stderr or res.stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}

def disconnect_wifi():
    if IS_WINDOWS:
        try:
            res = subprocess.run(['netsh', 'wlan', 'disconnect'], capture_output=True, text=True, timeout=5)
            return {"success": True, "message": "Wi-Fi disconnected", "output": res.stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}
    else:
        try:
            res = subprocess.run(['nmcli', 'dev', 'disconnect', 'wlan0'], capture_output=True, text=True, timeout=5)
            return {"success": True, "message": "Wi-Fi disconnected", "output": res.stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}

class StoreRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Requested-With')
        self.send_header('Access-Control-Allow-Private-Network', 'true')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        # 1. Real Wi-Fi Status
        if parsed.path == '/api/wifi/status':
            status = get_real_wifi_status()
            self._send_json(status)
            return

        # 2. Real Wi-Fi Scan
        elif parsed.path == '/api/wifi/scan':
            networks = scan_real_wifi_networks()
            self._send_json(networks)
            return

        # 3. Live Inventory State
        elif parsed.path == '/api/inventory':
            inv = get_inventory()
            import datetime
            now_dt = datetime.datetime.now()
            d1_dt = now_dt + datetime.timedelta(days=1)
            d2_dt = now_dt + datetime.timedelta(days=2)
            d3_dt = now_dt + datetime.timedelta(days=3)
            d1_short = d1_dt.strftime('%a')
            d2_short = d2_dt.strftime('%a')
            d3_short = d3_dt.strftime('%a')
            for item in inv:
                item['d1Day'] = d1_short
                item['d2Day'] = d2_short
                item['d3Day'] = d3_short
            self._send_json({
                "timestamp": time.time(),
                "inventory": inv,
                "forecastDays": {
                    "d1": d1_short,
                    "d2": d2_short,
                    "d3": d3_short
                }
            })
            return

        # 4. Pending Requests Queue
        elif parsed.path == '/api/portal/pending':
            pend = get_pending()
            self._send_json({"pending": pend})
            return

        # 5. Audit Log
        elif parsed.path == '/api/portal/audit':
            aud = get_audit()
            self._send_json({"audit": aud})
            return

        # Default: Serve static files
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8') if length > 0 else '{}'
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        # 1. Connect Wi-Fi
        if parsed.path == '/api/wifi/connect':
            ssid = payload.get('ssid', '')
            password = payload.get('password', '')
            result = connect_to_wifi(ssid, password)
            self._send_json(result)
            return

        # 2. Disconnect Wi-Fi
        elif parsed.path == '/api/wifi/disconnect':
            result = disconnect_wifi()
            self._send_json(result)
            return

        # 3. Submit Staff Request
        elif parsed.path == '/api/portal/submit':
            pending = get_pending()
            new_item = {
                "reqId": payload.get("reqId", f"REQ-{int(time.time())}"),
                "time": payload.get("time", time.strftime("%d-%b-%Y %I:%M %p")),
                "type": payload.get("type", "ISSUE"),
                "meter": payload.get("meter", ""),
                "qty": int(payload.get("qty", 1)),
                "staff": payload.get("staff", ""),
                "site": payload.get("site", ""),
                "remarks": payload.get("remarks", "")
            }
            pending.insert(0, new_item)
            save_json(PENDING_FILE, pending)
            self._send_json({"success": True, "item": new_item})
            return

        # 4. Manager Approve / Reject
        elif parsed.path == '/api/portal/approve':
            req_id = payload.get("reqId", "")
            decision = payload.get("decision", "APPROVED")
            pending = get_pending()
            audit = get_audit()
            inv = get_inventory()

            matched_item = None
            remaining_pending = []
            for item in pending:
                if item.get("reqId") == req_id:
                    matched_item = item
                else:
                    remaining_pending.append(item)

            if not matched_item:
                idx = payload.get("index")
                if idx is not None and 0 <= idx < len(pending):
                    matched_item = pending.pop(idx)
                    remaining_pending = pending

            save_json(PENDING_FILE, remaining_pending)

            # Extract details from matched_item OR payload directly
            m_name = (matched_item["meter"] if matched_item else payload.get("meter", "")).lower()
            qty = int(matched_item["qty"] if matched_item else payload.get("qty", 0))
            is_issue = (matched_item.get("type", "ISSUE") if matched_item else payload.get("type", "ISSUE")) == "ISSUE"
            staff = (matched_item.get("staff", "Store Staff") if matched_item else payload.get("staff", "Store Staff"))

            # Add to Audit Log
            audit_entry = {
                "time": time.strftime("%d-%b-%Y %I:%M %p"),
                "reqId": req_id or f"REQ-{int(time.time())}",
                "type": "OUTWARD" if is_issue else "INWARD",
                "meter": matched_item["meter"] if matched_item else payload.get("meter", "Meter"),
                "qty": qty,
                "staff": staff,
                "status": decision,
                "manager": "Store Manager (Auth-999)"
            }
            audit.insert(0, audit_entry)
            save_json(AUDIT_FILE, audit)

            # If Approved, update inventory immediately — with hard stock validation!
            updated_meter = None
            if decision == "APPROVED" and m_name and qty > 0:
                for row in inv:
                    r_name = row["name"].lower()
                    r_code = row["code"].lower()
                    if (r_name in m_name) or (m_name in r_name) or (r_code in m_name) or (m_name in r_code):
                        if is_issue:
                            opening = int(row.get("opening", 0))
                            current_issued = min(int(row.get("issued", 0)), opening)
                            available = opening - current_issued

                            # ── HARD RULE: issued can NEVER exceed opening stock ──
                            if qty > available:
                                self._send_json({
                                    "success": False,
                                    "blocked": True,
                                    "error": f"ISSUE BLOCKED: Only {available} units available for '{row['name']}'. "
                                             f"Requested {qty} exceeds available stock (Opening: {opening}, Issued: {current_issued}).",
                                    "available": available,
                                    "opening": opening,
                                    "requested": qty
                                })
                                return
                            row["issued"] = current_issued + qty  # Safe — validated above
                        else:
                            # INWARD: always safe to add to opening stock
                            row["opening"] = int(row.get("opening", 0)) + qty
                        row["lastUpdated"] = time.strftime("%d.%m.%Y, %I:%M %p")
                        updated_meter = row
                        break

                save_json(INVENTORY_FILE, inv)

            self._send_json({
                "success": True,
                "decision": decision,
                "inventory": inv,
                "updatedMeter": updated_meter,
                "audit": audit_entry
            })
            return

        # 5. Direct inventory override
        elif parsed.path == '/api/inventory/update':
            new_inv = payload.get("inventory")
            if new_inv and isinstance(new_inv, list):
                save_json(INVENTORY_FILE, new_inv)
                self._send_json({"success": True, "inventory": new_inv})
                return

        self.send_response(404)
        self.end_headers()

    def _send_json(self, data, status_code=200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

if __name__ == '__main__':
    web_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(web_dir)
    # Ensure initial files
    get_inventory()
    get_pending()
    get_audit()

    server = ThreadingHTTPServer(('0.0.0.0', PORT), StoreRequestHandler)
    print(f"============================================================")
    print(f"  MMG Stores KPM - Real Hardware Wi-Fi & Live Inventory Sync")
    print(f"  System OS:     {platform.system()} ({platform.release()})")
    print(f"  Local IP:      {get_local_ip()}")
    print(f"  Main Monitor:  http://localhost:{PORT}/index.html")
    print(f"  Rack Display:  http://localhost:{PORT}/rack_display.html?rack=1")
    print(f"  Racks Matrix:  http://localhost:{PORT}/rack_matrix.html")
    print(f"  Entry Portal:  http://localhost:{PORT}/store_entry_portal.html")
    print(f"============================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        server.server_close()
