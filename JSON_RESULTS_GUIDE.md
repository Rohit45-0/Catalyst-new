# 📊 Getting Workflow Results in JSON

## ✅ Yes, ALL Data is Stored in Database!

### Database Tables

#### 1. **`projects`** table stores:
```json
{
  "performance_prediction": {...},  // Phase 3.1 - Prediction scores
  "competitor_data": {...},         // Phase 2 - Competitor analysis
  "emotional_data": {...},          // Phase 2.2 - Emotional triggers
  "hook_data": {...}                // Phase 2.3 - Generated hooks
}
```

#### 2. **`jobs`** table stores:
```json
{
  "output_payload": {
    // Contains results from EVERY agent step:
    // - Vision analysis
    // - Market research
    // - Content generation
    // - Social media publishing (LinkedIn/Meta post IDs)
    // - Performance prediction
  }
}
```

#### 3. **`assets`** table stores:
```json
{
  "content": "...",                    // Generated posts (LinkedIn/Meta)
  "performance_metrics": {             // Phase 3.2 - Feedback data
    "likes": 150,
    "shares": 25,
    "clicks": 300
  }
}
```

## 🔌 New JSON API Endpoints

### 1. Get Complete Results
```bash
GET /results/projects/{project_id}/complete
```

**Returns:**
```json
{
  "project_id": "...",
  "status": "completed",
  "product_info": {
    "name": "Nike Air Max",
    "category": "tech_gadgets",
    "category_confidence": 0.99
  },
  "analysis": {
    "competitor_data": {...},
    "emotional_data": {...},
    "hook_data": {...},
    "performance_prediction": {
      "global_score": 85.0,
      "platform_predictions": {...}
    }
  },
  "jobs": {
    "vision_analysis": {...},
    "content_generation": {...},
    "social_media_publishing": {...}
  },
  "generated_content": [
    {
      "type": "linkedin_post",
      "content": {...},
      "performance_metrics": {
        "likes": 150,
        "clicks": 300
      }
    }
  ],
  "publishing_results": {
    "linkedin": {
      "status": "success",
      "data": {
        "id": "urn:li:share:7422908696298414080"
      }
    },
    "meta": {
      "status": "success",
      "data": {
        "id": "1012567998597853_122102379417232411"
      }
    }
  }
}
```

### 2. Get Summary
```bash
GET /results/projects/{project_id}/summary
```

**Returns:**
```json
{
  "project_id": "...",
  "product_name": "Nike Air Max",
  "status": "completed",
  "performance_score": 85.0,
  "posts_published": {
    "linkedin": "success",
    "meta": "success"
  },
  "total_assets": 3,
  "assets_with_metrics": 1
}
```

## 🚀 How to Use

### Option 1: Python Script
```bash
python get_results.py
```

This will:
1. Login automatically
2. Find your latest project
3. Fetch complete results
4. Save to `workflow_results.json`
5. Display a summary

### Option 2: Direct API Call
```bash
# 1. Login
curl -X POST http://localhost:8000/auth/login \
  -d "username=your@email.com&password=yourpassword"

# 2. Get results (replace {token} and {project_id})
curl -X GET http://localhost:8000/results/projects/{project_id}/complete \
  -H "Authorization: Bearer {token}"
```

### Option 3: Swagger UI
1. Go to http://localhost:8000/docs
2. Authorize with your credentials
3. Use `/results/projects/{project_id}/complete` endpoint

## 📁 Output File Structure

The `workflow_results.json` file contains:
- ✅ Product information
- ✅ All agent analysis results
- ✅ Generated content (LinkedIn/Meta posts)
- ✅ Performance predictions
- ✅ Publishing results (post IDs)
- ✅ Performance metrics (likes, shares, clicks)
- ✅ All job execution details

## 🔍 Example Usage

```python
import requests

# Get results
response = requests.get(
    "http://localhost:8000/results/projects/YOUR_PROJECT_ID/complete",
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

results = response.json()

# Access specific data
linkedin_post_id = results['publishing_results']['linkedin']['data']['id']
performance_score = results['analysis']['performance_prediction']['global_score']
likes = results['generated_content'][0]['performance_metrics']['likes']

print(f"LinkedIn Post: {linkedin_post_id}")
print(f"Score: {performance_score}/100")
print(f"Likes: {likes}")
```

## 📝 Notes

- All data persists in PostgreSQL (Supabase)
- JSONB columns allow flexible schema
- No data is lost between workflow runs
- You can query historical results anytime
