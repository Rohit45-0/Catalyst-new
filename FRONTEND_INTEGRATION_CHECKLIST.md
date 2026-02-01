# Frontend Team Integration Checklist

## Before Starting

- [ ] Backend server running and accessible
- [ ] Environment variables configured (see `.env.example`)
- [ ] Test image available in `uploads/` directory
- [ ] Python 3.10+ and pip installed (for testing)

## Documentation Review (5 minutes)

Read in this order:

1. **[FRONTEND_README.md](./FRONTEND_README.md)** - START HERE
   - Overview of what the backend does
   - Quick start guide
   - 10 minute read

2. **[API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md)** - API Reference
   - All endpoints with examples
   - Request/response formats
   - 5 minute scan

3. **[FRONTEND_API_GUIDE.md](./FRONTEND_API_GUIDE.md)** - Full Documentation
   - Complete integration guide
   - React example code
   - 15 minute read

## Verify Backend Setup (5 minutes)

### Option 1: Run Test Script (Recommended)
```bash
# Install requests if needed
pip install requests

# Run tests
python test_api.py

# Expected output: All tests should pass ✓
```

### Option 2: Manual Verification
```bash
# Check server is running
curl http://localhost:8000/
# Expected: {"status": "ok", "service": "Catalyst AI Backend"}

# Check authentication endpoint
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test"}'
```

## Implement Frontend Integration (30 minutes)

### Step 1: Authentication (5 minutes)

**Create login function:**
```javascript
const login = async (email, password) => {
  const response = await fetch('/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const { access_token } = await response.json();
  localStorage.setItem('token', access_token);
  return access_token;
};
```

**Test it:**
- [ ] User can login
- [ ] Token is received
- [ ] Token stored in localStorage

### Step 2: Campaign Generation (10 minutes)

**Create campaign function:**
```javascript
const generateCampaign = async (productName, imageFile) => {
  const token = localStorage.getItem('token');
  const formData = new FormData();
  formData.append('product_name', productName);
  formData.append('image', imageFile);
  formData.append('generate_video', false); // true for video
  
  const response = await fetch('/api/v1/campaigns/generate', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData
  });
  
  return response.json();
};
```

**Test it:**
- [ ] Can upload image
- [ ] Campaign generated successfully
- [ ] Response includes content, poster_url, video_url
- [ ] Poster loads from URL
- [ ] Campaign ID returned

### Step 3: Display Results (10 minutes)

**Create display component:**
```javascript
const CampaignResults = ({ campaign }) => (
  <div>
    <h2>{campaign.content.title}</h2>
    <p>Category: {campaign.category}</p>
    <img src={campaign.poster_url} alt="Poster" />
    <p>{campaign.content.main_content}</p>
    <p>CTA: {campaign.content.cta}</p>
    <p>Hashtags: {campaign.content.hashtags.join(', ')}</p>
    {campaign.video_url && (
      <video src={campaign.video_url} controls></video>
    )}
  </div>
);
```

**Test it:**
- [ ] Poster displays correctly
- [ ] All content fields shown
- [ ] Video plays if available
- [ ] Styling matches design

### Step 4: List Previous Campaigns (5 minutes)

**Create list function:**
```javascript
const listCampaigns = async () => {
  const token = localStorage.getItem('token');
  const response = await fetch('/api/v1/campaigns/list', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
};
```

**Test it:**
- [ ] Can retrieve campaign list
- [ ] Shows previously generated campaigns
- [ ] Pagination works (skip/limit)

## Code Review Checklist

### Error Handling
- [ ] Network errors caught and displayed
- [ ] 401 errors trigger re-login
- [ ] 400 errors show validation messages
- [ ] 500 errors show friendly message

### Performance
- [ ] Shows loading indicator during generation
- [ ] Disables button during request
- [ ] Timeout handled (set to 5 min for video)
- [ ] Caches generated content

### User Experience
- [ ] Clear instructions for image upload
- [ ] Progress indication during generation
- [ ] Display campaign immediately after generation
- [ ] Allow retry if generation fails

### Accessibility
- [ ] Alt text on images
- [ ] Video has captions option
- [ ] Keyboard navigation works
- [ ] Color contrast sufficient

## Testing Checklist

### Functional Tests
- [ ] Registration works
- [ ] Login returns valid token
- [ ] Campaign generation with fashion item
- [ ] Campaign generation with different product type
- [ ] Video generation (if enabled)
- [ ] Campaign list shows results
- [ ] Poster displays correctly

### Error Handling Tests
- [ ] Invalid image format rejected
- [ ] Missing product name shows error
- [ ] Expired token handled
- [ ] Network timeout handled
- [ ] Invalid token rejected

### Performance Tests
- [ ] Campaign generation < 45 seconds (no video)
- [ ] Campaign generation < 3 minutes (with video)
- [ ] List loads quickly
- [ ] Poster loads < 2 seconds
- [ ] Video loads progressively

### Security Tests
- [ ] Cannot access endpoints without token
- [ ] Cannot access other users' campaigns
- [ ] Sensitive info not exposed in errors
- [ ] CORS working properly
- [ ] Token expires properly

## Deployment Checklist

### Before Production
- [ ] All environment variables configured
- [ ] Database migrated and tested
- [ ] SSL/HTTPS enabled
- [ ] CORS configured for production domain
- [ ] Error logging configured
- [ ] Monitoring set up
- [ ] Backup procedure documented

### Production Deployment
- [ ] Backend deployed to production
- [ ] Frontend points to production API
- [ ] Domain name configured
- [ ] SSL certificate installed
- [ ] Health check endpoint responds
- [ ] Monitoring alerts configured

### Post-Deployment
- [ ] Run full test suite
- [ ] Verify campaign generation works
- [ ] Check logs for errors
- [ ] Monitor API response times
- [ ] Test with real users

## Documentation for Your Team

### Create These for Your Frontend Team

#### 1. API Integration Guide
```markdown
# How to Use Catalyst AI Backend

## Setup
1. Get authentication token from login endpoint
2. Store token in localStorage
3. Include token in all requests

## Main Endpoint
POST /api/v1/campaigns/generate
- Upload product image
- Enter product name
- Returns campaign with content and images

## Example
[Include your implementation example]
```

#### 2. Component Documentation
Document each component that integrates with API:
- Input parameters
- Required props
- Sample usage
- Error states

#### 3. Error Handling Guide
```markdown
# Error Handling

## 401 Unauthorized
- Token expired or invalid
- Action: Clear storage, redirect to login

## 400 Bad Request
- Invalid image or missing field
- Action: Show validation error to user

## 500 Server Error
- Backend error
- Action: Retry or contact support
```

## Troubleshooting Guide

### "Cannot connect to API"
- Check backend server is running
- Verify URL in frontend config
- Check network/firewall

### "401 Unauthorized"
- Token expired: Get new token via login
- Token missing: Add to localStorage
- Token invalid: Check format in headers

### "Campaign generation failed"
- Check image format (JPEG/PNG/WebP)
- Check image size (< 25MB)
- Check backend logs for details

### "Timeout waiting for video"
- Video generation takes ~2 minutes
- Set timeout to 300+ seconds
- Check FastRouter API status

### "Poster not loading"
- Check URL is complete: `/static/images/poster_*.png`
- Check server is serving static files
- Try different image format

## API Version
- Current Version: **v1**
- Base Path: **/api/v1**
- Last Updated: 2024-02-01

## Support Resources

### Documentation
- [FRONTEND_README.md](./FRONTEND_README.md) - Overview
- [API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md) - All endpoints
- [FRONTEND_API_GUIDE.md](./FRONTEND_API_GUIDE.md) - Full guide
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Deployment

### Testing
- [test_api.py](./test_api.py) - Test script

### Architecture
- [WORKFLOW_DIAGRAM.md](./WORKFLOW_DIAGRAM.md) - System overview

## Sign-Off Checklist

Frontend Integrator: ___________________ Date: __________
- [ ] All documentation read and understood
- [ ] Backend tested and working
- [ ] Integration implemented
- [ ] All tests passing
- [ ] Ready for production

Backend Maintainer: ___________________ Date: __________
- [ ] Backend running stable
- [ ] All API endpoints working
- [ ] Monitoring configured
- [ ] Documentation complete

## Next Steps

1. **Today**: Review documentation, run test script
2. **Tomorrow**: Implement authentication and campaign generation
3. **This Week**: Complete integration and testing
4. **Next Week**: Deploy to production

---

**Expected Timeline**: 1-2 days for full integration  
**Support**: Check documentation first, then contact backend team  
**Questions**: Use GitHub issues with campaign_id for debugging
