# Job Pilot – Naukri.com Automation

## Overview

Automate login and job search on [Naukri.com](https://www.naukri.com/) using **Playwright + Firefox**, structured as a **modular monolith**.

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

## Flow

1. **Login** → Navigate to Naukri → open login drawer → fill email & password → submit → wait for redirect to `/mnjuser/homepage`
2. **Search** → Build direct URL from config (keyword, location, experience, jobAge) → navigate to results page
3. **Sort** → Click sort dropdown (`button#filter-sort`) → select "Date" (`li[title="Date"]`)

## Key DOM Selectors

### Login

| Element        | Selector |
|----------------|----------|
| Login link     | `a#login_Layer` |
| Email input    | `input[placeholder="Enter your active Email ID / Username"]` |
| Password input | `input[type="password"][placeholder="Enter your password"]` |
| Login button   | `button.btn-primary.loginButton` |

### Search URL Pattern

```
https://www.naukri.com/{keyword-slug}-jobs-in-{location}?k={keyword}&l={location}&experience={N}&jobAge={days}
```

### Sort by Date

| Element        | Selector |
|----------------|----------|
| Sort dropdown  | `button#filter-sort` |
| Date option    | `li[title="Date"]` |

## Usage

```bash
# 1. Edit config.yaml with credentials & search params
# 2. Run:
python main.py
```