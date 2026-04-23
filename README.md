# Proxy Server for Vercel

แอปพลิเคชันสำหรับจัดการเครื่องเป้าหมายผ่าน API และ Socket Connection

## โครงสร้างไฟล์

- `api.py` - Flask API สำหรับ Vercel (เพียง API endpoint)
- `proxy_server.py` - Socket Server เดิม (รันแยกกันบนเซิร์ฟเวอร์ของคุณ)
- `vercel.json` - Configuration สำหรับ Vercel
- `requirements.txt` - Python dependencies

## วิธีการ Deploy

### 1. Deploy API ไปที่ Vercel

```bash
# ลงชื่อเข้า Vercel
npx vercel login

# Deploy
npx vercel
```

### 2. รัน Socket Server ที่เซิร์ฟเวอร์ของคุณ

```bash
# ติดตั้ง dependencies
pip install -r requirements.txt

# รัน Socket Server
python proxy_server.py
```

## API Endpoints

### GET /api/health
ตรวจสอบสถานะเซิร์ฟเวอร์

### GET /api/targets
ดึงข้อมูลเครื่องทั้งหมด

### POST /api/register
ลงทะเบียนเครื่องใหม่

```json
{
  "pc_name": "computer-1",
  "tokens": ["token1", "token2"]
}
```

### POST /api/command
ส่งคำสั่งไปยังเครื่องเป้าหมาย

```json
{
  "pc_name": "computer-1",
  "command": "your-command"
}
```

## สถาปัตยกรรม

- **Vercel API** - APIs สำหรับหน้าเว็บเรียกใช้ (HTTP)
- **Socket Server** - รันบนเซิร์ฟเวอร์ของคุณเพื่อรับการเชื่อมต่อจากเครื่องเป้าหมาย (TCP Socket)

## ข้อสำคัญ

⚠️ Vercel เป็น serverless platform ที่ไม่รองรับ long-lived connections
ดังนั้นจึงแยก API ออกจาก Socket Server

- API จะรันบน Vercel
- Socket Server ต้องรันบน VPS/Server ของคุณเองโดยใช้ `proxy_server.py`
