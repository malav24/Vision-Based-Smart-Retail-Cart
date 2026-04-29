# Mobile iPhone Camera Integration - Complete Setup Guide

## 🚀 Overview

Your CV Project now supports **real-time object detection from an iPhone camera**. The laptop acts as a WebServer that processes frames sent from the iPhone and detects products in real-time.

---

## 📱 How It Works

### Architecture
```
iPhone → Camera Feed (getUserMedia API)
    ↓
Captures frames every 1 second
    ↓
Sends to Laptop Server (/api/mobile/detect)
    ↓
Server processes with YOLOv8 AI
    ↓
Returns detected products with confidence scores
    ↓
Display results on iPhone screen
    ↓
Add items to cart and checkout
```

---

## 🔧 Setup Instructions

### 1. **Install New Dependencies**
Run this command in your project directory:

```bash
pip install -r requirements.txt
```

New packages added:
- `python-socketio` - Real-time communication
- `python-engineio` - WebSocket support
- `aiofiles` - Async file handling
- `dropbox` - Dropbox integration (for future use)

### 2. **Start the Server**
From your laptop (Windows):

```bash
python app.py
```

The server will start on `http://0.0.0.0:5000`

### 3. **Access from iPhone**
- Connect your iPhone to the **same WiFi network** as your laptop
- Open Safari on iPhone
- Navigate to: `http://<laptop-ip>:5000/mobile/camera`

**To find your laptop IP:**
- On Windows PowerShell: `ipconfig` → Look for IPv4 Address
- Example: `http://192.168.1.100:5000/mobile/camera`

---

## 📹 Mobile Camera Features

### **Real-Time Detection**
- **Continuous Scanning**: Frames captured every 1 second
- **Live Detection Panel**: See detected items with confidence scores
- **Automatic Updates**: List refreshes as items are detected

### **Detection Interface**
- 📊 Confidence Score: Shows AI certainty (e.g., 95.3%)
- 💰 Price Display: Real-time pricing from database
- ➕ Add Individual Items: Click `+` button for any detected item
- 🛒 Add All at Once: "Add to Cart" button adds all detected items

### **Controls**
| Button | Function |
|--------|----------|
| 🔄 | Restart camera if connection issues |
| ⛶ | Toggle fullscreen mode (iOS) |
| 📸 Clear | Clear detection history |
| Add to Cart | Add all detected items to cart |

### **Status Indicators**
- 🟢 **Connected** - Ready to scan
- 🔵 **Items Detected** - Products found!
- ⚠️ **Error** - Connection or camera issue

---

## 🎯 Usage Workflow

### **Step 1: Open iPhone Camera**
1. On your iPhone, go to `http://192.168.1.X:5000/mobile/camera`
2. Allow camera access when prompted
3. Wait for "Connected" status

### **Step 2: Point at Items**
1. Position iPhone camera over items/products
2. Hold steady for 1-2 seconds
3. Detected items appear in bottom panel

### **Step 3: Add to Cart**
- **Option A**: Click `+` button on individual items
- **Option B**: Click "Add to Cart" to add all detected items at once

### **Step 4: Checkout**
1. Items saved to iPhone browser storage
2. Navigate to `/dropbox` on laptop for checkout
3. Click "Confirm & Generate Bill"

---

## 🗄️ Database Integration

### **Stored Detection Data**
Each detection is logged in `detection_logs` table:

```sql
-- Detection Log Entry
INSERT INTO detection_logs (detected_class, confidence, timestamp)
VALUES ('product_name', 0.95, CURRENT_TIMESTAMP)
```

### **Tracked Information**
- Product class name
- Confidence score (0.0 - 1.0)
- Detection timestamp
- Product ID (for billing)

---

## 🔗 API Endpoints

### **GET `/mobile/camera`**
Returns the mobile camera HTML interface

### **POST `/api/mobile/detect`**
Process a video frame and detect items

**Request:**
```
Content-Type: multipart/form-data
Body: image (binary JPG frame)
```

**Response:**
```json
{
  "success": true,
  "items": [
    {
      "product_id": 1,
      "product_name": "Product A",
      "price": 29.99,
      "confidence": 0.95,
      "class_name": "product_a"
    }
  ]
}
```

---

## 🛠️ File Structure

```
CV Project/
├── app.py                          # New routes added
├── templates/
│   └── dropbox/
│       ├── index.html              # Updated with mobile link
│       └── mobile_camera.html      # NEW - Mobile interface
├── core/
│   ├── cv_engine.py               # YOLO inference
│   └── db.py                       # Database queries
└── requirements.txt               # Updated dependencies
```

---

## 🎨 Mobile UI Features

### **Dark Mode Optimized**
- Designed for iPhone use in any lighting
- High contrast buttons and text
- Safe area support for iPhone notch

### **Real-Time Animations**
- Pulsing status dot
- Smooth item slide-in
- Detection count updates

### **Responsive Design**
- Works on all screen sizes
- Full iPhone camera access
- Fullscreen mode support

---

## ⚙️ Configuration

### **Detection Confidence Threshold**
In `app.py`, line in `mobile_detect()`:
```python
if item['confidence'] < 0.5:  # Lower threshold for mobile
    continue
```
Adjust `0.5` to change sensitivity:
- **Lower** (e.g., 0.3) = More detections, more false positives
- **Higher** (e.g., 0.8) = Fewer detections, higher accuracy

### **Frame Capture Rate**
In `mobile_camera.html`, line in `startCapturing()`:
```javascript
this.captureInterval = setInterval(() => this.captureFrame(), 1000);
```
Change `1000` (1 second) for different rates:
- **500** = Faster (2 FPS)
- **2000** = Slower (0.5 FPS)

---

## 🐛 Troubleshooting

### **iPhone Can't Connect to Server**
1. Check IP address: `ipconfig` on Windows
2. Ensure same WiFi network
3. Disable Windows Firewall temporarily
4. Try: `http://localhost:5000/mobile/camera` on laptop first

### **Camera Permission Denied**
1. Open Settings → Safari
2. Enable "Camera" access
3. Refresh the page

### **No Detections Appearing**
1. Check YOLOv8 model is loaded: Check console logs
2. Verify product database has entries with `model_class_name`
3. Lower confidence threshold in app.py
4. Test with `/api/dropbox/infer` endpoint first

### **Frames Processing Too Slow**
1. Reduce frame capture rate (increase interval)
2. Close other browser tabs
3. Check laptop CPU usage
4. Consider reducing video resolution

---

## 📊 Performance Tips

- **Best Performance**: 3-5 items in frame, good lighting
- **Frame Size**: 1280x720 auto-optimized for performance
- **Processing**: ~1-2 seconds per frame on modern laptop
- **Bandwidth**: Minimal data usage (compressed JPG frames)

---

## 🔒 Security Notes

- Server runs on `0.0.0.0:5000` (local network only)
- No authentication required (local network assumed trusted)
- For production: Add HTTPS, firewall rules, and authentication
- Detection data stored in local SQLite database

---

## 🚀 Next Steps

### Planned Enhancements
- [ ] Dropbox auto-save detected items
- [ ] WebRTC for lower latency
- [ ] Multi-phone support
- [ ] Real-time video stream (instead of frame captures)
- [ ] Batch processing optimization

### Current Limitations
- 1-2 second processing delay per frame
- Requires same WiFi network
- No real-time video stream display
- No browser tab background processing

---

## 📝 Example Usage Scenario

```
1. User opens iPhone camera at: http://192.168.1.50:5000/mobile/camera
2. Points at a shelf with products
3. AI detects: "Apple ($5.99), Orange ($3.99)" with 92% confidence
4. User clicks "Add to Cart"
5. Items stored in browser
6. User goes to desktop and accesses /dropbox
7. Sees cart items
8. Clicks "Confirm & Generate Bill"
9. Transaction complete ✅
```

---

## 📞 Support

If you encounter issues:
1. Check browser console (F12) for JavaScript errors
2. Check Flask console for backend errors
3. Verify all database tables exist
4. Ensure products have `model_class_name` values
5. Test frame capture on laptop first

---

**Happy detection! 🎯📱**
