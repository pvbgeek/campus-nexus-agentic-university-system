from pathlib import Path
import math
import shutil
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "Architecture/architecture.png"
W, H = 3000, 2280

image = Image.new("RGB", (W, H), "#F7FAFC")
draw = ImageDraw.Draw(image)

def font(size, bold=False):
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size)
    raise RuntimeError("A scalable Arial or DejaVu Sans font is required.")

TITLE = font(64, True)
SUBTITLE = font(40)
HEADING = font(34, True)
BODY = font(26)
SMALL = font(25)
NAVY = "#102A43"
MUTED = "#52677C"
LINE = "#60758A"

def wrap(text, width, face):
    result = []
    for paragraph in text.splitlines():
        line = ""
        for word in paragraph.split():
            candidate = (line + " " + word).strip()
            if line and draw.textlength(candidate, font=face) > width:
                result.append(line)
                line = word
            else:
                line = candidate
        result.append(line)
    return result

def box(bounds, heading, body, fill="#FFFFFF", border="#91A8BD"):
    x1, y1, x2, y2 = bounds
    lines = wrap(body, x2 - x1 - 48, BODY)
    required = 24 + 40 + 12 + len(lines) * 34 + 20
    if required > y2 - y1:
        raise RuntimeError(f"Text does not fit in diagram box: {heading}")
    if draw.textlength(heading, font=HEADING) > x2 - x1 - 48:
        raise RuntimeError(f"Heading does not fit: {heading}")
    draw.rounded_rectangle(bounds, radius=20, fill=fill, outline=border, width=4)
    draw.text((x1 + 24, y1 + 22), heading, font=HEADING, fill=NAVY)
    y = y1 + 76
    for line in lines:
        draw.text((x1 + 24, y), line, font=BODY, fill=NAVY)
        y += 34

def arrow(a, b, both=False):
    draw.line([a, b], fill=LINE, width=5)
    angle = math.atan2(b[1] - a[1], b[0] - a[0])
    def tip(point, direction):
        size = 18
        triangle = [
            point,
            (point[0] - size * math.cos(direction - 0.45),
             point[1] - size * math.sin(direction - 0.45)),
            (point[0] - size * math.cos(direction + 0.45),
             point[1] - size * math.sin(direction + 0.45)),
        ]
        draw.polygon(triangle, fill=LINE)
    tip(b, angle)
    if both:
        tip(a, angle + math.pi)

def centered(y, text, face=SMALL):
    x = (W - draw.textlength(text, font=face)) / 2
    left, top, right, bottom = draw.textbbox((x, y), text, font=face)
    draw.rectangle((left - 12, top - 5, right + 12, bottom + 5), fill="#F7FAFC")
    draw.text((x, y), text, font=face, fill=MUTED)

draw.text((60, 45), "Campus Nexus", font=TITLE, fill=NAVY)
draw.text((60, 125), "Enterprise Customer Support Agent", font=SUBTITLE, fill=NAVY)
draw.text(
    (60, 190),
    "PROPOSED TARGET DESIGN | Current implementation: simulated course starter",
    font=SMALL, fill=MUTED,
)

# Browser, orchestration, and scoped memory.
arrow((805, 350), (1043, 350), both=True)
arrow((1957, 350), (2193, 350), both=True)

box((60, 240, 800, 465), "Browser UI",
    "Customer cases\nAdmin policy upload\nSupervisor interface", "#EAF4FD")
box((1050, 240, 1950, 465), "Orchestrator",
    "LLM planning and routing\nResponse aggregation\nScoped task state", "#E7F4F4", "#25828A")
box((2200, 240, 2940, 465), "Scoped memory",
    "Session and persistent notes\nCase-bound permissions\nNo executable authority", "#EEEAFB")

# Bidirectional coordination between orchestrator and five agents.
centers = [300, 900, 1500, 2100, 2700]
draw.text((60, 500), "Task assignment, scoped context, and agent responses", font=SMALL, fill=MUTED)
arrow((1500, 472), (1500, 550), both=True)
draw.line([(300, 550), (2700, 550)], fill=LINE, width=5)
for x in centers:
    arrow((x, 550), (x, 643), both=True)

agents = [
    ("Intake Agent", "Create support cases\nAssign case processing\nTrack case identity"),
    ("Email Agent", "Receive and draft\nAuthorized sends\nAcknowledgements"),
    ("Records Agent", "Assigned case/profile access\nPolicy retrieval\nControlled updates"),
    ("Refunds Agent", "Evaluate eligibility\nPropose decisions\nRequest refund processing"),
    ("Reporting Agent", "Approved / denied / pending\nDecision reasons\nScoped outcome reports"),
]
for x, (heading, body) in zip(centers, agents):
    box((x - 240, 650, x + 240, 860), heading, body, "#FFFFFF", "#4A86B8")

# All tool access crosses an independent execution boundary.
for x in centers:
    arrow((x, 867), (x, 950), both=True)
draw.line([(300, 950), (2700, 950)], fill=LINE, width=5)
arrow((1500, 950), (1500, 1053), both=True)
centered(990, "Tool requests and results: agent identity + assigned case + explicit scope")

box(
    (650, 1060, 2360, 1340),
    "Independent execution gateway",
    "Identity + assigned case + tool permissions\n"
    "$100 per autonomous refund | $500 cumulative per week\n"
    "Supervisor decisions | revocation | duplicate-processing protection\n"
    "Atomic limit checks and ledger updates",
    "#E8F7EF", "#318260",
)

arrow((547, 1200), (643, 1200), both=True)
box(
    (60, 1080, 540, 1340), "Supervisor",
    "Exceptions and decisions\nAuthority revocation\nNo policy-limit bypass",
    "#FFF3D6", "#B48B32",
)

arrow((2367, 1200), (2453, 1200))
box(
    (2460, 1080, 2940, 1340), "Audit evidence",
    "Attempt / authorize / execute\nDecision IDs + policy versions\nAppend-only audit evidence",
    "#EEEAFB", "#8671AC",
)

# Authorized mock tools and data services.
arrow((1500, 1347), (1500, 1450), both=True)
draw.line([(300, 1450), (2700, 1450)], fill=LINE, width=5)
centered(1500, "Authorized mock tool and data access")
for x in centers:
    arrow((x, 1450), (x, 1593), both=True)

services = [
    ("Case tools", "Synthetic requests\nCase creation and assignment\nCase status"),
    ("Mock email", "Receive / draft / send\nAcknowledgements\nDecision notifications"),
    ("Records and RAG", "Records DB + vector retrieval\nVersioned refund policies\nAssigned cases and profiles\nSynthetic account details"),
    ("Refund accounts", "Synthetic balances\nShared weekly ledger\nIdempotent updates"),
    ("Reporting tools", "Approved / denied / pending\nDecision reasons\nScoped summaries"),
]
for x, (heading, body) in zip(centers, services):
    box((x - 240, 1600, x + 240, 1870), heading, body, "#EAF4FD")

box(
    (60, 1970, 2940, 2150), "Authority boundary",
    "Customer input, retrieved text, and model output cannot grant permissions.\n"
    "Revocation and supervisor decisions are checked before consequential execution.",
    "#FFFFFF", "#91A8BD",
)
centered(2190, "All records, emails, and balances are synthetic. This diagram describes the planned target application.")

OUT.parent.mkdir(parents=True, exist_ok=True)
image.save(OUT, "PNG", optimize=True)

# Preserve the previous diagram after generating the replacement successfully.
old = ROOT / "Architecture/diagram.png"
archived = ROOT / "docs/archive/original-architecture.png"
if old.exists() and not archived.exists():
    archived.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(old), str(archived))

print("Generated:", OUT)
print("Dimensions:", image.size)
