# Vercel Deployment Guide

## ขั้นตอนการ Deploy

### 1. ติดตั้ง Git (ถ้ายังไม่ติดตั้ง)

Download จาก: https://git-scm.com/download/win

หลังติดตั้งเสร็จให้ restart terminal

### 2. ตั้งค่า Git (ครั้งแรกเท่านั้น)

```powershell
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

### 3. เตรียม Repository บน GitHub

- สร้าง repository ใหม่บน GitHub (ปิด "Initialize with README")
- คัดลอก URL ของ repository

### 4. ตั้งค่า Local Repository

```powershell
cd "C:\Users\Administrator\Desktop\Hook"

# สร้าง git repository
git init

# เพิ่มไฟล์ทั้งหมด
git add -A

# สร้าง initial commit
git commit -m "Initial commit: Vercel-ready API setup"

# เพิ่ม remote repository
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Push ไปที่ GitHub
git branch -M main
git push -u origin main
```

### 5. Deploy ไปที่ Vercel

**วิธีที่ 1: ใช้ Dashboard (ง่ายที่สุด)**

1. ไปที่ https://vercel.com
2. Log in ด้วย GitHub account
3. Click "Add New..." > "Project"
4. เลือก repository
5. Click "Deploy"

**วิธีที่ 2: ใช้ CLI**

```powershell
npm install -g vercel
vercel login
vercel
```

### 6. เตรียม Socket Server ของคุณ

Socket Server ต้องรันแยกต่างหากบน VPS/Server ของคุณ:

```bash
pip install -r requirements.txt
python proxy_server.py
```

## โครงสร้าง

```
api.py              ← Flask API (Deploy ไปที่ Vercel)
proxy_server.py     ← Socket Server (รันบน VPS ของคุณ)
vercel.json         ← Vercel config
requirements.txt    ← Python packages
.env.example        ← Environment variables template
README.md           ← Documentation
```

## URL หลังจาก Deploy

หลังจาก Deploy สำเร็จคุณจะได้ URL เช่น:

```
https://your-project-name.vercel.app
```

API Endpoints จะอยู่ที่:

```
GET    https://your-project-name.vercel.app/api/health
GET    https://your-project-name.vercel.app/api/targets
POST   https://your-project-name.vercel.app/api/register
POST   https://your-project-name.vercel.app/api/command
```

## Troubleshooting

### Build ไม่สำเร็จ

ตรวจสอบ:
- requirements.txt มี Flask และ flask-cors ถูกต้องหรือไม่?
- Python version ถูกต้องหรือไม่?

### API ไม่ทำงาน

ตรวจสอบ Vercel logs:
```powershell
vercel logs
```

---

**สำคัญ**: Socket Server (`proxy_server.py`) ต้องรันบน VPS/Server ของคุณ ไม่สามารถรันบน Vercel ได้เนื่องจากเป็น serverless platform
