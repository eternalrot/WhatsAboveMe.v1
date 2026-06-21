# main.py
# Entry point of the application.

import sys
import logging
from satellite_tracker import (
    get_satellites,
    show_satellite_list,
    get_observer_location,
    calculate_satellite_positions,
    show_satellite_positions,
    find_nearby_satellites,
    show_nearby_satellites,
    find_next_passes_for_all,
    show_next_passes,
    print_summary_report,
)

SEARCH_RADIUS_KM = 5000.0
HOURS_AHEAD      = 24

logger = logging.getLogger("satellite_tracker")


def main():
    print("=" * 65)
    print("   🛰️  What's Above Me? — Satellite Tracker")
    print("=" * 65)

    logger.info("=" * 40)
    logger.info("Application started")

    try:
        # Step 1: Load satellites
        satellites = get_satellites()
        show_satellite_list(satellites)

        # Step 2: Get observer location
        latitude, longitude, elevation = get_observer_location()

        # Step 3: Calculate positions
        print("\n⚙️  Calculating satellite positions...")
        positions = calculate_satellite_positions(
            satellites, latitude, longitude, elevation
        )
        show_satellite_positions(positions)

        # Step 4: Nearby satellites
        nearby = find_nearby_satellites(
            positions, max_distance_km=SEARCH_RADIUS_KM
        )
        show_nearby_satellites(nearby, max_distance_km=SEARCH_RADIUS_KM)

        # Step 5: Upcoming passes
        passes = find_next_passes_for_all(
            satellites, latitude, longitude, elevation,
            hours_ahead=HOURS_AHEAD
        )
        show_next_passes(passes, hours_ahead=HOURS_AHEAD)

        # Step 6: Summary report
        print_summary_report(
            positions   = positions,
            nearby      = nearby,
            passes      = passes,
            latitude    = latitude,
            longitude   = longitude,
            elevation   = elevation,
            radius_km   = SEARCH_RADIUS_KM,
            hours_ahead = HOURS_AHEAD,
        )

        logger.info("Application finished successfully")

    except KeyboardInterrupt:
        # User pressed Ctrl+C
        print("\n\n  👋 Interrupted by user. Goodbye!")
        logger.info("Application interrupted by user (Ctrl+C)")
        sys.exit(0)

    except Exception as e:
        print(f"\n  ❌ Unexpected error: {e}")
        print("  📄 Check app.log for details")
        logger.critical(f"Unhandled exception: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()