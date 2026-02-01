# Catalyst AI Backend - Quick API Reference

## Base URL
```
http://localhost:8000  (development)
https://api.catalyst-ai.com  (production)
```

## Authentication
All endpoints require JWT token in header:
```
Authorization: Bearer <your_token>
```

---

## Authentication Endpoints

### Register User
```
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}

Response: 201 Created
{
  "id": "uuid",
  "email": "user@example.com",
  "created_at": "2024-02-01T10:00:00"
}
```

### Login
```
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}

Response: 200 OK
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

---

## Campaign Endpoints

### Generate Campaign (Main Endpoint)
```
POST /api/v1/campaigns/generate
Authorization: Bearer <token>
Content-Type: multipart/form-data

Form Data:
  product_name: string (required)
  brand_name: string (optional)
  price: string (optional)
  description: string (optional)
  campaign_goal: string (optional)
  target_audience: string (optional)
  brand_persona: string (optional)
  generate_video: boolean (optional, default: false)
  image: file (required)

Response: 200 OK
{
  "success": true,
  "campaign_id": "550e8400-e29b-41d4-a716-446655440000",
  "product_name": "Cotton T-Shirt",
  "category": "fashion_apparel",
  "content": {
    "title": "Premium Cotton Comfort",
    "hook": "Discover the perfect shirt",
    "main_content": "Our premium cotton blend...",
    "cta": "Shop now",
    "hashtags": ["#fashion", "#comfort"],
    "emotional_triggers": ["quality", "comfort"]
  },
  "poster_url": "/static/images/poster_550e8400.png",
  "video_url": "/static/videos/video_550e8400.mp4",
  "status": "completed",
  "created_at": "2024-02-01T10:30:00"
}
```

### Get Campaign
```
GET /api/v1/campaigns/campaigns/{campaign_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "success": true,
  "campaign_id": "550e8400-e29b-41d4-a716-446655440000",
  "product_name": "Cotton T-Shirt",
  "status": "completed",
  "created_at": "2024-02-01T10:30:00"
}
```

### List Campaigns
```
GET /api/v1/campaigns/list?skip=0&limit=10
Authorization: Bearer <token>

Response: 200 OK
{
  "success": true,
  "total": 5,
  "campaigns": [
    {
      "campaign_id": "550e8400-e29b-41d4-a716-446655440000",
      "product_name": "Cotton T-Shirt",
      "status": "completed",
      "created_at": "2024-02-01T10:30:00"
    }
  ]
}
```

---

## Project Endpoints (Alternative to Campaigns)

### Create Project
```
POST /projects/
Authorization: Bearer <token>
Content-Type: multipart/form-data

Form Data:
  product_name: string (required)
  brand_name: string (optional)
  price: string (optional)
  description: string (optional)
  campaign_goal: string (optional)
  target_audience: string (optional)
  brand_persona: string (optional)
  image: file (optional)

Response: 201 Created
{
  "id": "uuid",
  "product_name": "Product Name",
  "status": "created"
}
```

### List Projects
```
GET /projects/?skip=0&limit=100
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": "uuid",
    "product_name": "Product",
    "status": "created"
  }
]
```

### Get Project
```
GET /projects/{project_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "id": "uuid",
  "product_name": "Product",
  "brand_name": "Brand",
  "price": "$99",
  "status": "created",
  "image_path": "uploads/image.jpg"
}
```

---

## File Upload Endpoints

### Upload Image
```
POST /uploads/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

Form Data:
  file: image file
  project_id: uuid (optional)

Response: 200 OK
{
  "filename": "550e8400-uuid.jpg",
  "url": "/uploads/550e8400-uuid.jpg",
  "size": 102400
}
```

---

## Results Endpoints

### Get Campaign Results
```
GET /results/{project_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "project_id": "uuid",
  "category": "fashion_apparel",
  "content": { ... },
  "market_research": { ... },
  "video_url": "/static/videos/video.mp4",
  "poster_url": "/static/images/poster.png"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid image format. Supported: JPEG, PNG, WebP"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 404 Not Found
```json
{
  "detail": "Campaign not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Campaign generation failed: [error details]"
}
```

---

## Status Codes Reference

| Code | Status | Meaning |
|------|--------|---------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Missing/invalid token |
| 404 | Not Found | Resource not found |
| 500 | Server Error | Internal server error |

---

## Content Response Structure

Every campaign returns this content structure:

```json
{
  "category": {
    "category": "string",
    "subcategory": "string",
    "confidence": 0.95
  },
  "content": {
    "title": "string",
    "hook": "string",
    "main_content": "string",
    "cta": "string",
    "hashtags": ["string"],
    "emotional_triggers": ["string"]
  },
  "vision_analysis": {
    "features": ["string"],
    "quality_score": 8.5
  },
  "market_insights": {
    "trend": "string",
    "opportunity": "string",
    "competition": "string"
  },
  "performance_prediction": {
    "engagement_rate": 6.5,
    "reach_potential": "string",
    "best_posting_time": "string"
  }
}
```

---

## Frontend Integration Examples

### JavaScript/React
```javascript
const generateCampaign = async (productData, imageFile) => {
  const formData = new FormData();
  formData.append('product_name', productData.name);
  formData.append('image', imageFile);
  formData.append('generate_video', true);

  const response = await fetch('/api/v1/campaigns/generate', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });

  return response.json();
};
```

### Python
```python
import requests

response = requests.post(
    'http://localhost:8000/api/v1/campaigns/generate',
    headers={'Authorization': f'Bearer {token}'},
    data={
        'product_name': 'T-Shirt',
        'generate_video': False
    },
    files={'image': open('product.jpg', 'rb')}
)

campaign = response.json()
```

### cURL
```bash
curl -X POST http://localhost:8000/api/v1/campaigns/generate \
  -H "Authorization: Bearer <token>" \
  -F "product_name=T-Shirt" \
  -F "image=@product.jpg" \
  -F "generate_video=false"
```

---

## Response Times

- **Campaign Generation (no video)**: 30-45 seconds
- **Campaign Generation (with video)**: 2-3 minutes
- **Video Download**: 30-60 seconds
- **Poster Generation**: 10-20 seconds
- **Market Research**: 20-40 seconds

---

## Rate Limits

- **Campaign Generation**: 10 per hour per user
- **API Requests**: 100 per minute per user

If rate limit exceeded: HTTP 429 Too Many Requests

---

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)
- Maximum size: 25MB

---

## API Version

Current Version: **v1**
Base Path: **/api/v1**

---

## Useful Links

- [Full API Documentation](./FRONTEND_API_GUIDE.md)
- [Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [GitHub Repository](https://github.com/your-repo)
