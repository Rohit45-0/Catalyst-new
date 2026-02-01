# Catalyst AI Backend - Frontend Integration Guide

## Overview

The Catalyst AI Backend provides a complete API for generating marketing campaigns. The system orchestrates 10+ specialized AI agents to analyze products, generate content, create videos, and publish to social media.

## Quick Start

### 1. Authentication

All endpoints require JWT authentication. Get a token first:

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

Include token in all requests:
```
Authorization: Bearer <token>
```

### 2. Generate Campaign

Create a complete marketing campaign for a product:

```bash
POST /api/v1/campaigns/generate
Authorization: Bearer <token>
Content-Type: multipart/form-data

Parameters:
- product_name: "Cotton T-Shirt" (required)
- brand_name: "Your Brand" (optional)
- price: "$29.99" (optional)
- description: "Premium cotton blend" (optional)
- campaign_goal: "brand awareness" (optional)
- target_audience: "Men 18-35" (optional)
- brand_persona: "Casual and friendly" (optional)
- image: <binary image file> (required, JPEG/PNG/WebP)
- generate_video: true/false (optional, default: false)

Response:
{
  "success": true,
  "campaign_id": "550e8400-e29b-41d4-a716-446655440000",
  "product_name": "Cotton T-Shirt",
  "category": "fashion_apparel",
  "content": {
    "title": "Premium Cotton Comfort",
    "hook": "Discover the perfect shirt for every occasion",
    "main_content": "Our premium cotton blend delivers...",
    "cta": "Shop now and feel the difference",
    "hashtags": ["#fashion", "#cottonshirt", "#comfort"]
  },
  "poster_url": "/static/images/poster_550e8400.png",
  "video_url": "/static/videos/video_550e8400.mp4",
  "status": "completed",
  "created_at": "2024-02-01T10:30:00"
}
```

**Response Time:**
- Without video: ~30-45 seconds
- With video: ~2-3 minutes

### 3. Retrieve Campaign

Get campaign details:

```bash
GET /api/v1/campaigns/campaigns/{campaign_id}
Authorization: Bearer <token>

Response:
{
  "success": true,
  "campaign_id": "550e8400-e29b-41d4-a716-446655440000",
  "product_name": "Cotton T-Shirt",
  "status": "completed",
  "created_at": "2024-02-01T10:30:00"
}
```

### 4. List Campaigns

Get all campaigns for the user:

```bash
GET /api/v1/campaigns/list?skip=0&limit=10
Authorization: Bearer <token>

Response:
{
  "success": true,
  "total": 5,
  "campaigns": [
    {
      "campaign_id": "550e8400-e29b-41d4-a716-446655440000",
      "product_name": "Cotton T-Shirt",
      "status": "completed",
      "created_at": "2024-02-01T10:30:00"
    },
    ...
  ]
}
```

## API Endpoints Reference

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | Login and get JWT token |
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/refresh` | Refresh JWT token |

### Campaign Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/campaigns/generate` | Generate new campaign |
| GET | `/api/v1/campaigns/campaigns/{id}` | Get campaign details |
| GET | `/api/v1/campaigns/list` | List user's campaigns |

### Project Endpoints (Advanced)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/projects/` | Create project |
| GET | `/projects/` | List projects |
| GET | `/projects/{id}` | Get project details |
| PUT | `/projects/{id}` | Update project |

### Results Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/results/{project_id}` | Get workflow results |

## Campaign Workflow

The system orchestrates the following phases:

### Phase 1: Analysis
- **Vision Analysis**: Analyzes product image to extract features
- **Category Detection**: Identifies product category with confidence score
- **Emotional Analysis**: Determines emotional triggers for the product

### Phase 2: Intelligence
- **Market Research**: Searches market trends and competitive landscape
- **Competitor Analysis**: Analyzes competitor products and positioning
- **Hook Generation**: Creates compelling hooks for marketing

### Phase 3: Content Generation
- **Content Writing**: Generates marketing copy
- **Poster Generation**: Creates visual poster using DALL-E
- **Video Generation**: Generates 10-second video using Sora-2 (if enabled)
- **Performance Prediction**: Predicts engagement metrics

### Phase 4: Publishing
- **Social Media Publishing**: Posts to LinkedIn, Instagram, Facebook
- **Results Storage**: Saves all results and metadata

## Content Structure

Each campaign returns structured content:

```json
{
  "category": {
    "category": "fashion_apparel",
    "subcategory": "men's shirts",
    "confidence": 0.95
  },
  "content": {
    "title": "Viral Marketing Title",
    "hook": "Attention-grabbing opening",
    "main_content": "Detailed product benefits",
    "cta": "Clear call to action",
    "hashtags": ["#trend1", "#trend2"],
    "emotional_triggers": ["quality", "comfort", "style"]
  },
  "vision_analysis": {
    "features": ["blue color", "cotton material", "classic fit"],
    "quality_score": 8.5
  },
  "market_insights": {
    "trend": "sustainable fashion",
    "opportunity": "eco-conscious consumers",
    "competition": "moderate"
  },
  "performance_prediction": {
    "engagement_rate": 6.5,
    "reach_potential": "50k-100k",
    "best_posting_time": "Tuesday 2-4 PM"
  }
}
```

## Error Handling

All errors return JSON with status code and message:

```json
{
  "detail": "Error message describing the issue"
}
```

### Common Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Campaign generated successfully |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid input parameters |
| 401 | Unauthorized | Missing or invalid token |
| 403 | Forbidden | Permission denied |
| 404 | Not Found | Resource not found |
| 500 | Server Error | Contact support |

## Frontend Implementation Example

### React Hook for Campaign Generation

```javascript
import { useState } from 'react';

export const useCampaignGenerator = (authToken) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const generateCampaign = async (productData, imageFile) => {
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('product_name', productData.name);
      formData.append('brand_name', productData.brand);
      formData.append('price', productData.price);
      formData.append('description', productData.description);
      formData.append('generate_video', productData.generateVideo);
      formData.append('image', imageFile);

      const response = await fetch(
        'http://localhost:8000/api/v1/campaigns/generate',
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${authToken}`
          },
          body: formData
        }
      );

      if (!response.ok) {
        throw new Error(await response.text());
      }

      const campaign = await response.json();
      return campaign;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { generateCampaign, loading, error };
};
```

## Configuration

The backend requires these environment variables (in `.env`):

```bash
# Database
DATABASE_URL=postgresql://user:password@host/dbname

# Azure OpenAI
AZURE_OPENAI_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# Video Generation
FASTROUTER_API_KEY=your-fastrouter-api-key

# Social Media
LINKEDIN_ACCESS_TOKEN=your-token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your-id
INSTAGRAM_ACCESS_TOKEN=your-token
FACEBOOK_PAGE_TOKEN=your-token

# Search
BRAVE_SEARCH_API_KEY=your-key

# JWT
JWT_SECRET=your-secret-key
```

## Rate Limiting

- **Campaign Generation**: 10 per hour per user
- **API Requests**: 100 per minute per user

## Best Practices

1. **Image Quality**: Use high-resolution product images (1000x1000 px minimum)
2. **Product Info**: Provide accurate product descriptions for better results
3. **Video Generation**: Only enable when needed (uses more time and resources)
4. **Error Handling**: Always handle 500 errors gracefully
5. **Polling**: Don't poll more than once every 5 seconds
6. **Assets**: Download and cache generated images/videos immediately

## Support

For issues or questions:
1. Check error message details
2. Verify authentication token is valid
3. Ensure image file is valid format
4. Check backend server logs
5. Contact support with campaign_id

## Version

Backend Version: 0.1.0
API Version: v1
Last Updated: 2024-02-01
