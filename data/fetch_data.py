import fastf1
import pandas as pd


def load_race(year: int, race_name: str, session_type: str = "R"):
    # Enable FastF1 cache
    fastf1.Cache.enable_cache("cache")

    print(f"Loading {year} {race_name} {session_type} session...")

    session = fastf1.get_session(year, race_name, session_type)
    session.load()

    print("Session loaded successfully.")
    return session


def get_driver_telemetry(session, driver_number: str):
    """
    Extract telemetry data for a specific driver.
    Returns a pandas DataFrame with time, X, Y, speed.
    """
    print(f"Extracting telemetry for driver {driver_number}...")

    lap = session.laps.pick_driver(driver_number).pick_fastest()
    telemetry = lap.get_telemetry()

    df = telemetry[["Time", "X", "Y", "Speed"]].copy()

    print("Telemetry extracted.")
    return df


def normalize_coordinates(df, width=1200, height=800, padding=50):
    """
    Normalize X, Y telemetry coordinates to fit inside a window.
    Returns a new DataFrame with screen_x and screen_y.
    """

    df = df.copy()

    min_x, max_x = df["X"].min(), df["X"].max()
    min_y, max_y = df["Y"].min(), df["Y"].max()

    # Prevent division by zero (important safety)
    x_range = max_x - min_x
    y_range = max_y - min_y

    if x_range == 0 or y_range == 0:
        raise ValueError("Invalid telemetry data: zero range in X or Y")

    df["screen_x"] = (
        (df["X"] - min_x) / x_range
    ) * (width - 2 * padding) + padding

    df["screen_y"] = (
        (df["Y"] - min_y) / y_range
    ) * (height - 2 * padding) + padding

    return df
