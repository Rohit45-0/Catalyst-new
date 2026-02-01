# 🚀 QUICK START - Test in 5 Minutes!

## ✅ PREREQUISITES
- [x] Server running
- [x] API keys configured in `.env`
- [x] Dependencies installed

---

## 🎯 5-STEP TEST

### **1. RESTART SERVER**
```bash
# Stop current server (Ctrl+C if running)
python -m uvicorn app.main:app --reload
```

### **2. OPEN SWAGGER UI**
```
http://localhost:8000/docs
```

### **3. AUTHENTICATE**
```
POST /auth/signup
{
  "email": "test@catalyst.ai",
  "password": "test123456"
}

Click "Authorize" → Login
```

### **4. CREATE PROJECT & START WORKFLOW**
```
POST /projects
- product_name: "iPhone 15 Pro Max"
- description: "Premium smartphone with titanium design"
- campaign_goal: "product launch"
- target_audience: "tech enthusiasts"
- brand_persona: "innovative, premium"

Copy project ID

POST /jobs/start/{project_id}
```

### **5. GET RESULTS**
```
GET /projects/{project_id}/assets
```

---

## ✅ SUCCESS = 3 AI-Generated Assets

- LinkedIn post
- Meta/Facebook post
- Blog post

---

## 🔧 IF SOMETHING FAILS

1. **Check `.env` has your API keys**
2. **Restart server**
3. **Check job errors:** `GET /jobs/project/{id}/status`

---

## 📚 FULL GUIDES

- **END_TO_END_TEST.md** - Complete testing guide
- **INTEGRATION_COMPLETE.md** - Full documentation

---

**🎉 READY TO TEST!**
