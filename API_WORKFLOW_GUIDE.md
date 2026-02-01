# Catalyst AI: Workflow & API Guide for Frontend

## 1. Execution Flow & Architecture

The workflow is divided into logical phases. The Frontend should Poll the `/api/projects/{id}/jobs` endpoint to track progress.

### Phase 1: Input & Initialization
1.  **User Action**: Upload Image + Product Name/Description.
2.  **API**: `POST /api/projects/`
3.  **Result**: Project created with status `created`.
4.  **Backend**: Triggers `CategoryDetectorAgent`.

### Phase 2: The Brain (Parallel Analysis)
*Once Category is detected, the Orchestrator runs parallel agents.*

1.  **Vision Analysis** (`VISION_ANALYSIS` job):
    - Extracts `visual_style`, `color_psychology`, `lifestyle_context`.
2.  **Competitor Analysis** (`COMPETITOR_ANALYSIS` job):
    - Search web for competitors.
    - Output: `competitors_found`, `differentiation_score`.
3.  **Emotional Mapping** (`EMOTIONAL_ANALYSIS` job):
    - Determines `primary_emotion`, `psychological_triggers`.
4.  **Hook Generation** (`HOOK_GENERATION` job):
    - Uses data from above to create scroll-stopping hooks.

### Phase 3: Creation (The Heavy Lifting)
1.  **Market Research** (`MARKET_RESEARCH` job):
    - Deep search for identifying features.
2.  **Video Generation** (`VIDEO_GENERATION` job):
    - Generates a script based on hooks + market data.
    - Calls Video AI (e.g. Sora).
    - **Polling**: This step takes 2-5 minutes.
    - **Output**: Creates a `video_short` **Asset**.
3.  **Poster Generation** (`POSTER_GENERATION` job):
    - Generates an ad poster (Gemini).
    - Runs in parallel.
    - **Output**: Creates an `image_poster` **Asset**.
4.  **Content Generation** (`CONTENT_GENERATION` job):
    - Writes platform-specific text (LinkedIn, Meta, Twitter).
    - Output: `linkedin_post`, `meta_post` objects.

### Phase 4: Publishing & Feedback
1.  **Performance Prediction** (`PERFORMANCE_PREDICTION` job):
    - Scores the content (0-100).
2.  **Social Media Publishing** (`SOCIAL_MEDIA_PUBLISHING` job):
    - Posts to LinkedIn, Instagram, etc.
    - Output: `results` object with Post IDs.

---

## 2. API Integration Strategy

### Polling Mechanism
Since the workflow is asynchronous, the frontend should poll the Jobs endpoint every 3-5 seconds.

**Endpoint**: `GET /api/projects/{project_id}/jobs`

**Response Handling**:
- The response contains a list of jobs.
- Sort by `created_at desc`.
- Check `status` of each job type (`running`, `completed`, `failed`).

### Displaying Results (Mappings)
| Job Type | What to Display | Data Source (in `output_payload`) |
| :--- | :--- | :--- |
| `VISION_ANALYSIS` | Product Attributes, Color Palette | `visual_style`, `color_psychology` |
| `COMPETITOR_ANALYSIS` | Competitor List, Advice | `competitors_found`, `analysis.strategic_advice` |
| `HOOK_GENERATION` | Best Hook + Alternatives | `best_hook`, `hooks` (array) |
| `VIDEO_GENERATION` | **The Video Player** | Check `/api/projects/{id}/assets` for `video_short` |
| `CONTENT_GENERATION` | Generated Post Text | `linkedin_post.content`, `meta_post.caption` |
| `SOCIAL_MEDIA_PUBLISHING`| Live Links / Status | `linkedin.data.id`, `meta.data.id` |

### Video Assets
For the video specifically, fetch:
`GET /api/projects/{project_id}/assets`
Look for `asset_type: "video_short"`.
Use logic from `FRONTEND_INTEGRATION_GUIDE.md` to display it.
