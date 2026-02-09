import fastf1
import pandas as pd


def load_race(year: int, race_name: str, session_type: str = "R"):
    fastf1.Cache.enable_cache("cache")

    print(f"Loading {year} {race_name} {session_type} session...")
    session = fastf1.get_session(year, race_name, session_type)
    session.load()
    print("Session loaded successfully.")
    return session


def get_driver_telemetry(session, driver_number: str):
    print(f"Extracting telemetry for driver {driver_number}...")

    laps = session.laps.pick_drivers([driver_number])

    if laps.empty:
        raise ValueError("No laps")

    lap = laps.pick_fastest()
    if lap is None:
        raise ValueError("No fastest lap")

    telemetry = lap.get_telemetry()
    
    # Extract all telemetry fields needed for focus mode graphs
    # Speed, Throttle, Brake, Gear are essential for broadcast-style telemetry
    df = telemetry[["Time", "X", "Y", "Speed", "Throttle", "Brake", "nGear"]].copy()
    
    # Rename nGear to Gear for consistency
    df.rename(columns={"nGear": "Gear"}, inplace=True)

    return df


def normalize_coordinates(df, width=1200, height=800, padding=50):
    df = df.copy()

    min_x, max_x = df["X"].min(), df["X"].max()
    min_y, max_y = df["Y"].min(), df["Y"].max()

    if max_x - min_x == 0 or max_y - min_y == 0:
        raise ValueError("Invalid telemetry range")

    df["screen_x"] = (df["X"] - min_x) / (max_x - min_x) * (width - 2 * padding) + padding
    df["screen_y"] = (df["Y"] - min_y) / (max_y - min_y) * (height - 2 * padding) + padding

    return df


def get_multiple_drivers_telemetry(session, driver_numbers):
    drivers_data = {}

    for driver in driver_numbers:
        try:
            df = get_driver_telemetry(session, driver)
            df = normalize_coordinates(df)
            drivers_data[driver] = df
            print(f"✔ Driver {driver} loaded")
        except Exception as e:
            print(f"⚠ Skipping driver {driver}: {e}")

    if not drivers_data:
        raise RuntimeError("No valid telemetry for any driver")

    return drivers_data
