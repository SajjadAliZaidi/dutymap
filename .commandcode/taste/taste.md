# Taste

## Code Quality
- Wants unused/dead code removed rather than left in place — flags endpoints, routes, and constants nothing actually consumes and expects them deleted (including their now-orphaned dependencies and docs). Confidence: 0.75

## Style & Presentation
- Likes to add a personal signature to projects (e.g., "Built by" credits, console easter eggs) rather than shipping them generically. Confidence: 0.55
- Extends the personal signature with social/contact links (e.g., LinkedIn) next to the portfolio credit, and wants their icons to "go with the website theme" — monochrome glyphs that inherit the site's existing link colors rather than brand-colored logos or new icon dependencies. Confidence: 0.6
- Keeps identity/branding constants (name, portfolio, social URLs) in a single shared branding module that both frontend and backend import, rather than inlining the strings at each use site. Confidence: 0.45
