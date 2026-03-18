# Job Pilot – Naukri.com Automation

## Overview

Automate login, multi-page job search, AI-keyword filtering, and optional auto-apply on [Naukri.com](https://www.naukri.com/) using **Playwright + Firefox**, structured as a **modular monolith**.

## Architecture

```
Jop-Pilot/
├── config/          # YAML config loader + AppConfig dataclass
├── browser/         # Playwright Firefox browser factory
├── auth/            # Naukri login automation
├── search/          # URL-based job search + sort by date
├── config.yaml      # Credentials & search params
├── main.py          # CLI orchestrator
└── requirements.txt # playwright, pyyaml
```

## Features

- Login automation (email + password)
- Direct URL search from YAML config
- Multi-keyword search with comma-safe URL building
- Optional sort by Date
- Collect and print all listings (in-memory only)
- Filter jobs by user-defined terms (in-memory only)
- Optional auto-apply with status detection
- Pagination: auto-advance through pages using Next

## Flow

1. **Login** → Navigate to Naukri → open login drawer → fill email & password → submit → wait for redirect to `/mnjuser/homepage`
2. **Search** → Build direct URL from config → navigate to results page
3. **Sort (optional)** → Click sort dropdown (`button#filter-sort`) → select "Date" (`li[title="Date"]`)
4. **Collect listings** → Capture all jobs on each page
5. **Filter jobs** → Match on terms in title, tags, and description
6. **Auto-apply (optional)** → Open each filtered job and attempt apply
7. **Paginate** → Move to Next page and repeat until no Next link

## Key DOM Selectors

### Login

| Element        | Selector |
|----------------|----------|
| Login link     | `a#login_Layer` |
| Email input    | `input[placeholder="Enter your active Email ID / Username"]` |
| Password input | `input[type="password"][placeholder="Enter your password"]` |
| Login button   | `button.btn-primary.loginButton` |

### Search URL Patterns

With location:

```
https://www.naukri.com/{keyword-slug}-jobs-in-{location}?k={keyword}&l={location}&experience={N}&jobAge={days}
```

Without location:

```
https://www.naukri.com/{keyword-slug}-jobs?k={keyword}&experience={N}&jobAge={days}
```

### Sort by Date

| Element        | Selector |
|----------------|----------|
| Sort dropdown  | `button#filter-sort` |
| Date option    | `li[title="Date"]` |

### Apply Flow

| Case | Detected By | Result |
|------|-------------|--------|
| Apply button | `button#apply-button` | Attempts apply |
| Walk-in | `button#walkin-button` | Status: WalkIn |
| Company site | `button#company-site-button` | Status: CompanySite |
| Chatbot | `div._chatBotContainer` or `div[id$='ChatbotContainer']` | Status: Chatbot |
| Applied success | `.acp-header-container` or `.applied-job-content` | Status: Applied |
| Already applied | `span.apply-message` contains "does not require you to apply again" | Status: AlreadyApplied |
| Apply failed | `.apply-status-header.red` | Status: ApplyFailed |

## Usage

```bash
# 1. Edit config.yaml with credentials & search params
# 2. Run:
python main.py
```

## Config Reference

```yaml
auth:
	email: "you@example.com"
	password: "your_password"

search:
	keywords:
		- "langchain, agentcore, langgraph"
	filter_terms:
		- "ai, llm, rag, agent, chatbot"
	experience: "2"           # optional
	location: "Bangalore"     # optional
	job_age: "1"              # optional
	sort_by_date: false        # optional
	auto_apply: false          # optional

browser:
	headless: false
	implicit_wait: 10
```