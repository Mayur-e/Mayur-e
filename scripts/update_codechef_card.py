
import re
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont

# ==========================================
# CONFIG
# ==========================================

USERNAME = "mayurmandalik"

WIDTH  = 700
HEIGHT = 280

BG     = "#0D1117"
CARD   = "#161B22"
BORDER = "#30363D"

TEXT    = "#E6EDF3"
SUBTEXT = "#8B949E"

ACCENT  = "#A97B50"

PADDING = 28          # left / right outer margin inside card
DIVIDER = 215         # x where the right panel begins
RIGHT_EDGE = 672      # rightmost x for text / bar (WIDTH - PADDING)

# ==========================================
# FETCH CODECHEF DATA
# ==========================================

url  = f"https://www.codechef.com/users/{USERNAME}"
html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text
soup = BeautifulSoup(html, "html.parser")

rating = soup.find("div", class_="rating-number").get_text(strip=True)
stars  = soup.find("div", class_="rating-star").get_text(strip=True)

ranks        = soup.select(".rating-ranks strong")
global_rank  = ranks[0].get_text(strip=True)
country_rank = ranks[1].get_text(strip=True)

# ==========================================
# HIGHEST RATING
# ==========================================

highest_rating = rating

try:
    page_text = soup.get_text(" ", strip=True)
    match = re.search(r"Highest Rating\s+(\d+)", page_text)
    if match:
        highest_rating = match.group(1)
except Exception:
    pass

# ==========================================
# STAR DISPLAY
# ==========================================

star_count = stars.count("★")
if star_count == 0:
    star_count = 1

stars_display = "★" * star_count + "☆" * (4 - star_count)

# ==========================================
# CREATE IMAGE
# ==========================================

img  = Image.new("RGB", (WIDTH, HEIGHT), BG)
draw = ImageDraw.Draw(img)

# ==========================================
# CARD BACKGROUND
# ==========================================

draw.rounded_rectangle(
    [(10, 10), (690, 270)],
    radius=20,
    fill=CARD,
    outline=BORDER,
    width=2
)

# Accent strip at top
draw.rounded_rectangle(
    [(10, 10), (690, 20)],
    radius=20,
    fill=ACCENT
)

# ==========================================
# FONTS
# ==========================================

title_font    = ImageFont.truetype("assets/fonts/Inter_28pt-Bold.ttf",    22)
username_font = ImageFont.truetype("assets/fonts/Inter_28pt-Regular.ttf", 22)
rating_font   = ImageFont.truetype("assets/fonts/Inter_28pt-Bold.ttf",    42)
stat_font     = ImageFont.truetype("assets/fonts/Inter_28pt-Regular.ttf", 18)
footer_font   = ImageFont.truetype("assets/fonts/Inter_28pt-Regular.ttf", 14)

# ==========================================
# HELPERS
# ==========================================

def text_size(draw_obj, text, font):
    """Return (width, height) of rendered text."""
    bb = draw_obj.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0], bb[3] - bb[1]


def draw_right_aligned(draw_obj, text, right_x, y, font, fill):
    """Draw text so its right edge sits at right_x."""
    tw, _ = text_size(draw_obj, text, font)
    draw_obj.text((right_x - tw, y), text, fill=fill, font=font)

# ==========================================
# HEADER ROW
# ==========================================

HEADER_Y = 35      # top of header text

# Orange dot + "CODECHEF"
dot_r = 7
dot_cx = PADDING + dot_r          # centre-x of dot
dot_cy = HEADER_Y + 11            # vertically centres on text

draw.ellipse(
    (dot_cx - dot_r, dot_cy - dot_r, dot_cx + dot_r, dot_cy + dot_r),
    fill=ACCENT
)

draw.text(
    (dot_cx + dot_r + 8, HEADER_Y),
    "CODECHEF",
    fill=ACCENT,
    font=title_font
)

# Username — left-aligned at divider + 20
draw.text((DIVIDER + 20, HEADER_Y + 4), USERNAME, fill=TEXT, font=username_font)

# Global rank — right-aligned to RIGHT_EDGE
draw_right_aligned(draw, f"#{global_rank}", RIGHT_EDGE, HEADER_Y + 4, username_font, TEXT)

# ==========================================
# RATING CIRCLE  (left panel)
# ==========================================

CIRCLE_L = PADDING + 12
CIRCLE_T = 68
CIRCLE_R = CIRCLE_L + 160
CIRCLE_B = CIRCLE_T + 160
CX = (CIRCLE_L + CIRCLE_R) // 2
CY = (CIRCLE_T + CIRCLE_B) // 2

draw.ellipse(
    (CIRCLE_L, CIRCLE_T, CIRCLE_R, CIRCLE_B),
    outline=ACCENT,
    width=6
)

# "Current Rating" label — horizontally centred inside circle
label_text = "Current Rating"
lw, lh = text_size(draw, label_text, footer_font)
draw.text(
    (CX - lw // 2, CIRCLE_T + 14),
    label_text,
    fill=SUBTEXT,
    font=footer_font
)

# Rating number — centred in circle
rw, rh = text_size(draw, rating, rating_font)
draw.text(
    (CX - rw // 2, CY - rh // 2 + 8),
    rating,
    fill=TEXT,
    font=rating_font
)

# ==========================================
# STATS  (right panel)
# ==========================================

stats = [
    ("Stars",          stars_display),
    ("Highest Rating", highest_rating),
    ("Country Rank",   country_rank),
]

STATS_START_Y = 85
ROW_GAP       = 55
SEP_OFFSET    = 38    # separator y below row start

for i, (label, value) in enumerate(stats):
    y = STATS_START_Y + i * ROW_GAP

    # Label — left-aligned at DIVIDER + 20
    draw.text((DIVIDER + 20, y), label, fill=SUBTEXT, font=stat_font)

    # Value — right-aligned at RIGHT_EDGE
    draw_right_aligned(draw, str(value), RIGHT_EDGE, y, stat_font, TEXT)

    # Separator line
    draw.line(
        (DIVIDER + 20, y + SEP_OFFSET, RIGHT_EDGE, y + SEP_OFFSET),
        fill="#30363D",
        width=1
    )

# ==========================================
# RATING PROGRESS BAR  (right panel, bottom)
# ==========================================

try:
    current = int(rating)
    highest = int(highest_rating)
    progress = min(current / highest, 1.0)

    BAR_LEFT   = DIVIDER + 20
    BAR_RIGHT  = RIGHT_EDGE
    BAR_WIDTH  = BAR_RIGHT - BAR_LEFT
    BAR_Y      = 247
    BAR_HEIGHT = 10

    # Track
    draw.rounded_rectangle(
        (BAR_LEFT, BAR_Y, BAR_RIGHT, BAR_Y + BAR_HEIGHT),
        radius=5,
        fill="#30363D"
    )

    # Fill
    fill_end = BAR_LEFT + max(int(BAR_WIDTH * progress), 10)
    draw.rounded_rectangle(
        (BAR_LEFT, BAR_Y, fill_end, BAR_Y + BAR_HEIGHT),
        radius=5,
        fill=ACCENT
    )

    # "current/highest" label — right-aligned, just above the bar
    prog_label = f"{rating}/{highest_rating}"
    draw_right_aligned(draw, prog_label, RIGHT_EDGE, BAR_Y - 17, footer_font, SUBTEXT)

except Exception:
    pass

# ==========================================
# FOOTER  (left panel)
# ==========================================

_, fh = text_size(draw, "Updated Daily", footer_font)
draw.text(
    (PADDING, HEIGHT - PADDING - fh),
    "Updated Daily",
    fill=SUBTEXT,
    font=footer_font
)

# ==========================================
# SAVE
# ==========================================

img.save("assets/codechef-card.png", quality=100)

print("[OK] CodeChef card updated successfully")