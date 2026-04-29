# Quick Start - iPhone Camera Detection

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start Server
```bash
python app.py
```
Server runs on: `http://0.0.0.0:5000`

### Step 3: Open on iPhone
Get your laptop IP:
```powershell
ipconfig
```
Look for "IPv4 Address" (e.g., 192.168.1.100)

Then on iPhone Safari, go to:
```
http://192.168.1.100:5000/mobile/camera
```

---

## 📱 What You Get

✅ **Real-time object detection** from iPhone camera  
✅ **Product detection** with AI confidence scores  
✅ **Instant cart updates** on mobile  
✅ **Laptop-as-server** processing  
✅ **Dropbox integration** for checkout  

---

## 🎯 Features

| Feature | Description |
|---------|-------------|
| **Live Camera** | Stream from iPhone back camera |
| **Frame Capture** | 1 image per second processed |
| **Detection Panel** | Shows detected items with prices |
| **Confidence Score** | AI accuracy percentage |
| **Add to Cart** | Individual or bulk add items |
| **Status Badge** | Connected/Scanning/Detected states |

---

## 🔗 Key URLs

| URL | Purpose |
|-----|---------|
| `/mobile/camera` | iPhone camera interface |
| `/api/mobile/detect` | Frame processing API |
| `/dropbox` | Desktop checkout interface |
| `/admin/products` | Manage product database |

---

## ⚙️ How It Works

```
iPhone Camera
    ↓
Capture Frame (JPG)
    ↓
Send to Laptop Server
    ↓
YOLOv8 AI Detection
    ↓
Match to Products DB
    ↓
Return Detected Items
    ↓
Display on iPhone
    ↓
Add to Cart & Checkout
```

---

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| Can't connect | Check WiFi & use correct IP |
| No camera | Allow camera permissions in Safari |
| No detections | Lower confidence threshold in app.py |
| Slow processing | Close other apps/tabs |

---

## 📚 Full Documentation

See `MOBILE_CAMERA_SETUP.md` for complete guide with:
- Detailed architecture
- API endpoints
- Configuration options
- Troubleshooting
- Performance tips

---

**Version: 1.0 | Date: 2026-04-29**
