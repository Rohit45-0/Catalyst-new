# Catalyst AI Backend - For Frontend Integration

## What is This?

This is the **backend API server** for the Catalyst AI marketing automation platform. It provides REST endpoints for generating complete marketing campaigns (content, posters, videos) for any product.

## Quick Start for Frontend Developers

### 1. Prerequisites
- Backend server running (Python 3.10+)
- Postman or similar API client (optional)
- Your API authentication token

### 2. Main Integration Point

**One Endpoint Does Everything:**

```bash
POST /api/v1/campaigns/generate

Required:
  - product_name (string)
  - image (file: JPEG/PNG/WebP)

Optional:
  - brand_name
  - price
  - description
  - campaign_goal
  - target_audience
  - brand_persona
  - generate_video (boolean)

Returns:
  - campaign_id, content, poster_url, video_url, status, created_at
```

### 3. Authentication

All requests need a JWT token:

```javascript
// Get token
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}

// Use token in headers
Authorization: Bearer <token>
```

### 4. Response Example

```json
{
  "success": true,
  "campaign_id": "550e8400-e29b-41d4-a716-446655440000",
  "product_name": "Cotton T-Shirt",
  "category": "fashion_apparel",
  "content": {
    "title": "Premium Cotton Comfort",
    "hook": "Discover the perfect shirt",
    "main_content": "High-quality cotton blend...",
    "cta": "Shop now",
    "hashtags": ["#fashion", "#comfort"],
    "emotional_triggers": ["quality", "comfort"]
  },
  "poster_url": "/static/images/poster_550e8400.png",
  "video_url": null,
  "status": "completed",
  "created_at": "2024-02-01T10:30:00"
}
```

## Documentation Files

### For API Integration
- **[API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md)** - Copy-paste API endpoints and examples
- **[FRONTEND_API_GUIDE.md](./FRONTEND_API_GUIDE.md)** - Complete integration guide with React examples
- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Setup and deployment instructions

### For Testing
- **[test_api.py](./test_api.py)** - Python script to test all API endpoints
  ```bash
  python test_api.py --url http://localhost:8000
  python test_api.py --video  # Include video generation test
  ```

## API Endpoints Summary

| Endpoint | Purpose |
|----------|---------|
| `POST /api/v1/auth/register` | Create new account |
| `POST /api/v1/auth/login` | Get authentication token |
| `POST /api/v1/campaigns/generate` | **Generate marketing campaign** |
| `GET /api/v1/campaigns/campaigns/{id}` | Get campaign details |
| `GET /api/v1/campaigns/list` | List user's campaigns |

## What the Backend Does

When you call `/campaigns/generate`, the system:

1. **Analyzes** the product image using vision AI
2. **Researches** market trends and competitors
3. **Detects** product category and emotional triggers
4. **Generates** marketing copy and hooks
5. **Creates** a beautiful poster using DALL-E
6. **Optionally** generates a 10-second video using Sora-2
7. **Predicts** engagement metrics and performance
8. **Returns** all content ready to use

**Time:** 30-45 seconds (without video), 2-3 minutes (with video)

## Response Time Breakdown

- Vision Analysis: ~5 seconds
- Market Research: ~20 seconds  
- Content Generation: ~15 seconds
- Poster Generation: ~10 seconds
- Video Generation: ~120 seconds (optional)

## File Locations

Generated files are stored in:
- **Images**: `/static/images/poster_*.png`
- **Videos**: `/static/videos/video_*.mp4`
- **Uploads**: `/uploads/`

Access via HTTP:
```
https://api.catalyst-ai.com/static/images/poster_550e8400.png
https://api.catalyst-ai.com/static/videos/video_550e8400.mp4
```

## Content Structure Returned

```json
{
  "category": {
    "category": "fashion_apparel",
    "subcategory": "men's shirts",
    "confidence": 0.95
  },
  "content": {
    "title": "...",
    "hook": "...",
    "main_content": "...",
    "cta": "...",
    "hashtags": ["..."],
    "emotional_triggers": ["..."]
  },
  "vision_analysis": {
    "features": ["..."],
    "quality_score": 8.5
  },
  "market_insights": {
    "trend": "...",
    "opportunity": "...",
    "competition": "moderate"
  },
  "performance_prediction": {
    "engagement_rate": 6.5,
    "reach_potential": "50k-100k",
    "best_posting_time": "Tuesday 2-4 PM"
  }
}
```

## Common Errors & Solutions

### "Not authenticated"
- Missing or invalid JWT token
- **Solution**: Call login endpoint, use returned token in Authorization header

### "File must be an image"
- Invalid image file
- **Solution**: Use JPEG, PNG, or WebP format

### "Campaign generation failed"
- Backend error during processing
- **Solution**: Check server logs, verify all API keys configured

### "Timeout"
- Request took too long
- **Solution**: Set timeout to 300 seconds (5 min) for video generation

## Frontend Integration Examples

### React Hook
```javascript
const [campaign, setCampaign] = useState(null);
const [loading, setLoading] = useState(false);

const generateCampaign = async (productData, image) => {
  setLoading(true);
  try {
    const formData = new FormData();
    formData.append('product_name', productData.name);
    formData.append('image', image);
    formData.append('generate_video', false);

    const response = await fetch('/api/v1/campaigns/generate', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData
    });

    const data = await response.json();
    setCampaign(data);
  } finally {
    setLoading(false);
  }
};
```

### Vue 3 Composable
```javascript
import { ref } from 'vue'

export const useCampaignGenerator = (token) => {
  const campaign = ref(null)
  const loading = ref(false)

  const generate = async (productData, image) => {
    loading.value = true
    const formData = new FormData()
    formData.append('product_name', productData.name)
    formData.append('image', image)

    const response = await fetch('/api/v1/campaigns/generate', {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: formData
    })

    campaign.value = await response.json()
    loading.value = false
  }

  return { campaign, loading, generate }
}
```

## Getting Help

1. **API Documentation**: See [API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md)
2. **Examples**: See [FRONTEND_API_GUIDE.md](./FRONTEND_API_GUIDE.md)
3. **Test Script**: Run `python test_api.py` to verify setup
4. **Server Logs**: Check backend server output for errors
5. **GitHub Issues**: File issue with campaign_id and error message

## Architecture Overview

```
Frontend (React/Vue)
        ↓
API Gateway (/api/v1/campaigns)
        ↓
Authentication (JWT)
        ↓
Campaign Orchestrator
    ├─ Vision Analyzer (image analysis)
    ├─ Market Research (trends & competitors)
    ├─ Content Writer (marketing copy)
    ├─ Poster Generator (DALL-E)
    ├─ Video Creator (Sora-2)
    └─ Performance Predictor
        ↓
Database (PostgreSQL)
        ↓
Static Storage (/static/images, /videos)
        ↓
Frontend (display results)
```

## Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Use the campaign |
| 201 | Created | Resource created |
| 400 | Bad Request | Check your input |
| 401 | Unauthorized | Get new token |
| 404 | Not Found | Check campaign ID |
| 429 | Rate Limited | Wait and retry |
| 500 | Server Error | Check logs |

## Rate Limiting

- 10 campaigns per hour per user
- 100 API requests per minute per user

Rate limit info in response headers:
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 9
X-RateLimit-Reset: 1706780400
```

## Next Steps

1. **Read**: [API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md)
2. **Test**: Run `python test_api.py`
3. **Integrate**: Use examples from [FRONTEND_API_GUIDE.md](./FRONTEND_API_GUIDE.md)
4. **Deploy**: Follow [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

---

**Backend Version**: 0.1.0  
**API Version**: v1  
**Last Updated**: 2024-02-01
