# satellite_tracker.py
# Core logic for satellite tracking.
# Stage 7: Added logging, error handling, and input validation.

from skyfield.api import load, EarthSatellite, wgs84
import requests
import logging
from datetime import datetime, timezone, timedelta

# ─────────────────────────────────────────────────────────
# LOGGING SETUP
# Writes to both the terminal AND a log file simultaneously
# ─────────────────────────────────────────────────────────

def setup_logging() -> logging.Logger:
    """
    Configures the application logger.
    Writes INFO+ to app.log and WARNING+ to the terminal.

    Returns:
        configured Logger instance
    """

    logger = logging.getLogger("satellite_tracker")
    logger.setLevel(logging.DEBUG)

    # ── File handler — saves everything to app.log ────────
    file_handler = logging.FileHandler("app.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_format)

    # ── Console handler — shows warnings in terminal ──────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_format = logging.Formatter("  ⚠️  %(message)s")
    console_handler.setFormatter(console_format)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Create logger — used throughout the entire module
logger = setup_logging()

# Timescale is Skyfield's internal clock
ts = load.timescale()

# ─────────────────────────────────────────────────────────
# FALLBACK TLE DATA
# ─────────────────────────────────────────────────────────

FALLBACK_TLE = """ISS (ZARYA)
1 25544U 98067A   24157.50000000  .00009579  00000-0  17355-3 0  9991
2 25544  51.6420 142.1335 0003664  49.2520  74.1281 15.50364452456009
HUBBLE SPACE TELESCOPE
1 20580U 90037B   24157.50000000  .00001018  00000-0  49985-4 0  9993
2 20580  28.4696 232.3123 0002679 318.1719 247.9234 15.09613492527371
NOAA 19
1 33591U 09005A   24157.50000000  .00000262  00000-0  17843-3 0  9998
2 33591  99.1906 188.3434 0013549 104.8303 255.4249 14.12271474793083
TERRA
1 25994U 99068A   24157.50000000  .00000106  00000-0  33003-4 0  9996
2 25994  98.2033  40.5987 0001232  91.2952 268.8413 14.57131240284459
AQUA
1 27424U 02022A   24157.50000000  .00000239  00000-0  62568-4 0  9993
2 27424  98.2127 125.8741 0001234  77.1928 283.9428 14.57326040167521
METEOR-M 2
1 40069U 14037A   24157.50000000  .00000052  00000-0  62617-5 0  9993
2 40069  98.5260 183.4820 0003028 254.6547 105.4286 14.20650792505369
SUOMI NPP
1 37849U 11061A   24157.50000000  .00000025  00000-0  28588-4 0  9991
2 37849  98.7089  26.8194 0001230  92.4603 267.6757 14.19529811646601
TIANGONG
1 48274U 21035A   24157.50000000  .00019453  00000-0  22408-3 0  9993
2 48274  41.4744  95.5000 0006108 104.0000 256.1000 15.61223234178411
LANDSAT 8
1 39084U 13008A   24157.50000000  .00000070  00000-0  21020-4 0  9993
2 39084  98.2186 163.4682 0001361  91.0803 269.0537 14.57114731594827
SENTINEL-2A
1 40697U 15028A   24157.50000000  .00000069  00000-0  33752-4 0  9994
2 40697  98.5687 190.5432 0001084  88.4679 271.6641 14.30818014480420"""


# ─────────────────────────────────────────────────────────
# SATELLITE LOADING
# ─────────────────────────────────────────────────────────

def load_fallback_satellites() -> list:
    """Loads hardcoded TLE data as a fallback."""

    satellites = []
    lines = FALLBACK_TLE.strip().splitlines()

    for i in range(0, len(lines) - 2, 3):
        name  = lines[i].strip()
        line1 = lines[i + 1].strip()
        line2 = lines[i + 2].strip()

        if line1.startswith("1") and line2.startswith("2"):
            try:
                sat = EarthSatellite(line1, line2, name, ts)
                satellites.append(sat)
                logger.debug(f"Loaded fallback satellite: {name}")
            except Exception as e:
                logger.error(f"Failed to parse TLE for {name}: {e}")

    logger.info(f"Fallback satellites loaded: {len(satellites)}")
    return satellites


def get_satellites() -> list:
    """
    Tries to download fresh TLE data from CelesTrak.
    Falls back to hardcoded data if all URLs fail.
    """

    urls = [
        "https://celestrak.org/pub/TLE/stations.txt",
        "https://celestrak.org/pub/TLE/visual.txt",
        "https://celestrak.org/pub/TLE/active.txt",
    ]

    session = requests.Session()
    session.headers.update({
        "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/120.0.0.0 Safari/537.36",
        "Accept":          "text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer":         "https://celestrak.org/",
    })

    for url in urls:
        try:
            logger.info(f"Fetching TLE data from: {url}")
            print(f"  📡 Trying: {url}")

            response = session.get(url, timeout=10)
            response.raise_for_status()

            lines = response.text.strip().splitlines()
            satellites = []

            for i in range(0, len(lines) - 2, 3):
                name  = lines[i].strip()
                line1 = lines[i + 1].strip()
                line2 = lines[i + 2].strip()

                if line1.startswith("1") and line2.startswith("2"):
                    try:
                        sat = EarthSatellite(line1, line2, name, ts)
                        satellites.append(sat)
                    except Exception as e:
                        logger.warning(f"Skipping invalid TLE for {name}: {e}")

            if satellites:
                logger.info(f"Loaded {len(satellites)} satellites from {url}")
                print(f"  ✅ Satellites loaded from internet: {len(satellites)}")
                return satellites

        except requests.exceptions.ConnectionError:
            logger.warning(f"No internet connection for: {url}")
            print(f"  ⚠️  No connection: {url}")

        except requests.exceptions.Timeout:
            logger.warning(f"Request timed out: {url}")
            print(f"  ⚠️  Timeout: {url}")

        except requests.exceptions.HTTPError as e:
            logger.warning(f"HTTP error for {url}: {e}")
            print(f"  ⚠️  Failed ({e}): {url}")

        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            print(f"  ⚠️  Unexpected error: {e}")

    logger.warning("All URLs failed — switching to fallback data")
    print("  📦 Using built-in satellite data (offline mode)...")
    satellites = load_fallback_satellites()
    print(f"  ✅ Satellites loaded from fallback: {len(satellites)}")
    return satellites


# ─────────────────────────────────────────────────────────
# DISPLAY FUNCTIONS
# ─────────────────────────────────────────────────────────

def show_satellite_list(satellites: list, limit: int = 20) -> None:
    """Prints a readable list of satellites."""

    print("\n" + "=" * 55)
    print("   📋 SATELLITE LIST")
    print("=" * 55)

    for i, sat in enumerate(satellites[:limit]):
        print(f"  {i + 1:>3}. {sat.name}")

    print("=" * 55)
    print(f"  Showing {min(limit, len(satellites))} of {len(satellites)} satellites")
    print("=" * 55)
    logger.info(f"Displayed satellite list ({len(satellites)} total)")


# ─────────────────────────────────────────────────────────
# OBSERVER LOCATION
# ─────────────────────────────────────────────────────────

def get_observer_location() -> tuple:
    """
    Asks the user to enter their coordinates.
    Validates input with clear error messages.
    Allows up to 5 attempts before raising an error.
    """

    print("\n" + "=" * 55)
    print("   📍 ENTER YOUR LOCATION")
    print("=" * 55)
    print("  Tip: Right-click your location on Google Maps")
    print("=" * 55)

    MAX_ATTEMPTS = 5

    for attempt in range(MAX_ATTEMPTS):

        try:
            lat_input = input("\n  Latitude  (-90  to  90 ) : ").strip()
            if not lat_input:
                print("  ❌ Latitude cannot be empty.")
                continue

            lat = float(lat_input)
            if not (-90 <= lat <= 90):
                print("  ❌ Latitude must be between -90 and 90.")
                logger.warning(f"Invalid latitude entered: {lat_input}")
                continue

            lon_input = input("  Longitude (-180 to 180) : ").strip()
            if not lon_input:
                print("  ❌ Longitude cannot be empty.")
                continue

            lon = float(lon_input)
            if not (-180 <= lon <= 180):
                print("  ❌ Longitude must be between -180 and 180.")
                logger.warning(f"Invalid longitude entered: {lon_input}")
                continue

            elev_input = input("  Elevation in meters (Enter = 0) : ").strip()
            elev = float(elev_input) if elev_input else 0.0

            if elev < -500 or elev > 9000:
                print("  ❌ Elevation must be between -500 and 9000 meters.")
                continue

            logger.info(f"Observer location set: lat={lat}, lon={lon}, elev={elev}")
            print(f"\n  ✅ Location set: {lat}°N, {lon}°E, {elev}m")
            return lat, lon, elev

        except ValueError:
            remaining = MAX_ATTEMPTS - attempt - 1
            print(f"  ❌ Invalid number. {remaining} attempt(s) remaining.")
            logger.warning(f"Non-numeric input on attempt {attempt + 1}")

    # All attempts exhausted — use default location (Warsaw)
    logger.error("Max input attempts reached — using default location (Warsaw)")
    print("\n  ⚠️  Too many invalid attempts. Using default: Warsaw, Poland.")
    return 52.2297, 21.0122, 100.0


# ─────────────────────────────────────────────────────────
# POSITION CALCULATIONS
# ─────────────────────────────────────────────────────────

def calculate_satellite_positions(
    satellites: list,
    latitude:   float,
    longitude:  float,
    elevation:  float
) -> list:
    """Calculates position of each satellite relative to the observer."""

    observer     = wgs84.latlon(latitude, longitude, elevation)
    current_time = ts.now()
    results      = []

    for sat in satellites:
        try:
            difference  = sat - observer
            topocentric = difference.at(current_time)
            alt, az, dist = topocentric.altaz()

            sat_position    = sat.at(current_time)
            sat_lat, sat_lon = wgs84.latlon_of(sat_position)
            sat_height      = wgs84.height_of(sat_position)

            results.append({
                "name":      sat.name,
                "altitude":  alt.degrees,
                "azimuth":   az.degrees,
                "distance":  dist.km,
                "height_km": sat_height.km,
                "sat_lat":   sat_lat.degrees,
                "sat_lon":   sat_lon.degrees,
            })

            logger.debug(
                f"{sat.name}: alt={alt.degrees:.1f}° "
                f"az={az.degrees:.1f}° dist={dist.km:.0f}km"
            )

        except Exception as e:
            logger.error(f"Failed to calculate position for {sat.name}: {e}")

    logger.info(f"Calculated positions for {len(results)} satellites")
    return results


def show_satellite_positions(positions: list) -> None:
    """Displays satellite positions in a table."""

    print("\n" + "=" * 65)
    print("   🛰️  SATELLITE POSITIONS (current time)")
    print("=" * 65)
    print(f"  {'NAME':<25} {'ALT':>6} {'AZ':>7} {'DIST':>10} {'HEIGHT':>8}")
    print(f"  {'':─<25} {'':─>6} {'':─>7} {'':─>10} {'':─>8}")

    for pos in positions:
        visibility = "👁️ " if pos["altitude"] > 0 else "   "
        print(
            f"  {visibility}{pos['name']:<23} "
            f"{pos['altitude']:>5.1f}° "
            f"{pos['azimuth']:>6.1f}° "
            f"{pos['distance']:>9.0f}km "
            f"{pos['height_km']:>7.0f}km"
        )

    print("=" * 65)


# ─────────────────────────────────────────────────────────
# NEARBY SATELLITES
# ─────────────────────────────────────────────────────────

def find_nearby_satellites(
    positions:       list,
    max_distance_km: float = 1000.0
) -> list:
    """Filters and sorts satellites by distance."""

    nearby = [p for p in positions if p["distance"] <= max_distance_km]
    nearby.sort(key=lambda x: x["distance"])
    logger.info(
        f"Found {len(nearby)} satellites within {max_distance_km:.0f} km"
    )
    return nearby


def get_compass_direction(azimuth: float) -> str:
    """Converts azimuth degrees to compass direction string."""
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return directions[int((azimuth + 22.5) / 45) % 8]


def show_nearby_satellites(
    nearby:          list,
    max_distance_km: float = 1000.0
) -> None:
    """Displays detailed info for nearby satellites."""

    print("\n" + "=" * 65)
    print(f"   🎯 SATELLITES WITHIN {max_distance_km:.0f} KM")
    print("=" * 65)

    if not nearby:
        print(f"\n  No satellites found within {max_distance_km:.0f} km")
        print("  Try increasing the search radius in main.py")
        print("=" * 65)
        return

    for i, pos in enumerate(nearby):
        compass = get_compass_direction(pos["azimuth"])

        if pos["altitude"] > 10:
            status = "🟢 Clearly visible"
        elif pos["altitude"] > 0:
            status = "🟡 Near horizon"
        else:
            status = "🔴 Below horizon"

        print(f"\n  #{i + 1} — {pos['name']}")
        print(f"  {'─' * 45}")
        print(f"  📏 Distance      : {pos['distance']:,.0f} km")
        print(f"  🏔️  Height        : {pos['height_km']:,.0f} km")
        print(f"  📐 Elevation     : {pos['altitude']:.1f}°")
        print(f"  🧭 Direction     : {pos['azimuth']:.1f}° ({compass})")
        print(f"  👁️  Status        : {status}")

    print("\n" + "=" * 65)
    print(f"  Found {len(nearby)} satellite(s) within {max_distance_km:.0f} km")
    print("=" * 65)


# ─────────────────────────────────────────────────────────
# PASS PREDICTION
# ─────────────────────────────────────────────────────────

def find_next_pass(
    satellite:   EarthSatellite,
    latitude:    float,
    longitude:   float,
    elevation:   float,
    hours_ahead: int = 24
) -> dict | None:
    """Finds the next pass of a satellite over the observer."""

    observer = wgs84.latlon(latitude, longitude, elevation)
    t0 = ts.now()
    t1 = ts.from_datetime(datetime.now(timezone.utc) + timedelta(hours=hours_ahead))

    try:
        times, events = satellite.find_events(
            observer, t0, t1, altitude_degrees=0.0
        )

        if len(times) == 0:
            return None

        pass_data = {}

        for time, event in zip(times, events):
            if event == 0 and "aos" not in pass_data:
                pass_data["aos"] = time

            elif event == 1 and "aos" in pass_data:
                pass_data["tca"] = time
                diff = satellite - observer
                alt, az, _ = diff.at(time).altaz()
                pass_data["max_elevation"] = alt.degrees
                pass_data["tca_azimuth"]   = az.degrees

            elif event == 2 and "tca" in pass_data:
                pass_data["los"] = time
                aos_dt = pass_data["aos"].utc_datetime()
                los_dt = pass_data["los"].utc_datetime()
                pass_data["duration_min"] = (
                    los_dt - aos_dt
                ).total_seconds() / 60
                break

        if all(k in pass_data for k in ["aos", "tca", "los"]):
            logger.debug(
                f"Pass found for {satellite.name}: "
                f"AOS={pass_data['aos'].utc_datetime().strftime('%H:%M')}"
            )
            return pass_data

        return None

    except Exception as e:
        logger.error(f"Error finding pass for {satellite.name}: {e}")
        return None


def find_next_passes_for_all(
    satellites:  list,
    latitude:    float,
    longitude:   float,
    elevation:   float,
    hours_ahead: int = 24
) -> list:
    """Finds next pass for all satellites, sorted by AOS time."""

    print(f"\n⏳ Searching passes for next {hours_ahead} hours...")
    results = []

    for sat in satellites:
        pass_data = find_next_pass(
            sat, latitude, longitude, elevation, hours_ahead
        )
        if pass_data:
            pass_data["name"] = sat.name
            results.append(pass_data)
            print(f"  ✅ {sat.name:<30} — pass found")
        else:
            print(f"  ⭕ {sat.name:<30} — no pass in {hours_ahead}h")

    results.sort(key=lambda x: x["aos"].utc_datetime())
    logger.info(f"Found {len(results)} passes in next {hours_ahead}h")
    return results


def show_next_passes(passes: list, hours_ahead: int = 24) -> None:
    """Displays upcoming satellite passes."""

    print("\n" + "=" * 65)
    print(f"   🔭 UPCOMING PASSES — next {hours_ahead} hours (UTC)")
    print("=" * 65)

    if not passes:
        print(f"\n  No passes found in the next {hours_ahead} hours.")
        print("  Try increasing HOURS_AHEAD in main.py")
        print("=" * 65)
        return

    for i, p in enumerate(passes):
        aos_dt        = p["aos"].utc_datetime()
        tca_dt        = p["tca"].utc_datetime()
        los_dt        = p["los"].utc_datetime()
        now           = datetime.now(timezone.utc)
        minutes_until = (aos_dt - now).total_seconds() / 60
        compass       = get_compass_direction(p["tca_azimuth"])

        if p["max_elevation"] >= 60:
            quality = "⭐⭐⭐ Excellent"
        elif p["max_elevation"] >= 30:
            quality = "⭐⭐   Good"
        elif p["max_elevation"] >= 10:
            quality = "⭐     Low"
        else:
            quality = "      Marginal"

        if minutes_until < 60:
            time_str = f"in {minutes_until:.0f} min"
        else:
            h = int(minutes_until // 60)
            m = int(minutes_until % 60)
            time_str = f"in {h}h {m:02d}m"

        print(f"\n  #{i + 1} — {p['name']}")
        print(f"  {'─' * 50}")
        print(f"  🛫 AOS : {aos_dt.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"  🎯 TCA : {tca_dt.strftime('%H:%M:%S')} UTC")
        print(f"  🛬 LOS : {los_dt.strftime('%H:%M:%S')} UTC")
        print(f"  ⏱️  Duration  : {p['duration_min']:.1f} min")
        print(f"  📐 Max elev. : {p['max_elevation']:.1f}°  {quality}")
        print(f"  🧭 Direction : {p['tca_azimuth']:.1f}° ({compass})")
        print(f"  🕐 {time_str}")

    print("\n" + "=" * 65)
    print(f"  Total: {len(passes)} pass(es) in next {hours_ahead} hours")
    print("=" * 65)


# ─────────────────────────────────────────────────────────
# SUMMARY REPORT
# ─────────────────────────────────────────────────────────

def get_time_bar(minutes_until: float, total_minutes: float = 360) -> str:
    """Creates a visual progress bar for time until next pass."""

    bar_length = 20
    filled     = int((1 - min(minutes_until, total_minutes) / total_minutes) * bar_length)
    filled     = max(0, filled)
    return f"[{'█' * filled}{'░' * (bar_length - filled)}]"


def print_summary_report(
    positions:   list,
    nearby:      list,
    passes:      list,
    latitude:    float,
    longitude:   float,
    elevation:   float,
    radius_km:   float,
    hours_ahead: int,
) -> None:
    """Prints the complete summary report."""

    now_utc = datetime.now(timezone.utc)
    visible = [p for p in positions if p["altitude"] > 0]

    print("\n")
    print("╔" + "═" * 63 + "╗")
    print("║" + "   🛰️  WHAT'S ABOVE ME — FULL REPORT".center(64) + "║")
    print("╠" + "═" * 63 + "╣")
    print(f"║  📍 Location   : {latitude:.4f}°N, {longitude:.4f}°E, {elevation:.0f}m".ljust(63) + "║")
    print(f"║  🕐 Time (UTC) : {now_utc.strftime('%Y-%m-%d %H:%M:%S')}".ljust(63) + "║")
    print(f"║  🛰️  Satellites : {len(positions)} tracked".ljust(65) + "║")
    print("╚" + "═" * 63 + "╝")

    # Currently visible
    print("\n" + "─" * 65)
    print(f"  👁️  VISIBLE RIGHT NOW ({len(visible)} satellites)")
    print("─" * 65)

    if visible:
        for pos in sorted(visible, key=lambda x: x["altitude"], reverse=True):
            compass = get_compass_direction(pos["azimuth"])
            bar     = "▓" * int(pos["altitude"] / 3)
            print(f"  🟢 {pos['name']:<28} {pos['altitude']:>5.1f}°  {compass:<3}  {bar}")
    else:
        print("  No satellites currently above the horizon.")

    # Nearby
    print("\n" + "─" * 65)
    print(f"  🎯 WITHIN {radius_km:.0f} KM ({len(nearby)} satellites)")
    print("─" * 65)

    if nearby:
        for pos in nearby:
            status = "🟢" if pos["altitude"] > 0 else "🔴"
            print(
                f"  {status} {pos['name']:<28} "
                f"{pos['distance']:>6,.0f} km  │  "
                f"{pos['height_km']:>5.0f} km alt"
            )
    else:
        print(f"  No satellites within {radius_km:.0f} km right now.")

    # Upcoming passes
    print("\n" + "─" * 65)
    print(f"  🔭 NEXT PASSES — {hours_ahead}h window ({len(passes)} found)")
    print("─" * 65)

    if passes:
        for p in passes[:5]:
            aos_dt        = p["aos"].utc_datetime()
            minutes_until = (aos_dt - now_utc).total_seconds() / 60
            bar           = get_time_bar(minutes_until)

            if p["max_elevation"] >= 60:
                stars = "⭐⭐⭐"
            elif p["max_elevation"] >= 30:
                stars = "⭐⭐ "
            else:
                stars = "⭐  "

            if minutes_until < 60:
                time_str = f"in {minutes_until:.0f} min"
            else:
                h = int(minutes_until // 60)
                m = int(minutes_until % 60)
                time_str = f"in {h}h {m:02d}m"

            print(f"\n  🛰️  {p['name']}")
            print(f"      {bar} {time_str}")
            print(
                f"      📅 {aos_dt.strftime('%H:%M')} UTC  │  "
                f"⏱️  {p['duration_min']:.0f} min  │  "
                f"📐 {p['max_elevation']:.0f}°  │  {stars}"
            )
    else:
        print(f"  No passes found in the next {hours_ahead} hours.")

    print("\n" + "╔" + "═" * 63 + "╗")
    print("║" + "  ✅ Report complete — What's Above Me? v1.0".ljust(62) + "║")
    print("╚" + "═" * 63 + "╝")

    logger.info("Summary report displayed successfully")
    print(f"\n  📄 Full log saved to: app.log")