# Asymmetrical Collage

A daily blog about freedom, personal sovereignty, financial resilience, and long-term thinking.

**Live site:** [asymmetricalcollage.com](https://www.asymmetricalcollage.com)

## About

Asymmetrical Collage explores ideas at the intersection of risk management, decision-making, and building for resilience. The name reflects the core philosophy: finding asymmetric opportunities where small bets can yield outsized returns.

## Tech Stack

- **Static Site Generator:** [Hugo](https://gohugo.io/)
- **Hosting:** GitHub Pages
- **Automation:** GitHub Actions
- **AI Integration:** Claude API (Anthropic)

## Local Development

### Prerequisites

- [Hugo](https://gohugo.io/installation/) (extended version)
- Git

### Running Locally

```bash
# Clone the repository
git clone https://github.com/elledub-lw/asymmetrical-collage.git
cd asymmetrical-collage

# Start the development server
hugo server

# Site available at http://localhost:1313
```

### Building for Production

```bash
hugo
# Output in /public directory
```

## Creating New Posts

### Using Hugo

```bash
hugo new articles/YYYY-MM-DD-post-title.md
```

### Manual Creation

Create a new file in `content/articles/` with this front matter:

```yaml
---
title: "Your Title Here"
date: YYYY-MM-DD
draft: false
tags: ["tag1", "tag2"]
summary: "A brief one-sentence summary for RSS feeds."
image: ""
---

Your content here.
```

### Writing Guidelines

- 50-300 words per post
- One clear idea per post
- Strong opening hook
- End with question, assertion, directive, or observation (vary the format)
- See `context/writing_styles.md` for detailed style guide

## Project Structure

```
.
├── content/
│   ├── articles/          # Blog posts
│   └── about/             # About page
├── context/               # AI context files for blog generation
│   ├── instructions.md    # Master instructions for AI
│   ├── themes.md          # Topics and angles to explore
│   ├── writing_styles.md  # Three core writing approaches
│   ├── banked_drafts.md   # Drafts saved for future
│   ├── refinements.md     # Learnings and adjustments
│   └── exemplar_posts.md  # Reference posts for inspiration
├── layouts/               # Hugo templates
├── static/                # Static assets (CSS, images)
├── scripts/               # Automation scripts
│   └── generate_blog_ideas.py
├── archetypes/            # Post templates
└── .github/workflows/     # GitHub Actions
    ├── gh-pages.yml       # Auto-deploy on push
    └── daily-blog-ideas.yml
```

## Automated Blog Ideas

The repository includes an automated system that generates daily blog post ideas using Claude API.

### How It Works

1. **Daily trigger:** GitHub Actions runs at 8:00 AM CET
2. **Context gathering:** Script reads recent posts and all context files
3. **AI generation:** Claude generates 3 unique blog post ideas
4. **Email delivery:** Ideas sent via Gmail with formatted HTML

### Setup Requirements

Add these secrets to your GitHub repository (Settings → Secrets → Actions):

| Secret | Description |
|--------|-------------|
| `ANTHROPIC_API_KEY` | Claude API key from console.anthropic.com |
| `GMAIL_ADDRESS` | Your Gmail address |
| `GMAIL_APP_PASSWORD` | Gmail App Password (requires 2FA) |

### Manual Trigger

Go to Actions → "Daily Blog Ideas" → Run workflow

## Context Files

The `context/` folder contains documents that guide AI-assisted content generation:

| File | Purpose |
|------|---------|
| `instructions.md` | Master instructions, voice, tone, process |
| `themes.md` | Topics to explore, tracked coverage |
| `writing_styles.md` | Provocative, Observational, Practical styles |
| `banked_drafts.md` | Strong drafts saved for future refinement |
| `refinements.md` | Post-by-post learnings and adjustments |
| `exemplar_posts.md` | Reference posts that demonstrate good writing |

These files are version-controlled, allowing you to track how your writing system evolves over time.

## Deployment

The site automatically deploys to GitHub Pages when you push to the `main` branch.

### Workflow

1. Push changes to `main`
2. GitHub Actions builds the site with Hugo
3. Built files deployed to `gh-pages` branch
4. Site live within minutes

## RSS Feed

Subscribe to new posts: [asymmetricalcollage.com/articles/index.xml](https://www.asymmetricalcollage.com/articles/index.xml)

The feed includes images via `media:content` tags, with a default banner for posts without dedicated images.

## License

All rights reserved. Content is not licensed for reuse without permission.

---

*Built with Hugo. Powered by ideas.*
