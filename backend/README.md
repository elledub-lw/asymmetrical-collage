# Blog Automation Backend

FastAPI backend for reviewing and publishing AI-generated blog drafts. Replaces email-based delivery with a self-hosted web UI.

## Features

- Receives draft batches from GitHub Actions
- Web UI for reviewing, editing, and publishing drafts
- Direct publishing to GitHub via Contents API
- Prompt version management with analytics
- Dark mode, mobile-friendly interface

## Quick Start

### Local Development

1. Create a virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. Create a `.env` file:
   ```bash
   API_KEY=your-32-char-api-key
   GITHUB_TOKEN=ghp_xxx
   GITHUB_REPO=owner/repo
   DATABASE_URL=./data/blog.db
   ```

3. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

4. Open http://localhost:8000 in your browser

### Docker Deployment (Synology NAS)

1. Copy the `backend` folder to your NAS

2. Create a `.env` file with your secrets:
   ```bash
   API_KEY=your-32-char-api-key
   GITHUB_TOKEN=ghp_xxx
   GITHUB_REPO=owner/repo
   ```

3. Build and run:
   ```bash
   docker-compose up -d
   ```

4. Access at http://your-nas-ip:8080

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/drafts/batch` | POST | Receive drafts from GitHub Actions (requires API key) |
| `/api/drafts/pending` | GET | List pending drafts by batch |
| `/api/drafts/{id}` | GET/PUT | View/edit a draft |
| `/api/drafts/{id}/publish` | POST | Publish to GitHub |
| `/api/drafts/{id}/reject` | POST | Mark as rejected |
| `/api/prompts` | GET/POST | List/create prompt versions |
| `/api/prompts/active` | GET | Get active prompt |
| `/api/prompts/{version}/activate` | POST | Set active version |
| `/api/analytics` | GET | Metrics by prompt version |
| `/health` | GET | Health check |

## Web UI Pages

- **/** - Dashboard with pending drafts
- **/review/{id}** - Edit and publish a draft
- **/prompts** - Manage prompt versions
- **/analytics** - View performance metrics
- **/published** - Archive of published posts

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `API_KEY` | Yes | API key for GitHub Actions authentication |
| `GITHUB_TOKEN` | Yes | GitHub PAT with `contents:write` scope |
| `GITHUB_REPO` | Yes | Target repo in `owner/repo` format |
| `DATABASE_URL` | No | SQLite path (default: `/data/blog.db`) |
| `GMAIL_ADDRESS` | No | Email fallback sender |
| `GMAIL_APP_PASSWORD` | No | Email fallback password |

## GitHub Actions Setup

Add these secrets to your repository:

| Secret | Description |
|--------|-------------|
| `SYNOLOGY_URL` | Backend URL (e.g., `http://your-nas:8080`) |
| `SYNOLOGY_API_KEY` | Same as `API_KEY` in Docker |

The updated `generate_blog_ideas.py` script will:
1. Try to POST drafts to Synology first
2. Fall back to email if Synology fails or is not configured

## Database

SQLite database with three tables:
- `drafts` - Generated drafts with status tracking
- `prompt_versions` - Prompt version history
- `published_posts` - Archive of published content

Schema is auto-created on first run.

## Publishing Flow

1. Draft arrives from GitHub Actions
2. Review in web UI, edit if needed
3. Click "Publish" to:
   - Generate slug from title
   - Build Hugo front matter
   - Commit to `content/articles/YYYY-MM-DD-{slug}.md`
4. Draft marked as published with GitHub commit SHA

## Security

- API key required for `/api/drafts/batch` endpoint
- Internal network recommended for NAS deployment
- For external access, use HTTPS via reverse proxy
