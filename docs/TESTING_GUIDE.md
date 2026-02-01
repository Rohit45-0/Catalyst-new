# 🧪 Catalyst AI Backend - Complete Testing Guide

## 🎯 Quick Start

**Server URL:** http://localhost:8000
**Swagger UI:** http://localhost:8000/docs
**OpenAPI Schema:** http://localhost:8000/openapi.json

---

## 📋 Testing Workflow (Step-by-Step)

### **Step 1: Test Signup** ✅

**Endpoint:** `POST /auth/signup`

**How to test in Swagger UI:**
1. Find the `/auth/signup` endpoint
2. Click "Try it out"
3. Enter the following JSON:
```json
{
  "email": "test@example.com",
  "password": "testpassword123"
}
```
4. Click "Execute"

**Expected Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "test@example.com"
}
```

**Notes:**
- ✅ First time: Creates new user
- ⚠️ Second time: Returns 400 "Email already registered" (this is correct!)

---

### **Step 2: Test Login (OAuth2)** ✅

**Endpoint:** `POST /auth/login`

**Method 1: Using Swagger's Authorize Button (Recommended)**

1. Click the 🔓 **Authorize** button (top right of Swagger UI)
2. In the OAuth2 dialog:
   - **username:** `test@example.com`
   - **password:** `testpassword123`
   - Leave `client_id` and `client_secret` empty
3. Click **Authorize**
4. Click **Close**

**Expected Result:**
- ✅ Green checkmark appears
- 🔒 Lock icon changes to locked
- You're now authenticated!

**Method 2: Direct Endpoint Test**

1. Find `/auth/login` endpoint
2. Click "Try it out"
3. Enter:
   - **username:** `test@example.com`
   - **password:** `testpassword123`
4. Click "Execute"

**Expected Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Notes:**
- Copy the `access_token` - you'll need it for protected endpoints
- Token expires in 30 minutes

---

### **Step 3: Test Protected Endpoint** ✅

**Endpoint:** `GET /auth/me`

**Prerequisites:** You must be authenticated (use Method 1 from Step 2)

**How to test:**
1. Make sure you clicked "Authorize" and logged in
2. Find `/auth/me` endpoint
3. Click "Try it out"
4. Click "Execute"

**Expected Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "test@example.com"
}
```

**If you get 401 Unauthorized:**
- Click "Authorize" again and login
- Make sure you used the correct credentials

---

## 🔐 Understanding OAuth2 Flow

```
┌─────────────┐
│   Signup    │  Create account
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Login    │  Get JWT token
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Use Token  │  Access protected endpoints
└─────────────┘
```

---

## 🧪 Testing with Python Script

I've created `test_oauth_fix.py` for automated testing:

```bash
python test_oauth_fix.py
```

This will automatically test:
- ✅ CORS headers
- ✅ User signup
- ✅ OAuth2 login
- ✅ Protected endpoint access

---

## 🛠️ Manual Testing with cURL

### 1. Signup
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpassword123"}'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpassword123"
```

**Save the token from response!**

### 3. Get Current User
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 🐍 Testing with Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Signup
signup_response = requests.post(
    f"{BASE_URL}/auth/signup",
    json={"email": "test@example.com", "password": "testpassword123"}
)
print("Signup:", signup_response.json())

# 2. Login
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "test@example.com", "password": "testpassword123"}
)
token = login_response.json()["access_token"]
print("Token:", token[:50] + "...")

# 3. Get current user
me_response = requests.get(
    f"{BASE_URL}/auth/me",
    headers={"Authorization": f"Bearer {token}"}
)
print("User:", me_response.json())
```

---

## 🎯 Common Test Scenarios

### ✅ Successful Scenarios

| Test Case | Endpoint | Expected Result |
|-----------|----------|-----------------|
| New user signup | POST /auth/signup | 201 Created |
| Valid login | POST /auth/login | 200 OK + token |
| Access with valid token | GET /auth/me | 200 OK + user data |

### ❌ Error Scenarios (These should fail!)

| Test Case | Endpoint | Expected Result |
|-----------|----------|-----------------|
| Duplicate email | POST /auth/signup | 400 Bad Request |
| Wrong password | POST /auth/login | 401 Unauthorized |
| No token | GET /auth/me | 401 Unauthorized |
| Invalid token | GET /auth/me | 401 Unauthorized |
| Expired token | GET /auth/me | 401 Unauthorized |

---

## 🔍 Troubleshooting

### Issue: "Failed to fetch" error
**Solution:** ✅ Already fixed with CORS middleware!

### Issue: 401 Unauthorized on /auth/me
**Solutions:**
1. Click "Authorize" in Swagger UI
2. Login with correct credentials
3. Make sure token hasn't expired (30 min)

### Issue: 400 "Email already registered"
**Solution:** This is correct! Use a different email or login with existing account

### Issue: Can't see endpoints in Swagger
**Solution:** Refresh the page (Ctrl+F5)

---

## 📊 Testing Checklist

Use this checklist to verify everything works:

- [ ] Server starts without errors
- [ ] Swagger UI loads at http://localhost:8000/docs
- [ ] Can create new user with POST /auth/signup
- [ ] Can login with POST /auth/login
- [ ] Receive JWT token after login
- [ ] Can authorize in Swagger UI
- [ ] Can access GET /auth/me with token
- [ ] Get 401 error when accessing /auth/me without token
- [ ] Get 400 error when signing up with duplicate email
- [ ] Get 401 error when logging in with wrong password

---

## 🚀 Next Steps After Testing

Once authentication is working, you can proceed with:

1. **Create Projects API**
   - POST /projects - Create new project
   - GET /projects - List user's projects
   - GET /projects/{id} - Get project details

2. **Upload Images**
   - POST /uploads/image - Upload product image

3. **Agent Orchestration**
   - POST /jobs/start - Trigger agent workflow
   - GET /jobs/{id} - Check job status

4. **View Results**
   - GET /projects/{id}/assets - Get generated content

---

## 💡 Pro Tips

1. **Use Swagger's "Authorize" button** - It's the easiest way to test
2. **Keep the token** - Copy it if you need to test with other tools
3. **Check the response codes** - They tell you what's happening
4. **Read error messages** - They explain what went wrong
5. **Test error cases too** - Make sure validation works

---

## 📞 Quick Reference

| What | Where |
|------|-------|
| Swagger UI | http://localhost:8000/docs |
| API Docs | http://localhost:8000/redoc |
| OpenAPI Schema | http://localhost:8000/openapi.json |
| Health Check | http://localhost:8000/ |

---

**Status:** 🟢 Ready for Testing!

Start with Step 1 (Signup) and work your way through. The OAuth2 error is fixed and everything should work smoothly! 🎉
