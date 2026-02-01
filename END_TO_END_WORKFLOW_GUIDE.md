# 🚀 End-to-End Catalyst AI Workflow Test

This guide explains how to run the complete marketing campaign pipeline from product image to published content on all social media platforms.

---

## 📋 What This Test Does

```
IMAGE UPLOAD
    ↓
PHASE 1: ANALYSIS
  - Category Detection
  - Vision Analysis
    ↓
PHASE 2: STRATEGIC INTELLIGENCE
  - Market Research (Brave API)
  - Competitor Visual Analysis
  - Emotional Trigger Mapping
  - Hook Generation
    ↓
PHASE 3: CONTENT & ASSET GENERATION
  - Platform-Specific Content (LinkedIn, Instagram, Facebook)
  - Poster Generation (DALL-E via FastRouter)
  - Video Generation (Sora-2 via FastRouter) ⚠️ LIMITED CREDITS
  - Performance Prediction
    ↓
PHASE 4: PUBLISHING
  - LinkedIn (Professional Post + Poster)
  - Instagram (Caption + Video Reel)
  - Facebook (Meta Graph API Post + Poster)
```

---

## ✅ Prerequisites

### 1. **Database Setup**
Make sure PostgreSQL/Supabase is running and `.env` has `DATABASE_URL`:
```bash
DATABASE_URL=postgresql://user:password@host:port/database
```

### 2. **API Credentials (All in `.env`)**
```bash
# Azure OpenAI (GPT-4o for content generation)
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_KEY=...

# Brave Search (Market Research)
BRAVE_API_KEY=...

# FastRouter (DALL-E Posters + Sora-2 Videos)
FASTROUTER_API_KEY=sk-v1-...

# LinkedIn
LINKEDIN_ACCESS_TOKEN=...
LINKEDIN_PERSON_ID=...
LINKEDIN_ORGANIZATION_ID=...

# Meta/Facebook/Instagram
META_ACCESS_TOKEN=...
META_PAGE_ID=...
INSTAGRAM_BUSINESS_ID=...
```

### 3. **Test Images**
Place product images in `uploads/` folder:
- The script automatically selects the first available image
- Supported formats: `.jpg`, `.png`

**Example:**
```
uploads/
├── test_upload_trigger.jpg ✅
├── fitted_hf_test_upload_trigger.jpg ✅
└── ...
```

---

## 🎯 Running the Test

### **Option 1: DRY RUN (Recommended First Time)**
Preview the entire workflow WITHOUT posting to social media:

```bash
python end_to_end_workflow.py --dry-run
```

**Output:**
```
[2026-02-01 10:30:45] 📍 Setting up database...
[2026-02-01 10:30:46] ✅ Database tables created/verified
[2026-02-01 10:30:47] 📍 Creating/retrieving test user...
[2026-02-01 10:30:48] ✅ Using existing test user: test@catalyst-ai.com
[2026-02-01 10:30:49] 📍 Selecting test image from uploads/...
[2026-02-01 10:30:50] ✅ Selected image: test_upload_trigger.jpg

[2026-02-01 10:30:51] 📍 ============================================================
[2026-02-01 10:30:51] 📍 PHASE 1: ANALYSIS
[2026-02-01 10:30:51] 📍 ============================================================
[2026-02-01 10:30:52] ✅ Category detected: footwear (sneakers)
[2026-02-01 10:30:55] ✅ Product identified: Nike Air Max
...
```

### **Option 2: Full Workflow with Posting (NO Video)**
Generate and publish content WITHOUT creating videos (saves SORA credits):

```bash
python end_to_end_workflow.py
```

### **Option 3: Full Workflow WITH Video Generation**
⚠️ **WARNING:** Uses SORA credits - only do this after verifying content quality!

```bash
python end_to_end_workflow.py --generate-video
```

**You'll be prompted:**
```
✋ About to generate VIDEO (uses SORA credits). Continue? (yes/no): 
```

Type `yes` only if you've reviewed the content and want to proceed.

---

## 📊 Understanding the Output

### **Successful Run**
```json
{
  "timestamp": "2026-02-01T10:35:00.123456",
  "dry_run": true,
  "skip_video": true,
  "phases": {
    "category": {
      "category": "footwear",
      "subcategory": "sneakers",
      "confidence": 0.95
    },
    "vision": {
      "product_name": "Nike Air Max",
      "category": "footwear",
      "primary_colors": ["white", "red", "black"],
      "material": "synthetic leather",
      "key_features": ["air cushioning", "lightweight", "comfortable"],
      "target_demographic": "athletes, casual wearers",
      "visual_style": "modern, minimalist",
      "selling_points": ["durability", "comfort", "style"]
    },
    "market": {
      "trends": ["minimalist design", "sustainable materials"],
      "price_range": "$80-$150",
      "top_competitors": ["Adidas Ultraboost", "New Balance 990"],
      "market_gap": "Premium comfort at mid-range price"
    },
    "competitor": {
      "analysis": {
        "visual_trends": ["white/neutral colors", "minimalist design"],
        "differentiation_score": 7.5,
        "opportunities": ["unique color variants", "sustainability messaging"]
      }
    },
    "emotional": {
      "primary_emotion": "confidence",
      "psychological_triggers": ["aspiration", "exclusivity", "status"],
      "messaging_hooks": ["Performance meets style", "The athlete's choice"]
    },
    "hooks": {
      "best_hook": "From training ground to street style.",
      "alternatives": ["Engineered for champions.", "Comfort that powers your day."]
    },
    "content": {
      "linkedin_post": {
        "title": "Innovation in Motion",
        "content": "Discover how modern footwear technology...",
        "hashtags": ["#innovation", "#footwear", "#technology"]
      },
      "instagram_post": {
        "caption": "From training ground to street style. 👟",
        "hashtags": ["#sneakerculture", "#style", "#comfort"]
      },
      "facebook_post": {
        "caption": "Premium comfort meets modern design...",
        "hashtags": ["#footwear", "#style"]
      }
    },
    "poster": {
      "status": "success",
      "poster_path": "/static/images/poster_a1b2c3d4.png",
      "prompt": "A high-quality advertisement poster for 'Nike Air Max'..."
    },
    "video": {
      "status": "skipped",
      "reason": "SORA credits preserved",
      "video_script": {
        "script": "Shot 1: Close-up of Nike Air Max...",
        "scenes": ["showcase", "fit", "lifestyle"]
      }
    },
    "performance": {
      "platform_scores": {
        "linkedin": 87,
        "instagram": 92,
        "facebook": 85
      },
      "predicted_kpis": {
        "linkedin": {"expected_reach": 5000, "engagement_rate": 0.08},
        "instagram": {"expected_reach": 8000, "engagement_rate": 0.12}
      }
    },
    "publishing": {
      "linkedin": {
        "status": "dry_run"
      },
      "instagram": {
        "status": "dry_run"
      },
      "facebook": {
        "status": "dry_run"
      }
    }
  }
}
```

**Saved to:** `workflow_results_final.json`

### **Results File Structure**
```
{
  "timestamp": "ISO format timestamp",
  "dry_run": boolean,
  "skip_video": boolean,
  "phases": {
    "category": {...},
    "vision": {...},
    "market": {...},
    "competitor": {...},
    "emotional": {...},
    "hooks": {...},
    "content": {...},
    "poster": {...},
    "video": {...},
    "performance": {...},
    "publishing": {
      "linkedin": {"status": "success|failed|dry_run", ...},
      "instagram": {"status": "success|failed|dry_run", ...},
      "facebook": {"status": "success|failed|dry_run", ...}
    }
  }
}
```

---

## 🔍 Troubleshooting

### **Error: "uploads/ folder not found"**
Solution: Create the uploads folder and add test images
```bash
mkdir uploads
# Add your product images to uploads/
```

### **Error: "Database tables creation failed"**
Solution: Verify `DATABASE_URL` in `.env` and ensure PostgreSQL is running
```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

### **Error: "Azure OpenAI credentials not found"**
Solution: Ensure these are in `.env`:
```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-key-here
AZURE_DEPLOYMENT_NAME=gpt-4o
```

### **Error: "Brave API key not found"**
Solution: Set `BRAVE_API_KEY` in `.env`
```bash
BRAVE_API_KEY=your-brave-api-key
```

### **Error: "LinkedIn publishing failed"**
Solution: Verify LinkedIn credentials are fresh
- LinkedIn Access Tokens expire - get a fresh one from [LinkedIn Developer Portal](https://www.linkedin.com/developers/apps)
- Ensure `LINKEDIN_PERSON_ID` and `LINKEDIN_ORGANIZATION_ID` are correct

### **Error: "Poster generation failed"**
Solution: Check FastRouter API key and DALL-E quota
```bash
FASTROUTER_API_KEY=sk-v1-your-key-here
```

### **Error: "Video generation cancelled"**
This is normal - the system prompts before using SORA credits. Type `yes` to proceed or `no` to skip.

---

## 💡 Tips & Best Practices

### **1. Start with Dry Run**
Always test with `--dry-run` first to catch configuration issues before making API calls.

### **2. Monitor SORA Credits**
- Check your FastRouter dashboard: https://go.fastrouter.ai/dashboard
- Each video generation uses credits
- Use `--generate-video` only after confirming content quality

### **3. Save Results**
Each run saves to `workflow_results_final.json` - review this file before posting to social media.

### **4. Test with Real Images**
Replace the test images in `uploads/` with your actual product photos for best results.

### **5. Verify Content**
Before running with `--generate-video`:
1. Check `workflow_results_final.json` content quality
2. Review generated posts and hooks
3. Ensure performance predictions are acceptable (scores > 80/100)

---

## 🚀 Production Workflow

For production use, consider:

1. **Batch Processing:**
   ```bash
   for image in uploads/*.jpg; do
     python end_to_end_workflow.py "$image"
   done
   ```

2. **Scheduled Runs (Cron):**
   ```bash
   # Daily at 9 AM
   0 9 * * * cd /path/to/catalyst-ai-backend && python end_to_end_workflow.py
   ```

3. **Error Monitoring:**
   - Review `workflow_results_final.json` for failures
   - Set up alerts for any "failed" status

4. **API Rate Limiting:**
   - Brave Search: Max 2 queries per product (already optimized)
   - OpenAI: Monitor token usage
   - FastRouter: Monitor SORA credit balance

---

## 📞 Getting Help

1. **Check Logs:** Look at console output for error messages
2. **Review Results:** `workflow_results_final.json` contains detailed error info
3. **Verify APIs:** Test individual API keys in `.env`
4. **Database:** Ensure tables exist: `SELECT * FROM projects;`

---

## ✨ Next Steps

- ✅ Run with `--dry-run` to verify setup
- ✅ Review `workflow_results_final.json`
- ✅ Run full workflow to generate and post content
- ✅ Use `--generate-video` only when confident in content quality

Good luck! 🎉
