# 🛰️ What's Above Me?

> A Python-based satellite tracker that shows which satellites are currently above your location — with real orbital mechanics.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Skyfield](https://img.shields.io/badge/Skyfield-1.49-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## 📸 Demo

```
╔═══════════════════════════════════════════════════════════════╗
║              🛰️  WHAT'S ABOVE ME — FULL REPORT               ║
╠═══════════════════════════════════════════════════════════════╣
║  📍 Location   : 52.2297°N, 21.0122°E, 100m                  ║
║  🕐 Time (UTC) : 2024-06-17 18:42:11                          ║
║  🛰️  Satellites : 10 tracked                                  ║
╚═══════════════════════════════════════════════════════════════╝

──────────────────────────────────────────────────────────────────
  👁️  VISIBLE RIGHT NOW (2 satellites)
──────────────────────────────────────────────────────────────────
  🟢 SUOMI NPP                    25.0°  SW   ▓▓▓▓▓▓▓▓
  🟢 NOAA 19                       5.7°  NNW  ▓

──────────────────────────────────────────────────────────────────
  🔭 NEXT PASSES — 24h window (7 found)
──────────────────────────────────────────────────────────────────

  🛰️  ISS (ZARYA)
      [████████████░░░░░░░░] in 2h 14m
      📅 20:56 UTC  │  ⏱️  6 min  │  📐 47°  │  ⭐⭐
```

---

## ✨ Features

- **Real-time satellite positions** — azimuth, elevation, distance from your location
- **Visible satellites** — instantly see what's above the horizon right now
- **Pass prediction** — find out when the next satellite will fly over your location
- **Pass quality rating** — ⭐⭐⭐ Excellent / ⭐⭐ Good / ⭐ Low pass
- **Offline fallback** — works without internet using built-in TLE data
- **Full logging** — all events saved to `app.log`
- **Input validation** — handles invalid coordinates gracefully

---

## 🛸 Tracked Satellites

The program tracks these real satellites currently in orbit:

| Satellite | Type | Altitude |
|---|---|---|
| ISS (ZARYA) | Space Station | ~400 km |
| Tiangong | Space Station | ~400 km |
| Hubble Space Telescope | Observatory | ~540 km |
| NOAA 19 | Weather | ~870 km |
| Terra | Earth Observation | ~710 km |
| Aqua | Earth Observation | ~710 km |
| Suomi NPP | Weather/Climate | ~830 km |
| Meteor-M 2 | Weather | ~830 km |
| Landsat 8 | Earth Observation | ~705 km |
| Sentinel-2A | Earth Observation | ~786 km |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/whats-above-me.git
cd whats-above-me

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

You will be prompted to enter your coordinates:

```
Enter latitude  (-90  to  90 ) : 52.2297
Enter longitude (-180 to 180) : 21.0122
Enter elevation in meters     : 100
```

> 💡 **Find your coordinates:** Right-click your location on [Google Maps](https://maps.google.com) and copy the coordinates.

---

## 📁 Project Structure

```
whats-above-me/
├── main.py               # Entry point — run this file
├── satellite_tracker.py  # Core logic: TLE loading, calculations, display
├── requirements.txt      # Python dependencies
├── README.md             # This file
└── app.log               # Generated at runtime — full activity log
```

---

## ⚙️ Configuration

Open `main.py` to adjust these settings:

```python
SEARCH_RADIUS_KM = 5000.0   # Search radius for nearby satellites (km)
HOURS_AHEAD      = 24        # How many hours ahead to predict passes
```

---

## 🔭 How It Works

This project uses **real orbital mechanics** — the same math used by NASA and ESA.

1. **TLE Data** (Two-Line Element sets) encode a satellite's orbital parameters — inclination, eccentricity, period, and more — captured at a specific moment in time.

2. **Skyfield** uses the SGP4 propagation model to mathematically predict where a satellite will be at any given moment, based on its TLE data.

3. **Topocentric coordinates** are computed by subtracting the observer's position (your coordinates on Earth) from the satellite's position in 3D space — giving azimuth, elevation angle, and distance.

4. **Pass prediction** works by scanning a future time window and finding the moments when a satellite crosses the horizon (elevation = 0°), which Skyfield calls AOS, TCA, and LOS events.

```
AOS — Acquisition of Signal  (satellite rises above horizon)
TCA — Time of Closest Approach (maximum elevation)
LOS — Loss of Signal          (satellite sets below horizon)
```

---

## 📦 Dependencies

| Library | Version | Purpose |
|---|---|---|
| [skyfield](https://rhodesmill.org/skyfield/) | 1.49 | Orbital mechanics & satellite position calculations |
| [requests](https://docs.python-requests.org/) | 2.31.0 | Downloading TLE data from CelesTrak |

---

## 🗺️ Roadmap

- [ ] Live refresh mode (auto-update every 30 seconds)
- [ ] Orbit visualization with `matplotlib`
- [ ] Interactive world map with `folium`
- [ ] CLI arguments with `argparse` (e.g. `--city Warsaw`)
- [ ] Export results to JSON / CSV
- [ ] Web interface with `Flask`

---

## 📄 License

This project is licensed under the MIT License.

---

## 👤 Author

Built as a portfolio project to explore satellite tracking and orbital mechanics with Python.

*Data source: [CelesTrak](https://celestrak.org/) — satellite TLE data updated multiple times daily.*