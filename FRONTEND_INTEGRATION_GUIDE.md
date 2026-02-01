# Frontend Integration Guide: Video Assets

## 1. Overview
The Catalyst AI backend generates video assets during the workflow (Step 3.5). These videos are stored locally on the server in the `static/videos/` directory and are served via the `/static` endpoint.

## 2. Accessing Video Files

### Base URL
Assuming the backend is running at `http://localhost:8000`:
- **Static File Base**: `http://localhost:8000/static/`

### Asset Structure
When you fetch project assets (e.g., via `/api/projects/{id}/assets`), you will receive an object like this:

```json
{
  "id": "uuid...",
  "asset_type": "video_short",
  "file_url": "D:\\path\\to\\backend\\static\\videos\\video_12345.mp4",
  "content": "{ \"cloud_url\": \"https://sora-api...\" }"
}
```

### 3. displaying the Video

#### Option A: Self-Hosted (Recommended)
Since the `file_url` is an absolute server path, you need to convert it to a web URL.
**Logic:** Extract everything after `static\` and append to your API Base URL.

**Example (JS/TS):**
```typescript
const getWebUrl = (localPath: string) => {
  // Split by 'static' and get the generic part
  // Handle both Windows (\) and Unix (/) paths
  const relativePath = localPath.split(/static[\\/]/).pop();
  return `http://localhost:8000/static/${relativePath}`;
};

// Result: http://localhost:8000/static/videos/video_12345.mp4
```

**React Component Example:**
```jsx
export const VideoPlayer = ({ asset }) => {
  // 1. Construct Local URL (Primary - Persistent)
  let videoSrc = "";
  if (asset.file_url) {
      const filename = asset.file_url.split(/static[\\/]/).pop();
      // Ensure backend URL is correct
      videoSrc = `http://localhost:8000/static/videos/${filename}`;
  }

  // 2. Fallback to Cloud URL (Secondary - Temporary/Expired)
  if (!videoSrc) {
      try {
          const content = JSON.parse(asset.content);
          if (content.cloud_url) videoSrc = content.cloud_url;
      } catch (e) {}
  }

  return (
    <div className="video-container">
      <h3>{asset.asset_type}</h3>
      <video controls width="100%" className="rounded-lg shadow-lg">
        <source src={videoSrc} type="video/mp4" />
        <p>Your browser does not support the video tag. Try: <a href={videoSrc}>{videoSrc}</a></p>
      </video>
    </div>
  );
};
```

#### Option B: Cloud URL (Temporary)
If the `content` field contains `cloud_url`, you can use that directly. Note that some provider URLs expire after a few hours, so the Self-Hosted logic (Option A) is more reliable for long-term display.

## 4. Testing
You can verify the video is accessible by opening the constructed URL in your browser directly:
`http://localhost:8000/static/videos/<filename>.mp4`

## 5. API Endpoints
- **List Assets**: `GET /api/projects/{project_id}/assets`
- **Get Specific Asset**: `GET /api/assets/{asset_id}`
