from dotenv import load_dotenv
import os
import requests
import streamlit as st
import streamlit.components.v1 as components
import time

load_dotenv()

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="City Assistant",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Global CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Syne:wght@400;600;700;800&display=swap');

:root {
  --bg: #060a12;
  --surface: #0d1321;
  --surface2: #111827;
  --border: #1e2d45;
  --accent: #00d4ff;
  --accent2: #0066ff;
  --accent3: #7c3aed;
  --text: #e2eaf6;
  --text-muted: #4a6080;
  --green: #00ff88;
  --orange: #ff6b35;
}

html, body, [data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  font-family: 'Syne', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(ellipse 80% 50% at 50% -20%, rgba(0,102,255,0.15) 0%, transparent 70%),
    radial-gradient(ellipse 60% 40% at 80% 80%, rgba(124,58,237,0.08) 0%, transparent 60%),
    var(--bg) !important;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { display: none; }

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* Typography */
h1, h2, h3, h4 {
  font-family: 'Syne', sans-serif !important;
  color: var(--text) !important;
}

/* Input */
[data-testid="stTextInput"] input {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  color: var(--text) !important;
  font-family: 'Space Mono', monospace !important;
  font-size: 14px !important;
  padding: 12px 16px !important;
}
[data-testid="stTextInput"] input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 2px rgba(0,212,255,0.15) !important;
}
[data-testid="stTextInput"] label {
  color: var(--text-muted) !important;
  font-family: 'Space Mono', monospace !important;
  font-size: 11px !important;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

/* Buttons */
[data-testid="baseButton-secondary"],
.stButton > button {
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
  font-family: 'Space Mono', monospace !important;
  font-size: 12px !important;
  border-radius: 6px !important;
  transition: all 0.2s !important;
}
.stButton > button:hover {
  border-color: var(--accent) !important;
  color: var(--accent) !important;
  box-shadow: 0 0 12px rgba(0,212,255,0.2) !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
  background: transparent !important;
  border: none !important;
}

/* Spinner */
[data-testid="stSpinner"] { color: var(--accent) !important; }

/* Selectbox */
[data-testid="stSelectbox"] select,
[data-testid="stSelectbox"] > div > div {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
  font-family: 'Space Mono', monospace !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent2); }
</style>
""", unsafe_allow_html=True)


# ─── City Coordinates ────────────────────────────────────────────────────────
CITY_COORDS = {
    "mumbai": (19.076, 72.8777),
    "delhi": (28.6139, 77.2090),
    "bangalore": (12.9716, 77.5946),
    "chennai": (13.0827, 80.2707),
    "kolkata": (22.5726, 88.3639),
    "hyderabad": (17.3850, 78.4867),
    "pune": (18.5204, 73.8567),
    "ahmedabad": (23.0225, 72.5714),
    "new york": (40.7128, -74.0060),
    "london": (51.5074, -0.1278),
    "paris": (48.8566, 2.3522),
    "tokyo": (35.6762, 139.6503),
    "sydney": (-33.8688, 151.2093),
    "dubai": (25.2048, 55.2708),
    "singapore": (1.3521, 103.8198),
    "beijing": (39.9042, 116.4074),
    "shanghai": (31.2304, 121.4737),
    "moscow": (55.7558, 37.6173),
    "berlin": (52.5200, 13.4050),
    "toronto": (43.6532, -79.3832),
    "los angeles": (34.0522, -118.2437),
    "chicago": (41.8781, -87.6298),
    "miami": (25.7617, -80.1918),
    "cairo": (30.0444, 31.2357),
    "nairobi": (-1.2921, 36.8219),
    "jakarta": (-6.2088, 106.8456),
    "istanbul": (41.0082, 28.9784),
    "mexico city": (19.4326, -99.1332),
    "buenos aires": (-34.6037, -58.3816),
    "bangkok": (13.7563, 100.5018),
}

def get_city_coords(city_name: str):
    name = city_name.lower().strip()
    for key, coords in CITY_COORDS.items():
        if key in name or name in key:
            return coords
    return None


# ─── Globe Animation Component ──────────────────────────────────────────────
def render_globe(city_name: str = None, lat: float = 20.0, lon: float = 78.0, animate: bool = False):
    city_label = city_name.upper() if city_name else ""
    do_animate = "true" if animate else "false"

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background: transparent; overflow: hidden; }}
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@700;800&display=swap');

  #globe-container {{
    display: flex;
    flex-direction: column;
    align-items: center;
    background: transparent;
    padding: 10px 0 4px;
  }}
  .globe-title {{
    font-family: 'Syne', sans-serif;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.25em;
    color: #4a6080;
    text-transform: uppercase;
    margin-bottom: 8px;
  }}
  #globe-canvas {{
    display: block;
    filter: drop-shadow(0 0 20px rgba(0,102,255,0.6)) drop-shadow(0 0 50px rgba(0,212,255,0.2));
  }}
  .city-label {{
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    color: #00d4ff;
    letter-spacing: 0.12em;
    margin-top: 8px;
    text-align: center;
    text-shadow: 0 0 14px rgba(0,212,255,0.9), 0 0 30px rgba(0,212,255,0.4);
    min-height: 16px;
    transition: opacity 0.4s;
  }}
</style>
</head>
<body>
<div id="globe-container">
  <div class="globe-title">◈ CITY INTELLIGENCE</div>
  <canvas id="globe-canvas" width="220" height="220"></canvas>
  <div class="city-label" id="city-label">{city_label}</div>
</div>

<script>
const canvas = document.getElementById('globe-canvas');
const ctx = canvas.getContext('2d');
const W = canvas.width, H = canvas.height;
const cx = W/2, cy = H/2;
const R = 96; // globe radius

// Target city
const TARGET_LAT = {lat};
const TARGET_LON = {lon};
const HAS_CITY = {'true' if city_name else 'false'};
const DO_ANIMATE = {do_animate};

// The globe's current rotation offset (longitude shown at center)
// We store it as the lon offset — i.e., what longitude is at the front face
let currentLonOffset = 0;  // degrees — what lon is currently centered
let targetLonOffset = 0;

// For idle slow rotation
let idleRotSpeed = 0.15; // deg/frame
let animating = false;
let animStartTime = null;
let animDuration = 2200; // ms
let animFromLon = 0;
let animToLon = 0;

// Lat tilt (fixed, we just rotate around Y axis)
const TILT = 0; // we'll handle lat via pin position

// Continent data — simplified polygons as [lon, lat] arrays
// These are rough approximations good enough for a stylized globe
const continents = [
  // North America
  [[-168,72],[-140,72],[-120,60],[-80,48],[-60,48],[-80,26],[-88,16],[-78,8],[-76,8],[-80,26],[-110,22],[-120,30],[-120,44],[-140,58],[-158,60],[-168,60],[-168,72]],
  // South America  
  [[-80,12],[-60,12],[-34,-6],[-34,-20],[-50,-34],[-70,-56],[-74,-42],[-70,-34],[-68,-22],[-68,-8],[-80,12]],
  // Europe
  [[-10,36],[30,36],[30,48],[20,56],[10,58],[0,52],[-10,44],[-10,36]],
  // Africa
  [[-18,16],[52,16],[52,-26],[18,-34],[-18,-26],[-18,16]],
  // Asia (rough)
  [[26,36],[140,36],[140,72],[100,72],[60,72],[26,68],[26,36]],
  // India sub-peninsula
  [[68,36],[90,26],[80,8],[72,8],[66,22],[68,36]],
  // Australia
  [[114,-22],[154,-22],[154,-38],[130,-46],[114,-34],[114,-22]],
  // Greenland
  [[-58,76],[-18,76],[-18,60],[-44,58],[-58,68],[-58,76]],
  // Japan
  [[130,30],[146,30],[146,44],[130,44],[130,30]],
];

function latLonToXY(lat, lon, lonOffset) {{
  // Convert lat/lon to canvas x,y given current globe rotation
  // lonOffset = what longitude is at the center (facing viewer)
  const relLon = lon - lonOffset;  // relative to center
  const phi = relLon * Math.PI / 180;
  const theta = lat * Math.PI / 180;
  
  // Orthographic projection
  const x3 = Math.cos(theta) * Math.sin(phi);
  const y3 = Math.sin(theta);
  const z3 = Math.cos(theta) * Math.cos(phi);
  
  // Only render if facing viewer (z > 0 means facing away in this convention — we flip)
  const facing = (Math.cos(theta) * Math.cos(phi)) > -0.05;
  
  return {{
    x: cx + R * x3,
    y: cy - R * y3,
    z: z3,
    visible: facing
  }};
}}

function drawGlobe(lonOffset) {{
  ctx.clearRect(0, 0, W, H);
  
  // === Atmosphere glow ===
  const atmos = ctx.createRadialGradient(cx, cy, R*0.85, cx, cy, R*1.15);
  atmos.addColorStop(0, 'rgba(0,80,220,0.0)');
  atmos.addColorStop(0.7, 'rgba(0,60,200,0.15)');
  atmos.addColorStop(1, 'rgba(0,40,180,0.0)');
  ctx.fillStyle = atmos;
  ctx.beginPath();
  ctx.arc(cx, cy, R*1.15, 0, Math.PI*2);
  ctx.fill();

  // === Globe base ===
  const grad = ctx.createRadialGradient(cx - R*0.3, cy - R*0.3, R*0.1, cx, cy, R);
  grad.addColorStop(0, '#1e4080');
  grad.addColorStop(0.4, '#0d1f42');
  grad.addColorStop(1, '#060d1e');
  ctx.beginPath();
  ctx.arc(cx, cy, R, 0, Math.PI*2);
  ctx.fillStyle = grad;
  ctx.fill();

  // Clip everything to globe circle
  ctx.save();
  ctx.beginPath();
  ctx.arc(cx, cy, R, 0, Math.PI*2);
  ctx.clip();

  // === Grid lines ===
  ctx.strokeStyle = 'rgba(30, 80, 160, 0.55)';
  ctx.lineWidth = 0.6;

  // Latitude lines
  for (let latLine = -75; latLine <= 75; latLine += 30) {{
    const latRad = latLine * Math.PI / 180;
    const ry = R * Math.sin(latRad);
    const rx = R * Math.cos(latRad);
    ctx.beginPath();
    ctx.ellipse(cx, cy - ry, rx, rx * 0.25, 0, 0, Math.PI*2);
    ctx.stroke();
  }}

  // Longitude lines (as ellipses)
  for (let lonLine = 0; lonLine < 180; lonLine += 30) {{
    const relLon = lonLine - lonOffset;
    const phi = relLon * Math.PI / 180;
    const xTilt = Math.cos(phi);
    
    ctx.beginPath();
    // Draw as vertical ellipse rotated by phi
    ctx.save();
    ctx.translate(cx, cy);
    ctx.scale(Math.abs(Math.cos(phi * 1)), 1);
    ctx.beginPath();
    ctx.ellipse(0, 0, Math.abs(xTilt) * R, R, 0, 0, Math.PI*2);
    ctx.restore();
    ctx.strokeStyle = `rgba(30,80,160,${{Math.abs(Math.cos(phi)) * 0.5 + 0.1}})`;
    ctx.lineWidth = 0.5;
    ctx.stroke();
  }}

  // === Continents ===
  continents.forEach(poly => {{
    ctx.beginPath();
    let first = true;
    let allHidden = true;
    
    poly.forEach(([lon, lat]) => {{
      const p = latLonToXY(lat, lon, lonOffset);
      if (p.visible) allHidden = false;
      if (first) {{ ctx.moveTo(p.x, p.y); first = false; }}
      else ctx.lineTo(p.x, p.y);
    }});
    ctx.closePath();
    
    if (!allHidden) {{
      ctx.fillStyle = 'rgba(22, 80, 140, 0.75)';
      ctx.fill();
      ctx.strokeStyle = 'rgba(40, 120, 200, 0.5)';
      ctx.lineWidth = 0.8;
      ctx.stroke();
    }}
  }});

  // === City pin ===
  if (HAS_CITY) {{
    const pin = latLonToXY(TARGET_LAT, TARGET_LON, lonOffset);
    if (pin.z > 0.05) {{
      const t = Date.now() / 1000;
      const pulse = 0.5 + 0.5 * Math.sin(t * 3);
      
      // Outer ring animation
      const ringR = 8 + pulse * 8;
      ctx.beginPath();
      ctx.arc(pin.x, pin.y, ringR, 0, Math.PI*2);
      ctx.strokeStyle = `rgba(0,212,255,${{0.5 - pulse * 0.4}})`;
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Middle ring
      ctx.beginPath();
      ctx.arc(pin.x, pin.y, 6, 0, Math.PI*2);
      ctx.strokeStyle = 'rgba(0,212,255,0.7)';
      ctx.lineWidth = 1.2;
      ctx.stroke();

      // Inner glow
      const pinGrad = ctx.createRadialGradient(pin.x, pin.y, 0, pin.x, pin.y, 5);
      pinGrad.addColorStop(0, 'rgba(0,255,255,1)');
      pinGrad.addColorStop(1, 'rgba(0,100,255,0)');
      ctx.beginPath();
      ctx.arc(pin.x, pin.y, 5, 0, Math.PI*2);
      ctx.fillStyle = pinGrad;
      ctx.fill();

      // Core dot
      ctx.beginPath();
      ctx.arc(pin.x, pin.y, 2.5, 0, Math.PI*2);
      ctx.fillStyle = '#00ffff';
      ctx.fill();
    }}
  }}

  ctx.restore(); // end clip

  // === Shine highlight ===
  const shine = ctx.createRadialGradient(cx - R*0.35, cy - R*0.3, 0, cx - R*0.1, cy - R*0.1, R*0.8);
  shine.addColorStop(0, 'rgba(80,150,255,0.18)');
  shine.addColorStop(0.5, 'rgba(40,80,200,0.06)');
  shine.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.beginPath();
  ctx.arc(cx, cy, R, 0, Math.PI*2);
  ctx.fillStyle = shine;
  ctx.fill();

  // === Outer rim ===
  ctx.beginPath();
  ctx.arc(cx, cy, R, 0, Math.PI*2);
  ctx.strokeStyle = 'rgba(0,100,220,0.4)';
  ctx.lineWidth = 1.5;
  ctx.stroke();
  
  // thin inner rim
  ctx.beginPath();
  ctx.arc(cx, cy, R - 2, 0, Math.PI*2);
  ctx.strokeStyle = 'rgba(0,180,255,0.12)';
  ctx.lineWidth = 1;
  ctx.stroke();
}}

// Orbit ring (drawn on separate pass, outside clip)
function drawOrbit(lonOffset) {{
  const t = Date.now() / 1000;
  // Draw orbit ellipse
  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(-0.25); // tilt
  ctx.beginPath();
  ctx.ellipse(0, 0, R*1.22, R*0.3, 0, 0, Math.PI*2);
  ctx.strokeStyle = 'rgba(0,80,200,0.35)';
  ctx.lineWidth = 1;
  ctx.setLineDash([4, 8]);
  ctx.stroke();
  ctx.setLineDash([]);
  
  // Satellite dot on orbit
  const satAngle = t * 0.7;
  const satX = Math.cos(satAngle) * R * 1.22;
  const satY = Math.sin(satAngle) * R * 0.3;
  ctx.beginPath();
  ctx.arc(satX, satY, 3, 0, Math.PI*2);
  ctx.fillStyle = '#00d4ff';
  ctx.shadowColor = '#00d4ff';
  ctx.shadowBlur = 8;
  ctx.fill();
  ctx.shadowBlur = 0;
  ctx.restore();
}}

// Easing function
function easeInOutCubic(t) {{
  return t < 0.5 ? 4*t*t*t : 1 - Math.pow(-2*t + 2, 3) / 2;
}}

// Normalize angle difference to [-180, 180]
function normalizeDelta(delta) {{
  while (delta > 180) delta -= 360;
  while (delta < -180) delta += 360;
  return delta;
}}

// Start globe: set initial lon to show Indian subcontinent by default
currentLonOffset = HAS_CITY ? TARGET_LON : 78;

if (DO_ANIMATE && HAS_CITY) {{
  animating = true;
  animStartTime = null;
  animFromLon = currentLonOffset - normalizeDelta(TARGET_LON - currentLonOffset) * 0 + 180;
  // Start from a random-ish angle
  animFromLon = TARGET_LON + 180;
  animToLon = TARGET_LON;
  currentLonOffset = animFromLon;
}}

function animate(timestamp) {{
  if (animating && DO_ANIMATE) {{
    if (!animStartTime) animStartTime = timestamp;
    const elapsed = timestamp - animStartTime;
    const progress = Math.min(elapsed / animDuration, 1);
    const eased = easeInOutCubic(progress);
    
    // Interpolate rotation
    const delta = normalizeDelta(animToLon - animFromLon);
    currentLonOffset = animFromLon + delta * eased;
    
    if (progress >= 1) {{
      currentLonOffset = animToLon;
      animating = false;
    }}
  }} else if (!HAS_CITY) {{
    // Idle rotation when no city selected
    currentLonOffset += idleRotSpeed;
  }}
  // else: stay fixed on city, just redraw for pin pulse
  
  ctx.clearRect(0, 0, W, H);
  drawGlobe(currentLonOffset);
  drawOrbit(currentLonOffset);
  
  requestAnimationFrame(animate);
}}

requestAnimationFrame(animate);
</script>
</body>
</html>
"""
    return html


# ─── Tool Functions ──────────────────────────────────────────────────────────
def get_weather(city: str) -> str:
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return f"⚠️ OPENWEATHER_API_KEY not set. (Demo) Weather in {city}: Clear skies, 28°C"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={api_key}&units=metric"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if str(data.get("cod")) != "200":
            return f"Error: {data.get('message', 'Could not fetch weather')}"
        temp = data["main"]["temp"]
        feels = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        desc = data["weather"][0]["description"].capitalize()
        return f"🌡️ **{desc}** · {temp}°C (feels {feels}°C) · 💧 Humidity: {humidity}%"
    except Exception as e:
        return f"Error fetching weather: {str(e)}"


def get_news(city: str) -> str:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return f"⚠️ TAVILY_API_KEY not set. (Demo) Latest news in {city}: City development projects underway."
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=api_key)
        response = client.search(query=f"latest news in {city}", search_depth="basic", max_results=3)
        results = response.get("results", [])
        if not results:
            return f"No news found for {city}"
        news_list = []
        for r in results:
            title = r.get("title", "No title")
            url_link = r.get("url", "")
            snippet = r.get("content", "")[:120]
            news_list.append(f"**{title}**\n🔗 {url_link}\n_{snippet}..._")
        return "\n\n---\n\n".join(news_list)
    except Exception as e:
        return f"Error fetching news: {str(e)}"


# ─── Agent Logic ─────────────────────────────────────────────────────────────
def detect_intent(text: str):
    text_lower = text.lower()
    wants_weather = any(w in text_lower for w in ["weather", "temperature", "temp", "hot", "cold", "rain", "sunny", "climate"])
    wants_news = any(w in text_lower for w in ["news", "latest", "update", "happening", "today", "current"])
    return wants_weather, wants_news


def extract_city(text: str) -> str | None:
    words = text.lower().replace(",", " ").replace(".", " ").split()
    # Try multi-word city names first
    for length in [3, 2]:
        for i in range(len(words) - length + 1):
            candidate = " ".join(words[i:i+length])
            if candidate in CITY_COORDS:
                return candidate.title()
    # Single word
    for word in words:
        if word in CITY_COORDS:
            return word.title()
    # Fallback: capitalize words that look like proper nouns (basic heuristic)
    skip = {"weather", "news", "city", "the", "in", "of", "for", "and", "what", "show", "get", "latest", "tell", "me", "about", "give", "today", "current", "is"}
    for word in text.split():
        if word[0].isupper() and word.lower() not in skip and len(word) > 2:
            return word
    return None


def process_query(user_input: str, approval_mode: bool = True):
    wants_weather, wants_news = detect_intent(user_input)
    city = extract_city(user_input)

    if not city:
        return None, "I couldn't identify a city in your message. Please mention a city name!", None

    coords = get_city_coords(city)
    results = {}

    tools_to_call = []
    if wants_weather:
        tools_to_call.append("get_weather")
    if wants_news:
        tools_to_call.append("get_news")
    if not tools_to_call:
        tools_to_call = ["get_weather", "get_news"]

    return city, tools_to_call, coords


# ─── Session State ────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_city" not in st.session_state:
    st.session_state.current_city = None
if "current_coords" not in st.session_state:
    st.session_state.current_coords = (20.0, 78.0)
if "globe_animate" not in st.session_state:
    st.session_state.globe_animate = False
if "pending_tools" not in st.session_state:
    st.session_state.pending_tools = []
if "pending_city" not in st.session_state:
    st.session_state.pending_city = None
if "awaiting_approval" not in st.session_state:
    st.session_state.awaiting_approval = False


# ─── Layout ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 32px 0 8px;">
  <div style="font-family:'Space Mono',monospace; font-size:10px; letter-spacing:0.3em; color:#4a6080; margin-bottom:6px;">◈ INTELLIGENCE TERMINAL v2.1 ◈</div>
  <div style="font-family:'Syne',sans-serif; font-size:36px; font-weight:800; color:#e2eaf6; letter-spacing:-0.02em; line-height:1;">
    CITY<span style="color:#00d4ff;">·</span>AGENT
  </div>
  <div style="font-family:'Space Mono',monospace; font-size:11px; color:#4a6080; margin-top:8px; letter-spacing:0.1em;">
    WEATHER &amp; NEWS INTELLIGENCE SYSTEM
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

# Two-column layout
left_col, right_col = st.columns([1, 1.6], gap="large")

# ─── LEFT: Globe ──────────────────────────────────────────────────────────────
with left_col:
    lat, lon = st.session_state.current_coords
    globe_html = render_globe(
        city_name=st.session_state.current_city,
        lat=lat, lon=lon,
        animate=st.session_state.globe_animate
    )
    components.html(globe_html, height=300, scrolling=False)

    # Status panel
    st.markdown(f"""
    <div style="
      background: #0d1321;
      border: 1px solid #1e2d45;
      border-radius: 8px;
      padding: 14px 16px;
      margin-top: 4px;
      font-family: 'Space Mono', monospace;
    ">
      <div style="font-size:9px; letter-spacing:0.2em; color:#4a6080; margin-bottom:10px;">◈ SYSTEM STATUS</div>
      <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:6px;">
        <span style="color:#4a6080;">TARGET CITY</span>
        <span style="color:#00d4ff;">{st.session_state.current_city or '—'}</span>
      </div>
      <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:6px;">
        <span style="color:#4a6080;">COORDINATES</span>
        <span style="color:#e2eaf6; font-size:10px;">{f'{lat:.2f}°N, {lon:.2f}°E' if st.session_state.current_city else '—'}</span>
      </div>
      <div style="display:flex; justify-content:space-between; font-size:11px;">
        <span style="color:#4a6080;">QUERIES RUN</span>
        <span style="color:#00ff88;">{len(st.session_state.messages) // 2}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ─── RIGHT: Chat ──────────────────────────────────────────────────────────────
with right_col:
    # Chat container
    st.markdown("""
    <div style="
      font-family:'Space Mono',monospace;
      font-size:9px;
      letter-spacing:0.2em;
      color:#4a6080;
      margin-bottom:10px;
    ">◈ AGENT CONVERSATION LOG</div>
    """, unsafe_allow_html=True)

    chat_container = st.container()

    with chat_container:
        # Render messages
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="
                  display:flex; justify-content:flex-end; margin-bottom:10px;
                ">
                  <div style="
                    background: #0d1f42;
                    border: 1px solid #1e3a6e;
                    border-radius: 10px 10px 2px 10px;
                    padding: 10px 14px;
                    max-width: 80%;
                    font-family: 'Space Mono', monospace;
                    font-size: 12px;
                    color: #a8c8f0;
                  ">
                    <span style="font-size:9px; color:#4a6080; display:block; margin-bottom:4px;">YOU</span>
                    {msg['content']}
                  </div>
                </div>
                """, unsafe_allow_html=True)
            elif msg["role"] == "tool_call":
                icon = "🌡️" if "weather" in msg["tool"] else "📰"
                color = "#00d4ff" if "weather" in msg["tool"] else "#7c3aed"
                st.markdown(f"""
                <div style="
                  margin-bottom:6px;
                  padding: 6px 12px;
                  background: rgba(0,0,0,0.3);
                  border-left: 2px solid {color};
                  border-radius: 0 6px 6px 0;
                  font-family: 'Space Mono', monospace;
                  font-size: 10px;
                  color: {color};
                ">
                  {icon} CALLING → <strong>{msg['tool'].upper()}</strong>({msg['city']})
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="
                  display:flex; margin-bottom:10px;
                ">
                  <div style="
                    background: #0d1321;
                    border: 1px solid #1e2d45;
                    border-radius: 10px 10px 10px 2px;
                    padding: 10px 14px;
                    max-width: 90%;
                    font-family: 'Space Mono', monospace;
                    font-size: 12px;
                    color: #e2eaf6;
                  ">
                    <span style="font-size:9px; color:#00d4ff; display:block; margin-bottom:6px;">◈ AGENT</span>
                    {msg['content']}
                  </div>
                </div>
                """, unsafe_allow_html=True)

        # Approval buttons
        if st.session_state.awaiting_approval and st.session_state.pending_tools:
            tool = st.session_state.pending_tools[0]
            city = st.session_state.pending_city
            icon = "🌡️" if "weather" in tool else "📰"
            color = "#00d4ff" if "weather" in tool else "#7c3aed"

            st.markdown(f"""
            <div style="
              background: #0d1321;
              border: 1px solid {color};
              border-radius: 8px;
              padding: 12px 16px;
              margin: 8px 0;
              font-family: 'Space Mono', monospace;
            ">
              <div style="font-size:9px; letter-spacing:0.2em; color:#4a6080; margin-bottom:8px;">◈ APPROVAL REQUIRED</div>
              <div style="font-size:12px; color:#e2eaf6; margin-bottom:10px;">
                {icon} Agent wants to call <span style="color:{color}; font-weight:bold;">{tool.upper()}</span> for <span style="color:#00ff88;">{city}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

            approve_col, deny_col = st.columns(2)
            with approve_col:
                if st.button("✓ APPROVE", key=f"approve_{tool}", use_container_width=True):
                    city_val = st.session_state.pending_city
                    tool_val = st.session_state.pending_tools.pop(0)

                    st.session_state.messages.append({"role": "tool_call", "tool": tool_val, "city": city_val, "content": ""})

                    with st.spinner(f"Fetching {tool_val}..."):
                        if "weather" in tool_val:
                            result = get_weather(city_val)
                        else:
                            result = get_news(city_val)

                    st.session_state.messages.append({"role": "assistant", "content": result})

                    if not st.session_state.pending_tools:
                        st.session_state.awaiting_approval = False
                        st.session_state.globe_animate = False

                    st.rerun()

            with deny_col:
                if st.button("✗ DENY", key=f"deny_{tool}", use_container_width=True):
                    st.session_state.pending_tools.pop(0)
                    st.session_state.messages.append({"role": "assistant", "content": f"🚫 Tool call `{tool}` was denied."})
                    if not st.session_state.pending_tools:
                        st.session_state.awaiting_approval = False
                        st.session_state.globe_animate = False
                    st.rerun()

    # Input area
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "QUERY INPUT",
            placeholder="e.g. Get weather and news for Mumbai",
            label_visibility="visible"
        )
        submitted = st.form_submit_button("⟶ TRANSMIT", use_container_width=True)

    if submitted and user_input.strip() and not st.session_state.awaiting_approval:
        query = user_input.strip()
        st.session_state.messages.append({"role": "user", "content": query})

        city, tools_or_error, coords = process_query(query)

        if city is None:
            st.session_state.messages.append({"role": "assistant", "content": tools_or_error})
        else:
            # Update globe
            st.session_state.current_city = city
            st.session_state.current_coords = coords if coords else (20.0, 78.0)
            st.session_state.globe_animate = True
            st.session_state.pending_city = city
            st.session_state.pending_tools = tools_or_error[:]
            st.session_state.awaiting_approval = True

        st.rerun()

# ─── Quick Examples ────────────────────────────────────────────────────────────
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; font-family:'Space Mono',monospace; font-size:9px; letter-spacing:0.2em; color:#4a6080; margin-bottom:10px;">◈ QUICK COMMANDS</div>
""", unsafe_allow_html=True)

example_cols = st.columns(4)
examples = [
    ("🌡️ Weather · Mumbai", "Get weather for Mumbai"),
    ("📰 News · Delhi", "Latest news in Delhi"),
    ("🌐 Both · Tokyo", "Weather and news for Tokyo"),
    ("🗺️ Both · New York", "Weather and news for New York"),
]

for i, (label, cmd) in enumerate(examples):
    with example_cols[i]:
        if st.button(label, key=f"ex_{i}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": cmd})
            city, tools_or_error, coords = process_query(cmd)
            if city:
                st.session_state.current_city = city
                st.session_state.current_coords = coords if coords else (20.0, 78.0)
                st.session_state.globe_animate = True
                st.session_state.pending_city = city
                st.session_state.pending_tools = tools_or_error[:]
                st.session_state.awaiting_approval = True
            st.rerun()

# Reset globe animation after render
if st.session_state.globe_animate and not st.session_state.awaiting_approval:
    st.session_state.globe_animate = False