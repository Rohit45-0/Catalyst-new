# 🎯 CATALYST AI - END-TO-END WORKFLOW TEST SUITE

## 📦 What's Included

Your complete end-to-end testing solution with 3 components:

### 1. **Main Workflow Script** (`end_to_end_workflow.py`)
Complete Python orchestrator that:
- Loads product image from `uploads/`
- Creates project in database
- Runs all 8 agents in sequence
- Generates poster (DALL-E)
- Generates video (Sora-2) with credit protection
- Publishes to LinkedIn, Instagram, Facebook
- Saves results to JSON

### 2. **Quick Start Launchers**
- `run_workflow.bat` - Windows batch file
- `run_workflow.sh` - Linux/Mac shell script

### 3. **Documentation**
- `END_TO_END_WORKFLOW_GUIDE.md` - Complete usage guide
- `THIS_FILE.md` - Overview & getting started

---

## 🚀 Quick Start (Choose Your Path)

### **Path 1: Windows Users**
```bash
# Run from PowerShell or Command Prompt
.\run_workflow.bat
```
Then select option from menu.

### **Path 2: Linux/Mac Users**
```bash
# Make script executable
chmod +x run_workflow.sh

# Run it
./run_workflow.sh
```
Then select option from menu.

### **Path 3: Direct Python Execution**
```bash
# Test without posting (recommended first time)
python end_to_end_workflow.py --dry-run

# Full workflow (generates content, posts to social media)
python end_to_end_workflow.py

# Full workflow WITH video generation (uses SORA credits)
python end_to_end_workflow.py --generate-video
```

---

## 📋 Workflow Steps (What Happens)

```
START
  ↓
[1] SETUP
  ├─ Create database tables
  ├─ Load/create test user
  ├─ Select product image from uploads/
  └─ Create project record

  ↓
[2] PHASE 1: ANALYSIS
  ├─ Category Detection → Identifies product type
  └─ Vision Analysis → Analyzes product image

  ↓
[3] PHASE 2: STRATEGIC INTELLIGENCE
  ├─ Market Research (Brave API) → Trends, competitors, pricing
  ├─ Competitor Visual Analysis → Competitor images & SWOT
  ├─ Emotional Trigger Mapping → Psychological hooks
  └─ Hook Generation → Best hooks for engagement

  ↓
[4] PHASE 3: CONTENT & ASSETS
  ├─ Content Writer → LinkedIn, Instagram, Facebook posts
  ├─ Poster Generator (DALL-E) → Creates promotional poster
  ├─ Video Creator (Sora-2) → Creates short-form video [OPTIONAL - CREDITS]
  └─ Performance Predictor → Scores content (0-100)

  ↓
[5] PHASE 4: PUBLISHING
  ├─ LinkedIn → Posts professional content + poster
  ├─ Instagram → Posts caption + video reel
  └─ Facebook → Posts via Meta API + poster

  ↓
[6] RESULTS
  └─ Save to workflow_results_final.json
```

---

## ⚙️ Configuration Requirements

### **MUST HAVE in `.env`:**

```bash
# Database
DATABASE_URL=postgresql://user:pass@host/db

# Azure OpenAI (Content Generation)
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_KEY=...
AZURE_DEPLOYMENT_NAME=gpt-4o

# Brave Search (Market Research)
BRAVE_API_KEY=your-key

# FastRouter (DALL-E Posters + Sora-2 Videos)
FASTROUTER_API_KEY=sk-v1-your-key

# LinkedIn
LINKEDIN_ACCESS_TOKEN=...
LINKEDIN_PERSON_ID=...
LINKEDIN_ORGANIZATION_ID=...

# Meta/Facebook/Instagram
META_ACCESS_TOKEN=...
META_PAGE_ID=...
INSTAGRAM_BUSINESS_ID=...
```

### **Check Your Setup:**
```bash
# Verify all keys exist
grep -E "AZURE_|BRAVE_|FASTROUTER_|LINKEDIN_|META_|INSTAGRAM_" .env

# Test database connection
psql $DATABASE_URL -c "SELECT 1"
```

---

## 🎯 Three Ways to Run

### **Option 1: DRY RUN ✅ (Recommended First)**
```bash
python end_to_end_workflow.py --dry-run
```

**What happens:**
- ✅ Runs ALL agents
- ✅ Generates content
- ✅ Generates poster
- ✅ Generates video metadata
- ❌ DOES NOT post to social media
- ❌ DOES NOT use SORA credits

**Use this to:**
- Verify setup is correct
- See what content looks like
- Check for errors before posting
- Preserve SORA credits for production

---

### **Option 2: FULL WORKFLOW (No Video)**
```bash
python end_to_end_workflow.py
```

**What happens:**
- ✅ Runs ALL agents
- ✅ Generates content
- ✅ Generates poster (DALL-E)
- ✅ Posts to LinkedIn, Instagram, Facebook
- ⏭️ SKIPS video generation (preserves SORA credits)

**Use this to:**
- Generate and post real content
- Build your social media presence
- Save SORA credits for later

---

### **Option 3: FULL WORKFLOW + VIDEO ⚠️**
```bash
python end_to_end_workflow.py --generate-video
```

**What happens:**
- ✅ Runs ALL agents
- ✅ Generates content
- ✅ Generates poster (DALL-E)
- ✅ **Generates video (Sora-2)** ⚠️ USES CREDITS
- ✅ Posts everything to LinkedIn, Instagram, Facebook

**You'll be prompted:**
```
✋ About to generate VIDEO (uses SORA credits). Continue? (yes/no): 
```

**Use this to:**
- Create complete marketing campaigns with video
- Only after verifying content quality from Option 2
- When you have SORA credits available

---

## 📊 Understanding Results

### **File: `workflow_results_final.json`**

Saved after each run. Contains:
```json
{
  "timestamp": "2026-02-01T10:30:45.123456",
  "dry_run": false,
  "skip_video": true,
  "phases": {
    "category": { ... },      // Step 1: Category detected
    "vision": { ... },        // Step 2: Product analyzed
    "market": { ... },        // Step 3: Market researched
    "competitor": { ... },    // Step 4: Competitors analyzed
    "emotional": { ... },     // Step 5: Emotional triggers found
    "hooks": { ... },         // Step 6: Best hooks generated
    "content": { ... },       // Step 7: Posts generated
    "poster": { ... },        // Step 8: Poster created
    "video": { ... },         // Step 9: Video created (or skipped)
    "performance": { ... },   // Step 10: Performance scored
    "publishing": {           // Step 11: Published results
      "linkedin": { "status": "success", "post_id": "..." },
      "instagram": { "status": "success", "post_id": "..." },
      "facebook": { "status": "success", "post_id": "..." }
    }
  }
}
```

### **Reading the Results:**

**Success Indicators:**
```json
{
  "publishing": {
    "linkedin": {
      "status": "success",
      "post_id": "123456789",
      "url": "https://linkedin.com/feed/..."
    }
  }
}
```

**Error Handling:**
```json
{
  "publishing": {
    "linkedin": {
      "status": "failed",
      "error": "Access token expired",
      "suggestion": "Refresh LINKEDIN_ACCESS_TOKEN in .env"
    }
  }
}
```

---

## 🔧 Troubleshooting

### **Problem: "uploads/ folder not found"**
```bash
mkdir uploads
# Add your product images here
cp /path/to/product.jpg uploads/
```

### **Problem: "Database connection failed"**
```bash
# Check DATABASE_URL in .env
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

### **Problem: "Azure OpenAI key not found"**
```bash
# Verify key is in .env
grep AZURE_OPENAI_KEY .env

# Test key works
curl -X POST https://your-endpoint/chat/completions \
  -H "api-key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o"}'
```

### **Problem: "LinkedIn posting failed"**
LinkedIn access tokens expire! Get fresh one:
1. Go to: https://www.linkedin.com/developers/apps
2. Generate new access token
3. Update `.env` → `LINKEDIN_ACCESS_TOKEN`

### **Problem: "Video generation cancelled"**
This is normal. You're prompted to confirm before using SORA credits.
```
✋ About to generate VIDEO (uses SORA credits). Continue? (yes/no): yes
```

Type `yes` to confirm.

---

## 💡 Best Practices

### **1. Always Start with Dry Run**
```bash
# First time
python end_to_end_workflow.py --dry-run

# Check results
cat workflow_results_final.json | jq '.phases'

# If OK, run for real
python end_to_end_workflow.py
```

### **2. Monitor SORA Credits**
- Check FastRouter dashboard: https://go.fastrouter.ai/dashboard
- Each video = X credits
- Use `--generate-video` sparingly

### **3. Review Content Quality**
Before posting:
1. Check `workflow_results_final.json`
2. Review generated posts
3. Check performance predictions (should be > 80/100)
4. Only then run without `--dry-run`

### **4. Set Up Logging**
Save output to file:
```bash
python end_to_end_workflow.py 2>&1 | tee workflow_run.log
```

### **5. Batch Multiple Products**
```bash
#!/bin/bash
for image in uploads/*.jpg; do
  echo "Processing $image..."
  python end_to_end_workflow.py --dry-run
  read -p "OK to post? (yes/no): " ok
  if [ "$ok" = "yes" ]; then
    python end_to_end_workflow.py
  fi
done
```

---

## 🚀 Production Deployment

### **Schedule Daily Runs (Linux/Mac):**
```bash
# Add to crontab
crontab -e

# Daily at 9 AM
0 9 * * * cd /path/to/catalyst-ai && python end_to_end_workflow.py >> workflow.log 2>&1
```

### **Monitor for Failures:**
```bash
# Check for errors
grep "ERROR\|failed" workflow_results_final.json

# Alert if video generation fails
grep -q "video.*failed" workflow_results_final.json && \
  echo "WARNING: Video generation failed" | mail -s "Catalyst AI Alert" you@example.com
```

### **API Rate Limiting:**
- Brave Search: 2 queries per product (optimized)
- Azure OpenAI: ~3-4 API calls per run
- FastRouter: 1 image gen + 1 video gen (if enabled)
- Social APIs: 1 post per platform

---

## 📞 Support

**Having issues?**

1. **Check logs:** Console output shows detailed errors
2. **Review results:** `workflow_results_final.json` has error details
3. **Verify setup:** Ensure all `.env` keys are present
4. **Test APIs individually:** Verify each service works
5. **Check documentation:** [END_TO_END_WORKFLOW_GUIDE.md](END_TO_END_WORKFLOW_GUIDE.md)

---

## ✨ What's Next?

- [x] ✅ End-to-end test file created
- [x] ✅ All agents integrated
- [x] ✅ Social media publishing configured
- [x] ✅ SORA video generation with credit protection
- [ ] 📱 Add Mobile UI for preview
- [ ] 📊 Add Analytics dashboard
- [ ] 🔄 Add feedback loop for continuous improvement
- [ ] 🎨 Add design variations generator

---

## 🎉 Ready to Go!

```bash
# Choose your launcher
./run_workflow.sh          # Linux/Mac
.\run_workflow.bat         # Windows

# Or direct execution
python end_to_end_workflow.py --dry-run
```

**Good luck! 🚀**
