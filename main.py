import arcade
from data.fetch_data import (
    load_race,
    get_driver_telemetry,
    normalize_coordinates,
)
from ui.arcade_view import TrackView


def main():
    session = load_race(2023, "Monza", "R")

    df = get_driver_telemetry(session, "16")
    df = normalize_coordinates(df)

    window = TrackView(df)
    arcade.run()


if __name__ == "__main__":
    main()
