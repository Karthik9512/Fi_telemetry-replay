import arcade
from data.fetch_data import load_race, get_multiple_drivers_telemetry
from ui.arcade_view import TrackView


def main():
    session = load_race(2023, "Monza", "R")

    drivers = ["16", "55", "1"]
    drivers_data = get_multiple_drivers_telemetry(session, drivers)

    window = TrackView(drivers_data)
    arcade.run()


if __name__ == "__main__":
    main()
