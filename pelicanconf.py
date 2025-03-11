AUTHOR = 'Ben Cliff'
SITENAME = 'Today I Learned'
SITEURL = 'https://ben-cliff.github.io'  # Remove any trailing dots

PATH = 'content'
TIMEZONE = 'Europe/London'  # Adjust to your timezone

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Markdown settings
DEFAULT_PAGINATION = 10
THEME = "themes/elegant"

# URL settings
ARTICLE_URL = 'posts/{slug}/'
ARTICLE_SAVE_AS = 'posts/{slug}/index.html'
PAGE_URL = 'pages/{slug}/'
PAGE_SAVE_AS = 'pages/{slug}/index.html'

# Site Settings
SITESUBTITLE = 'Daily Learning Journal'  # Optional subtitle
SITE_LICENSE = 'CC-BY-4.0'  # Optional license info

# Display settings
DISPLAY_CATEGORIES_ON_MENU = True

# Optional social links
SOCIAL = (
    ('github', 'https://github.com/Ben-Cliff'),
)

# Elegant theme specific settings
LANDING_PAGE_TITLE = 'Today I Learned'
PROJECTS_TITLE = 'TIL Entries'
DISPLAY_TAGS_ON_SIDEBAR = True

# Optional but recommended for Elegant
SITEDESCRIPTION = 'Daily Learning Journal'
USE_SHORTCUT_ICONS = True
SOCIAL_PROFILE_LABEL = 'Stay in Touch'
RECENT_ARTICLES_COUNT = 10

# Add static paths
STATIC_PATHS = ['images', 'extra']

# Ensure proper path handling
USE_FOLDER_AS_CATEGORY = False
PATH_METADATA = '(?P<path_no_ext>[^.]+)'

# Server settings
PORT = 8080
BIND = '127.0.0.1'
