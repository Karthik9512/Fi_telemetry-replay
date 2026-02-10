import arcade

from data.fetch_data import load_race, get_multiple_drivers_telemetry, get_race_positions
from ui.arcade_view import TrackView


# ================= CIRCUIT → FASTF1 MAP =================
CIRCUIT_MAP = {
    # Europe
    "Bahrain": "Bahrain Grand Prix",
    "Jeddah": "Saudi Arabian Grand Prix",
    "Melbourne": "Australian Grand Prix",
    "Baku": "Azerbaijan Grand Prix",
    "Miami": "Miami Grand Prix",
    "Monaco": "Monaco Grand Prix",
    "Barcelona": "Spanish Grand Prix",
    "Montreal": "Canadian Grand Prix",
    "Spielberg": "Austrian Grand Prix",
    "Silverstone": "British Grand Prix",
    "Budapest": "Hungarian Grand Prix",
    "Spa": "Belgian Grand Prix",
    "Zandvoort": "Dutch Grand Prix",
    "Monza": "Italian Grand Prix",

    # Asia
    "Singapore": "Singapore Grand Prix",
    "Suzuka": "Japanese Grand Prix",
    "Lusail": "Qatar Grand Prix",
    "Shanghai": "Chinese Grand Prix",

    # Americas
    "Austin": "United States Grand Prix",
    "Mexico City": "Mexican Grand Prix",
    "Sao Paulo": "São Paulo Grand Prix",
    "Las Vegas": "Las Vegas Grand Prix",

    # Middle East
    "Yas Marina": "Abu Dhabi Grand Prix",
}

# ================= TEAM NORMALIZATION MAP =================
TEAM_NAME_MAP = {
    # Ferrari
    "Ferrari": "Ferrari",

    # Red Bull
    "Red Bull Racing": "Red Bull",
    "Oracle Red Bull Racing": "Red Bull",

    # Mercedes
    "Mercedes": "Mercedes",
    "Mercedes AMG F1": "Mercedes",
    "Mercedes-AMG Petronas F1 Team": "Mercedes",

    # McLaren
    "McLaren": "McLaren",
    "McLaren F1 Team": "McLaren",

    # Aston Martin
    "Aston Martin": "Aston Martin",
    "Aston Martin Aramco F1 Team": "Aston Martin",

    # Alpine
    "Alpine": "Alpine",
    "Alpine F1 Team": "Alpine",

    # Williams
    "Williams": "Williams",
    "Williams Racing": "Williams",

    # AlphaTauri / RB
    "Scuderia AlphaTauri": "AlphaTauri",
    "AlphaTauri": "AlphaTauri",
    "RB F1 Team": "AlphaTauri",
    "Visa Cash App RB": "AlphaTauri",

    # Alfa Romeo / Sauber
    "Alfa Romeo": "Alfa Romeo",
    "Alfa Romeo F1 Team": "Alfa Romeo",
    "Stake F1 Team": "Alfa Romeo",
    "Stake F1 Team Kick Sauber": "Alfa Romeo",

    # Haas
    "Haas": "Haas",
    "Haas F1 Team": "Haas",
}


# ================= TEAM FILTER =================
def get_drivers_by_team(session, selected_team):
    results = session.results.copy()

    results["NormalizedTeam"] = results["TeamName"].apply(
        lambda name: TEAM_NAME_MAP.get(name, name)
    )

    if selected_team == "ALL":
        return results["DriverNumber"].astype(str).tolist()

    return results[
        results["NormalizedTeam"] == selected_team
    ]["DriverNumber"].astype(str).tolist()


# ================= REPLAY LAUNCHER =================
def start_replay(circuit: str, team: str):
    print(f"Starting replay for circuit: {circuit}, team: {team}")

    year = 2024
    session_type = "R"

    # ✅ CIRCUIT MAP IS NOW DEFINED
    race_name = CIRCUIT_MAP.get(circuit)
    if not race_name:
        raise ValueError(f"Unsupported circuit: {circuit}")

    # Load FastF1 session
    session = load_race(year, race_name, session_type)

    # Filter drivers
    drivers = get_drivers_by_team(session, team)
    if not drivers:
        raise ValueError(f"No drivers found for team: {team}")

    print(f"Drivers selected: {drivers}")

    # ✅ DRIVER → TEAM MAP
    driver_team_map = {
        str(row.DriverNumber): TEAM_NAME_MAP.get(row.TeamName, row.TeamName)
        for _, row in session.results.iterrows()
    }

    # Load telemetry
    drivers_data = get_multiple_drivers_telemetry(session, drivers)

    # Load historical positions for chart
    print("Loading race position history...")
    position_history, max_laps = get_race_positions(session)

    # ✅ DRIVER → ABBREVIATION MAP
    driver_abbr_map = {
        str(row.DriverNumber): row.Abbreviation
        for _, row in session.results.iterrows()
    }

    # ✅ PASS ALL ARGUMENTS
    TrackView(
        drivers_data, 
        driver_team_map, 
        position_history=position_history, 
        total_laps=max_laps,
        driver_abbr_map=driver_abbr_map
    )
    arcade.run()
