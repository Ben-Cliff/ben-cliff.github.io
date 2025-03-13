# [ben-cliff.github.io](https://ben-cliff.github.io) 🕊️ 🤲 

## Today I Learned

A personal knowledge base from a Data Engineer working in Berlin's startup ecosystem. This site is built with [Pelican](https://getpelican.com/) using the [Elegant](https://elegant.oncrashreboot.com/) theme.

## Purpose

As a Data Engineer working with startups in Berlin, I encounter new challenges, tools, and insights daily. This blog serves as my digital garden of knowledge snippets, technical discoveries, and data engineering learnings. By documenting these experiences, I create a searchable archive that helps reinforce my learning and might help other data professionals facing similar challenges.

Topics typically include:
- Data Engineering best practices
- Data Infrastructure and Architecture
- ETL/ELT Pipelines
- Cloud Technologies
- Startup Tech Stack Decisions
- Performance Optimization
- Data Modeling

## Directory Structure
```
today-i-learned.github.io/
├── content/                  # All content lives here
│   ├── articles/            # Blog posts/TIL entries
│   └── pages/              # Static pages (About, Contact)
├── output/                  # Generated site (not in git)
├── themes/                  # Theme submodules
│   └── elegant/            # Elegant theme
├── pelicanconf.py          # Pelican configuration
└── README.md               # This file
```

## Setup

1. Create a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
python -m pip install "pelican[markdown]"
```

3. Clone the Elegant theme:
```bash
git submodule add https://github.com/Pelican-Elegant/elegant.git themes/elegant
```

## Local Development

1. Generate the site:
```bash
python -m pelican content
```

2. Start the development server:
```bash
python -m pelican --listen
```

3. View the site at `http://localhost:8000`

## Writing New Articles

Create a new markdown file in `content/articles/` with the following format:

```markdown
Title: Your Title Here
Date: YYYY-MM-DD
Category: Topic
Tags: tag1, tag2
Slug: unique-url-name

Your content here...
```

## Configuration

The site configuration is managed in `pelicanconf.py`. Key settings include:

```python
AUTHOR = 'Your Name'
SITENAME = 'Today I Learned'
SITESUBTITLE = 'Daily Learning Journal'
THEME = "themes/elegant"
```

## Deployment

The site is automatically deployed to GitHub Pages when changes are pushed to the main branch.

## License

Content is licensed under CC-BY-4.0 unless otherwise specified.
