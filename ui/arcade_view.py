import arcade
import math
from collections import deque
from ui.circuits import CIRCUIT_MAP
import pandas as pd


# ================= WINDOW =================
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
WINDOW_TITLE = "F1 Telemetry Replay - Driver Focus Mode"

# ================= LAYOUT (TASK 1: Collision-Free) =================
LEADERBOARD_WIDTH = 280
LEADERBOARD_PADDING = 20
TRACK_VIEWPORT_WIDTH = WINDOW_WIDTH - LEADERBOARD_WIDTH - LEADERBOARD_PADDING
TRACK_VIEWPORT_HEIGHT = WINDOW_HEIGHT
TRACK_PADDING = 90

# ================= HUD STYLE =================
HUD_BG_COLOR = (30, 30, 30, 220)
HUD_SELECTED_BG = (50, 80, 120, 180)  # Blue tint for selected driver
HUD_ROW_HEIGHT = 18

# ================= TRACK STYLE =================
TRACK_BASE_COLOR = (60, 60, 60)
TRACK_LINE_COLOR = (120, 120, 120)
TRACK_BASE_WIDTH = 10
TRACK_LINE_WIDTH = 4

# ================= CAMERA (TASK 2) =================
CAMERA_ZOOM_FACTOR = 1.2
CAMERA_SMOOTH_SPEED = 0.1

# ================= TELEMETRY (DRIVER FOCUS MODE) =================
TELEMETRY_PANEL_BG = (15, 15, 15, 240)
TELEMETRY_GRAPH_HEIGHT = 100
TELEMETRY_GRAPH_MARGIN = 12
TELEMETRY_HISTORY_SECONDS = 10  # Show last 10 seconds

# ================= MINI TRACK =================
MINI_TRACK_SIZE = 150
MINI_TRACK_MARGIN = 40

# ================= RACE CONFIG =================
TOTAL_LAPS = 3

# ================= TEAM COLORS =================
TEAM_COLORS = {
    "Red Bull": (6, 0, 239),
    "Ferrari": (220, 0, 0),
    "Mercedes": (192, 192, 192),
    "McLaren": (255, 135, 0),
    "Aston Martin": (0, 111, 98),
    "Alpine": (255, 95, 190),
    "Williams": (0, 90, 255),
    "RB": (242, 242, 242),
    "Haas": (177, 18, 38),
    "Sauber": (0, 255, 135),
}


class TrackView(arcade.Window):
    def __init__(self,
             drivers_data,
             driver_team_map,
             position_history=None,
             total_laps=None,
             driver_abbr_map=None,
             weather_data=None,          # ✅ NEW
             circuit_name=None):         # ✅ NEW

        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # ================= ORIGINAL DATA =================
        self.drivers_data = drivers_data
        self.driver_team_map = driver_team_map
        self.driver_abbr_map = driver_abbr_map if driver_abbr_map else {}

    # ================= WEATHER DATA =================
        self.weather_data = weather_data     # FastF1 weather dataframe
        self.circuit_name = circuit_name
        self.current_weather = None          # Will update dynamically

    # ================= RACE CONFIG =================
        self.total_laps = total_laps if total_laps else TOTAL_LAPS

    # ================= POSITION HISTORY =================
        if position_history:
            self.position_history = position_history
            self.has_full_history = True
        else:
            self.position_history = {
            str(driver): [i + 1]
            for i, driver in enumerate(drivers_data.keys())
        }
            self.has_full_history = False

    # ================= SIMULATION STATE =================
        self.driver_indices = {d: 0.0 for d in drivers_data}
        self.driver_times = {d: 0.0 for d in drivers_data}
        self.driver_laps = {d: 1 for d in drivers_data}
        self.current_race_lap = 1.0

        self.speed_multiplier = 1.0
        self.paused = False
        self.elapsed_time = 0.0

    # ================= CAMERA =================
        self.focused_driver = None
        self.camera_offset_x = 0.0
        self.camera_offset_y = 0.0
        self.camera_zoom = 1.0

    # ================= LEADERBOARD =================
        self.leaderboard_rows = {}

    # ================= FOCUS MODE =================
        self.focus_mode = False

    # ================= TELEMETRY HISTORY =================
        self.telemetry_history = {
        'speed': deque(maxlen=500),
        'throttle': deque(maxlen=500),
        'brake': deque(maxlen=500),
        'gear': deque(maxlen=500),
    }

    # ================= POSITION CHART =================
        self.show_position_chart = False
        self.position_chart_button = None

    # ================= TRACK SCALING =================
        self._rescale_track_to_viewport()

        arcade.set_background_color(arcade.color.BLACK)


    def _draw_weather_panel(self):
        if not self.current_weather:
            return

        panel_width = 260
        panel_height = 170

        x1 = WINDOW_WIDTH - panel_width - 20
        y1 = 20
        x2 = x1 + panel_width
        y2 = y1 + panel_height

    # Background
        arcade.draw_lrbt_rectangle_filled(
            x1, x2, y1, y2,
            (20, 20, 20, 230)
        )

        arcade.draw_lrbt_rectangle_outline(
            x1, x2, y1, y2,
            arcade.color.GRAY, 2
        )

        w = self.current_weather

        arcade.draw_text(
            "WEATHER",
            x1 + 15, y2 - 25,
            arcade.color.WHITE, 14, bold=True
        )

        arcade.draw_text(f"Track: {w['track_temp']}°C", x1 + 15, y2 - 55, arcade.color.LIGHT_GRAY, 12)
        arcade.draw_text(f"Air: {w['air_temp']}°C", x1 + 15, y2 - 75, arcade.color.LIGHT_GRAY, 12)
        arcade.draw_text(f"Humidity: {w['humidity']}%", x1 + 15, y2 - 95, arcade.color.LIGHT_GRAY, 12)
        arcade.draw_text(f"Wind: {w['wind']} km/h", x1 + 15, y2 - 115, arcade.color.LIGHT_GRAY, 12)

        color = arcade.color.RED if w["condition"] == "WET" else arcade.color.GREEN

        arcade.draw_text(
            f"Condition: {w['condition']}",
            x1 + 15, y2 - 140,
            color, 13, bold=True
        )


    def _rescale_track_to_viewport(self):
        """
        Rescale all track coordinates to fit within the reserved track viewport.
        """
        for driver, df in self.drivers_data.items():
            min_x = df["screen_x"].min()
            max_x = df["screen_x"].max()
            min_y = df["screen_y"].min()
            max_y = df["screen_y"].max()

            df["screen_x"] = (
                (df["screen_x"] - min_x) / (max_x - min_x) * 
                (TRACK_VIEWPORT_WIDTH - 2 * TRACK_PADDING) + TRACK_PADDING
            )
            df["screen_y"] = (
                (df["screen_y"] - min_y) / (max_y - min_y) * 
                (TRACK_VIEWPORT_HEIGHT - 2 * TRACK_PADDING) + TRACK_PADDING
            )

    def format_time(self, seconds):
        m = int(seconds // 60)
        s = seconds % 60
        return f"{m:02d}:{s:06.3f}"

    def get_leaderboard(self):
        return sorted(
            self.driver_indices.items(),
            key=lambda x: (self.driver_laps[x[0]], x[1]),
            reverse=True
        )

    def get_time_gaps(self, leaderboard):
        leader = leaderboard[0][0]
        leader_time = self.driver_times[leader]

        gaps = {}
        for i, (driver, _) in enumerate(leaderboard):
            if i == 0:
                gaps[driver] = "LEADER"
            else:
                gap = max(self.driver_times[driver] - leader_time, 0.0)
                gaps[driver] = f"+{gap:.3f}s"
        return gaps

    def _update_camera(self, delta_time):
        """
        Smoothly interpolate camera to focus on the selected driver.
        """
        # In focus mode, camera is not used (we use mini track instead)
        if self.focus_mode:
            self.camera_offset_x = 0.0
            self.camera_offset_y = 0.0
            self.camera_zoom = 1.0
            return

        if self.focused_driver and self.focused_driver in self.drivers_data:
            df = self.drivers_data[self.focused_driver]
            idx = int(self.driver_indices[self.focused_driver])
            target_x = df.iloc[idx]["screen_x"]
            target_y = df.iloc[idx]["screen_y"]

            target_offset_x = TRACK_VIEWPORT_WIDTH / 2 - target_x
            target_offset_y = WINDOW_HEIGHT / 2 - target_y
            target_zoom = CAMERA_ZOOM_FACTOR
        else:
            target_offset_x = 0.0
            target_offset_y = 0.0
            target_zoom = 1.0

        self.camera_offset_x += (target_offset_x - self.camera_offset_x) * CAMERA_SMOOTH_SPEED
        self.camera_offset_y += (target_offset_y - self.camera_offset_y) * CAMERA_SMOOTH_SPEED
        self.camera_zoom += (target_zoom - self.camera_zoom) * CAMERA_SMOOTH_SPEED

    def _apply_camera_transform(self, x, y):
        """
        Apply camera offset and zoom to a coordinate.
        """
        center_x = TRACK_VIEWPORT_WIDTH / 2
        center_y = WINDOW_HEIGHT / 2

        x = center_x + (x - center_x) * self.camera_zoom
        y = center_y + (y - center_y) * self.camera_zoom

        x += self.camera_offset_x
        y += self.camera_offset_y

        return x, y

    def on_draw(self):
        self.clear()

        if self.show_position_chart:
            self._draw_position_chart()
            self._draw_mini_track()
        elif self.focus_mode and self.focused_driver:
            self._draw_focus_mode()
        else:
            self._draw_normal_mode()
        self._draw_weather_panel()

    def _draw_normal_mode(self):
        """Normal track view with camera controls."""
        df0 = next(iter(self.drivers_data.values()))

        # Track
        for i in range(len(df0) - 1):
            x1, y1 = self._apply_camera_transform(
                df0.iloc[i]["screen_x"], df0.iloc[i]["screen_y"]
            )
            x2, y2 = self._apply_camera_transform(
                df0.iloc[i + 1]["screen_x"], df0.iloc[i + 1]["screen_y"]
            )
            arcade.draw_line(x1, y1, x2, y2, TRACK_BASE_COLOR, TRACK_BASE_WIDTH)

        for i in range(0, len(df0) - 1, 2):
            x1, y1 = self._apply_camera_transform(
                df0.iloc[i]["screen_x"], df0.iloc[i]["screen_y"]
            )
            x2, y2 = self._apply_camera_transform(
                df0.iloc[i + 1]["screen_x"], df0.iloc[i + 1]["screen_y"]
            )
            arcade.draw_line(x1, y1, x2, y2, TRACK_LINE_COLOR, TRACK_LINE_WIDTH)

        # Start/Finish line
        x0, y0 = df0.iloc[0][["screen_x", "screen_y"]]
        x1, y1 = df0.iloc[1][["screen_x", "screen_y"]]

        dx, dy = x1 - x0, y1 - y0
        length = math.hypot(dx, dy)
        px, py = -dy / length, dx / length

        start_x1, start_y1 = self._apply_camera_transform(x0 + px * 20, y0 + py * 20)
        start_x2, start_y2 = self._apply_camera_transform(x0 - px * 20, y0 - py * 20)
        arcade.draw_line(start_x1, start_y1, start_x2, start_y2, arcade.color.WHITE, 4)

        # Cars
        for driver, df in self.drivers_data.items():
            idx = int(self.driver_indices[driver])
            x, y = df.iloc[idx][["screen_x", "screen_y"]]
            x, y = self._apply_camera_transform(x, y)

            team = self.driver_team_map.get(driver, "")
            color = TEAM_COLORS.get(team, arcade.color.WHITE)

            if self.focused_driver and driver != self.focused_driver:
                color = tuple(int(c * 0.4) for c in color[:3])

            arcade.draw_circle_outline(x, y, 7, arcade.color.BLACK, 2)
            arcade.draw_circle_filled(x, y, 5, color)

        # Leaderboard
        self._draw_leaderboard()

        # Info
        arcade.draw_text(
            f"Speed {self.speed_multiplier:.2f}x",
            20, WINDOW_HEIGHT - 30,
            arcade.color.WHITE, 14, bold=True
        )

        if self.paused:
            arcade.draw_text(
                "PAUSED",
                TRACK_VIEWPORT_WIDTH // 2 - 40,
                WINDOW_HEIGHT - 40,
                arcade.color.WHITE,
                16
            )

        if self.focused_driver:
            arcade.draw_text(
                f"Following: {self.focused_driver}",
                20, WINDOW_HEIGHT - 55,
                arcade.color.YELLOW, 12, italic=True
            )

    def _draw_focus_mode(self):
        """
        Draw focus mode with telemetry graphs and minimized track.
        """
        # Telemetry panel background
        arcade.draw_lrbt_rectangle_filled(
            0, WINDOW_WIDTH - LEADERBOARD_WIDTH - LEADERBOARD_PADDING,
            0, WINDOW_HEIGHT,
            TELEMETRY_PANEL_BG
        )

        # Driver info header
        team = self.driver_team_map.get(self.focused_driver, "")
        team_color = TEAM_COLORS.get(team, arcade.color.WHITE)
        
        arcade.draw_text(
            f"DRIVER {self.focused_driver}",
            30, WINDOW_HEIGHT - 40,
            team_color, 20, bold=True
        )
        
        arcade.draw_text(
            team,
            30, WINDOW_HEIGHT - 70,
            arcade.color.LIGHT_GRAY, 14
        )

        # Telemetry graphs
        # Telemetry graphs
        graph_start_y = WINDOW_HEIGHT - 200
        
        # Speed Graph
        self._draw_telemetry_graph(
            'speed', "SPEED (km/h)", 
            30, graph_start_y, 
            TRACK_VIEWPORT_WIDTH - 60, TELEMETRY_GRAPH_HEIGHT,
            team_color, 0, 350
        )
        
        # Combined Throttle & Brake Graph (NEW!)
        self._draw_combined_throttle_brake_graph(
            30, graph_start_y - TELEMETRY_GRAPH_HEIGHT - TELEMETRY_GRAPH_MARGIN,
            TRACK_VIEWPORT_WIDTH - 60, TELEMETRY_GRAPH_HEIGHT
        )
        
        # Gear Graph
        self._draw_telemetry_graph(
            'gear', "GEAR", 
            30, graph_start_y - 2 * (TELEMETRY_GRAPH_HEIGHT + TELEMETRY_GRAPH_MARGIN),
            TRACK_VIEWPORT_WIDTH - 60, TELEMETRY_GRAPH_HEIGHT,
            arcade.color.CYAN, 0, 8, step_graph=True
        )

        # Minimized track
        self._draw_mini_track()

        # Leaderboard
        self._draw_leaderboard()

        # Controls info
        arcade.draw_text(
            "Press ESC to exit focus mode",
            30, 30,
            arcade.color.GRAY, 12, italic=True
        )

    def _draw_combined_throttle_brake_graph(self, x, y, width, height):
        """
        Draw combined throttle and brake graph with center zero line.
        Professional F1 broadcast style visualization with filled areas.
        
        Throttle: plotted ABOVE center line (0 to +100%)
        Brake: plotted BELOW center line (0 to -100%)
        """
        # Background - darker for better contrast
        arcade.draw_lrbt_rectangle_filled(
            x, x + width, y, y + height,
            (15, 15, 15, 220)
        )
        
        # Border
        arcade.draw_lrbt_rectangle_outline(
            x, x + width, y, y + height,
            (80, 80, 80), 2
        )
        
        # Label
        arcade.draw_text(
            "THROTTLE & BRAKE (%)",
            x + 8, y + height - 18,
            arcade.color.WHITE, 10, bold=True
        )
        
        # Center line (zero line) - most important visual element
        center_y = y + height / 2
        arcade.draw_line(
            x, center_y, x + width, center_y,
            (120, 120, 120), 2
        )
        
        # Grid lines (horizontal) - subtle
        for i in range(1, 3):
            # Above center (throttle zone)
            grid_y = center_y + (height / 2) * (i / 2)
            arcade.draw_line(
                x, grid_y, x + width, grid_y,
                (40, 40, 40), 1
            )
            # Below center (brake zone)
            grid_y = center_y - (height / 2) * (i / 2)
            arcade.draw_line(
                x, grid_y, x + width, grid_y,
                (40, 40, 40), 1
            )
        
        # Y-axis labels (Right aligned to avoid title overlap)
        arcade.draw_text(
            "+100", x + width - 35, y + height - 12,
            (0, 220, 0), 8
        )
        arcade.draw_text(
            "0", x + width - 25, center_y - 4,
            (160, 160, 160), 8
        )
        arcade.draw_text(
            "-100", x + width - 35, y + 3,
            (220, 0, 0), 8
        )
        
        # Get data
        throttle_data = list(self.telemetry_history['throttle'])
        brake_data = list(self.telemetry_history['brake'])
        
        if len(throttle_data) < 2 or len(brake_data) < 2:
            return
        
        current_time = self.elapsed_time
        time_window_start = current_time - TELEMETRY_HISTORY_SECONDS
        
        # Draw THROTTLE (above center line) with filled area
        throttle_points = []
        for time_val, value in throttle_data:
            time_ratio = (time_val - time_window_start) / TELEMETRY_HISTORY_SECONDS
            px = x + (time_ratio * width)
            
            value_ratio = value / 100.0
            py = center_y + (value_ratio * height / 2)
            
            throttle_points.append((px, py))
        
        # Draw filled area under throttle line
        if len(throttle_points) >= 2:
            # Create polygon points for filled area
            fill_points = [(throttle_points[0][0], center_y)]  # Start at center line
            fill_points.extend(throttle_points)  # Add all data points
            fill_points.append((throttle_points[-1][0], center_y))  # End at center line
            
            # Draw filled area with transparency
            arcade.draw_polygon_filled(fill_points, (0, 200, 0, 80))
            
            # Draw line on top for clarity
            for i in range(len(throttle_points) - 1):
                x1, y1 = throttle_points[i]
                x2, y2 = throttle_points[i + 1]
                arcade.draw_line(x1, y1, x2, y2, (0, 255, 0), 2)
        
        # Draw BRAKE (below center line) with filled area
        brake_points = []
        for time_val, value in brake_data:
            time_ratio = (time_val - time_window_start) / TELEMETRY_HISTORY_SECONDS
            px = x + (time_ratio * width)
            
            value_ratio = value / 100.0
            py = center_y - (value_ratio * height / 2)
            
            brake_points.append((px, py))
        
        # Draw filled area under brake line
        if len(brake_points) >= 2:
            # Create polygon points for filled area
            fill_points = [(brake_points[0][0], center_y)]  # Start at center line
            fill_points.extend(brake_points)  # Add all data points
            fill_points.append((brake_points[-1][0], center_y))  # End at center line
            
            # Draw filled area with transparency
            arcade.draw_polygon_filled(fill_points, (200, 0, 0, 80))
            
            # Draw line on top for clarity
            for i in range(len(brake_points) - 1):
                x1, y1 = brake_points[i]
                x2, y2 = brake_points[i + 1]
                arcade.draw_line(x1, y1, x2, y2, (255, 0, 0), 2)
        
        # Current value indicators
        if throttle_points:
            last_x, last_y = throttle_points[-1]
            arcade.draw_circle_filled(last_x, last_y, 4, (0, 255, 0))
            
            current_throttle = throttle_data[-1][1]
            arcade.draw_text(
                f"T: {current_throttle:.0f}%",
                x + width - 80, y + height - 25,
                (0, 255, 0), 12, bold=True
            )
        
        if brake_points:
            last_x, last_y = brake_points[-1]
            arcade.draw_circle_filled(last_x, last_y, 4, (255, 0, 0))
            
            current_brake = brake_data[-1][1]
            arcade.draw_text(
                f"B: {current_brake:.0f}%",
                x + width - 80, y + height - 45,
                (255, 0, 0), 12, bold=True
            )

    def _draw_telemetry_graph(self, data_key, label, x, y, width, height, color, min_val, max_val, step_graph=False):
        """
        Draw a single telemetry graph with scrolling effect.
        """
        # Background
        arcade.draw_lrbt_rectangle_filled(
            x, x + width, y, y + height,
            (25, 25, 25, 200)
        )
        
        # Border
        arcade.draw_lrbt_rectangle_outline(
            x, x + width, y, y + height,
            (60, 60, 60), 2
        )
        
        # Label
        arcade.draw_text(
            label,
            x + 10, y + height - 25,
            arcade.color.WHITE, 12, bold=True
        )
        
        # Grid lines
        for i in range(5):
            grid_y = y + (height * i / 4)
            arcade.draw_line(
                x, grid_y, x + width, grid_y,
                (50, 50, 50), 1
            )
        
        # Get data
        data = list(self.telemetry_history[data_key])
        
        if len(data) < 2:
            return
        
        current_time = self.elapsed_time
        time_window_start = current_time - TELEMETRY_HISTORY_SECONDS
        
        # Map data to screen coordinates
        points = []
        for time_val, value in data:
            time_ratio = (time_val - time_window_start) / TELEMETRY_HISTORY_SECONDS
            px = x + (time_ratio * width)
            
            value_ratio = (value - min_val) / (max_val - min_val)
            py = y + (value_ratio * height)
            
            points.append((px, py))
        
        # Draw line
        if step_graph:
            for i in range(len(points) - 1):
                x1, y1 = points[i]
                x2, y2 = points[i + 1]
                arcade.draw_line(x1, y1, x2, y1, color, 2)
                arcade.draw_line(x2, y1, x2, y2, color, 2)
        else:
            for i in range(len(points) - 1):
                x1, y1 = points[i]
                x2, y2 = points[i + 1]
                arcade.draw_line(x1, y1, x2, y2, color, 3)
        
        # Current value indicator
        if points:
            last_x, last_y = points[-1]
            arcade.draw_circle_filled(last_x, last_y, 4, color)
            
            current_val = data[-1][1]
            arcade.draw_text(
                f"{current_val:.0f}",
                x + width - 60, y + height - 25,
                color, 14, bold=True
            )

    def _draw_mini_track(self):
        """
        Draw minimized track in bottom-right corner.
        """
        mini_x = WINDOW_WIDTH - LEADERBOARD_WIDTH - LEADERBOARD_PADDING - MINI_TRACK_SIZE - MINI_TRACK_MARGIN
        mini_y = MINI_TRACK_MARGIN
        
        # Background - darker with more opacity
        arcade.draw_lrbt_rectangle_filled(
            mini_x, mini_x + MINI_TRACK_SIZE,
            mini_y, mini_y + MINI_TRACK_SIZE,
            (10, 10, 10, 240)
        )
        
        # Border - brighter for better definition
        arcade.draw_lrbt_rectangle_outline(
            mini_x, mini_x + MINI_TRACK_SIZE,
            mini_y, mini_y + MINI_TRACK_SIZE,
            (100, 100, 100), 2
        )
        
        # Label
        arcade.draw_text(
            "TRACK",
            mini_x + 10, mini_y + MINI_TRACK_SIZE - 20,
            (180, 180, 180), 9, bold=True
        )
        
        # Get track bounds
        df0 = next(iter(self.drivers_data.values()))
        min_x = df0["screen_x"].min()
        max_x = df0["screen_x"].max()
        min_y = df0["screen_y"].min()
        max_y = df0["screen_y"].max()
        
        track_width = max_x - min_x
        track_height = max_y - min_y
        
        # Better padding for track inside mini map
        padding = 15
        scale = min((MINI_TRACK_SIZE - 2 * padding) / track_width, (MINI_TRACK_SIZE - 2 * padding) / track_height)
        
        # Center the track in the mini map
        scaled_width = track_width * scale
        scaled_height = track_height * scale
        offset_x = (MINI_TRACK_SIZE - scaled_width) / 2
        offset_y = (MINI_TRACK_SIZE - scaled_height) / 2
        
        # Draw track outline with better visibility
        for i in range(len(df0) - 1):
            x1 = mini_x + offset_x + (df0.iloc[i]["screen_x"] - min_x) * scale
            y1 = mini_y + offset_y + (df0.iloc[i]["screen_y"] - min_y) * scale
            x2 = mini_x + offset_x + (df0.iloc[i + 1]["screen_x"] - min_x) * scale
            y2 = mini_y + offset_y + (df0.iloc[i + 1]["screen_y"] - min_y) * scale
            
            arcade.draw_line(x1, y1, x2, y2, (100, 100, 100), 2)
        
        # Draw focused driver with glow effect
        if self.focused_driver in self.drivers_data:
            df = self.drivers_data[self.focused_driver]
            idx = int(self.driver_indices[self.focused_driver])
            
            car_x = mini_x + offset_x + (df.iloc[idx]["screen_x"] - min_x) * scale
            car_y = mini_y + offset_y + (df.iloc[idx]["screen_y"] - min_y) * scale
            
            team = self.driver_team_map.get(self.focused_driver, "")
            color = TEAM_COLORS.get(team, arcade.color.WHITE)
            
            # Glow effect
            arcade.draw_circle_filled(car_x, car_y, 7, (*color[:3], 100))
            # Main car dot
            arcade.draw_circle_filled(car_x, car_y, 5, color)
            # Bright center
            arcade.draw_circle_filled(car_x, car_y, 2, arcade.color.WHITE)

    def _draw_leaderboard(self):
        """Draw a professional F1-style leaderboard HUD with abbreviations and team colors."""
        leaderboard = self.get_leaderboard()
        gaps = self.get_time_gaps(leaderboard)

        # 1. Calculation of Layout
        row_count = len(leaderboard)
        header_height = 45
        footer_height = 45 # Space for button
        hud_height = header_height + (row_count * HUD_ROW_HEIGHT) + footer_height
        
        left = TRACK_VIEWPORT_WIDTH + LEADERBOARD_PADDING
        right = WINDOW_WIDTH - LEADERBOARD_PADDING
        top = WINDOW_HEIGHT - LEADERBOARD_PADDING
        bottom = top - hud_height
        
        # 2. Main Background
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (15, 15, 15, 230))
        
        # 3. Header (F1 RACE / LAP)
        header_bottom = top - header_height
        arcade.draw_lrbt_rectangle_filled(left, right, header_bottom, top, (10, 10, 10, 255))
        
        # Logo placeholder
        arcade.draw_text("F1", left + 15, top - 25, arcade.color.WHITE, 16, bold=True, italic=True)
        arcade.draw_text("RACE", left + 40, top - 25, arcade.color.GRAY, 12, bold=True)
        
        # Lap text
        leader_driver = leaderboard[0][0] if leaderboard else None
        lap_total = self.total_laps
        curr_lap = self.driver_laps[leader_driver] if leader_driver else 0
        arcade.draw_text(
            f"LAP {curr_lap}/{lap_total}", (left + right) // 2, header_bottom + 10,
            arcade.color.WHITE, 10, bold=True, anchor_x="center"
        )

        self.leaderboard_rows.clear()
        
        # 4. Driver Rows
        current_y = header_bottom - HUD_ROW_HEIGHT
        for pos, (driver, _) in enumerate(leaderboard, start=1):
            team = self.driver_team_map.get(driver, "")
            color = TEAM_COLORS.get(team, arcade.color.WHITE)
            abbr = self.driver_abbr_map.get(driver, driver)

            row_top = current_y + HUD_ROW_HEIGHT
            row_bottom = current_y
            
            # Row Background (for focus)
            if driver == self.focused_driver:
                arcade.draw_lrbt_rectangle_filled(left, right, row_bottom, row_top, (45, 45, 45, 255))
            
            # Team Color Stripe
            arcade.draw_lrbt_rectangle_filled(left, left + 4, row_bottom + 2, row_top - 2, color)

            # Position
            arcade.draw_text(str(pos), left + 12, current_y + 5, arcade.color.WHITE, 10, bold=True)

            # Abbreviation
            arcade.draw_text(abbr, left + 35, current_y + 5, arcade.color.WHITE, 10, bold=True)

            # Gap
            gap_text = gaps.get(driver, "")
            arcade.draw_text(gap_text, right - 12, current_y + 5, arcade.color.WHITE, 9, anchor_x="right")

            # Interaction tracking
            self.leaderboard_rows[driver] = (left, row_bottom, right, row_top)
            current_y -= HUD_ROW_HEIGHT

        # 5. Position Chart Button (Fixed at bottom)
        button_y1 = bottom + 10
        button_y2 = button_y1 + 28
        button_x1, button_x2 = left + 10, right - 10
        
        arcade.draw_lrbt_rectangle_filled(button_x1, button_x2, button_y1, button_y2, (40, 40, 40, 255))
        arcade.draw_text(
            "VIEW POSITION CHART", (button_x1 + button_x2) // 2, button_y1 + 8,
            arcade.color.WHITE, 9, bold=True, anchor_x="center"
        )
        self.position_chart_button = (button_x1, button_y1, button_x2, button_y2)

    def _draw_position_chart(self):
        """
        Draw a premium, professional F1-style position chart with:
        - Live progress tracking (vertical line)
        - Driver legend with team colors
        - Highlighted current focused driver
        - Dark grid aesthetics
        """
        # Layout variables
        LEGEND_WIDTH = 100
        MARGIN = 60
        CHART_PADDING = 20
        
        chart_left = MARGIN
        chart_right = WINDOW_WIDTH - LEADERBOARD_WIDTH - LEADERBOARD_PADDING - LEGEND_WIDTH - MARGIN
        chart_bottom = 120
        chart_top = WINDOW_HEIGHT - 100
        
        chart_width = chart_right - chart_left
        chart_height = chart_top - chart_bottom

        # Background - Very dark, almost black
        arcade.draw_lrbt_rectangle_filled(
            0, WINDOW_WIDTH - LEADERBOARD_WIDTH-LEADERBOARD_PADDING,
            0, WINDOW_HEIGHT,
            (10, 10, 10, 255)
        )
        
        # Grid lines (X-axis: Laps)
        max_laps = self.total_laps
        for lap in range(1, max_laps + 1):
            x = chart_left + ((lap - 1) / max(1, max_laps - 1)) * chart_width
            # Vertical line
            arcade.draw_line(
                x, chart_bottom, x, chart_top, 
                (40, 40, 40, 150), 1
            )
            # Lap label
            arcade.draw_text(
                str(lap), x, chart_bottom - 30,
                arcade.color.GRAY, 10, anchor_x="center"
            )

        # Grid lines (Y-axis: Positions)
        drivers = list(self.position_history.keys())
        num_drivers = len(drivers) if drivers else 20
        positions_to_show = [1, 5, 10, 15, num_drivers]
        
        for pos in positions_to_show:
            y = chart_top - ((pos - 1) / max(1, num_drivers - 1)) * chart_height
            # Horizontal line
            arcade.draw_line(
                chart_left, y, chart_right, y, 
                (40, 40, 40, 150), 1
            )
            # Position label
            arcade.draw_text(
                str(pos), chart_left - 25, y - 5,
                arcade.color.GRAY, 10, anchor_x="right"
            )

        # Title
        arcade.draw_text(
            "POSITION CHANGES",
            chart_left, chart_top + 40,
            arcade.color.WHITE, 22, bold=True
        )
        
        # Labels
        arcade.draw_text("LAP", (chart_left + chart_right) // 2, chart_bottom - 60, arcade.color.GRAY, 12, anchor_x="center")
        arcade.draw_text("POS", chart_left - 60, (chart_top + chart_bottom) // 2, arcade.color.GRAY, 12, rotation=90, anchor_x="center")

        # Position History Lines
        for driver in drivers:
            history = self.position_history.get(driver, [])
            if len(history) < 1:
                continue

            team = self.driver_team_map.get(driver, "")
            color = TEAM_COLORS.get(team, arcade.color.WHITE)
            
            # Focused driver line is bright and thick, others are slightly dimmed
            if self.focused_driver and driver == self.focused_driver:
                line_color = color
                line_width = 4
                z_order = 10
            else:
                line_color = (*color[:3], 150) # Dimmed
                line_width = 2
                z_order = 1
            
            points = []
            for lap_idx, pos in enumerate(history):
                # Map lap_idx (0-based) to chart X
                x = chart_left + (lap_idx / (max_laps - 1)) * chart_width
                y = chart_top - ((pos - 1) / (num_drivers - 1)) * chart_height
                points.append((x, y))
            
            if len(points) >= 2:
                arcade.draw_line_strip(points, line_color, line_width)
            elif len(points) == 1:
                 arcade.draw_circle_filled(points[0][0], points[0][1], line_width, line_color)

        # LIVE PROGRESS MARKER (Vertical red line)
        progress_x = chart_left + ((self.current_race_lap - 1) / (max_laps - 1)) * chart_width
        arcade.draw_line(
            progress_x, chart_bottom, progress_x, chart_top,
            (255, 0, 0, 200), 2
        )
        # Progress label
        arcade.draw_text(
            f"LAP {self.current_race_lap:.1f}",
            progress_x, chart_top + 10,
            (255, 50, 50), 10, bold=True, anchor_x="center"
        )

        # LEGEND (Right side)
        legend_x = chart_right + 30
        legend_y_start = chart_top
        
        # Sort drivers by their current position for the legend
        sorted_drivers = sorted(
            drivers,
            key=lambda d: self.position_history[d][-1] if self.position_history.get(d) else 99
        )
        
        for i, driver in enumerate(sorted_drivers):
            abbr = self.driver_abbr_map.get(driver, driver)
            team = self.driver_team_map.get(driver, "")
            color = TEAM_COLORS.get(team, arcade.color.WHITE)
            
            row_y = legend_y_start - i * 22
            
            # Active/Focused driver highlight in legend
            if driver == self.focused_driver:
                arcade.draw_lrbt_rectangle_filled(
                    legend_x - 5, legend_x + 80,
                    row_y - 2, row_y + 16,
                    (60, 60, 60, 200)
                )
            
            # Color indicator
            arcade.draw_lrbt_rectangle_filled(legend_x, legend_x + 10, row_y + 2, row_y + 12, color)
            
            # Abbreviation text
            arcade.draw_text(
                abbr, legend_x + 20, row_y,
                arcade.color.WHITE if driver != self.focused_driver else arcade.color.YELLOW, 
                10, bold=(driver == self.focused_driver)
            )

        # Return instruction
        arcade.draw_text(
            "PRESS ESC TO RETURN TO TRACK",
            chart_left, 40,
            arcade.color.DARK_GRAY, 10, italic=True
        )

        # Sub-views
        self._draw_leaderboard()
        self._draw_mini_track()

    def _update_telemetry_history(self):
        """Update telemetry history buffers for scrolling graphs."""
        if not self.focus_mode or not self.focused_driver:
            return

        df = self.drivers_data[self.focused_driver]
        idx = int(self.driver_indices[self.focused_driver])
        
        if idx >= len(df):
            return
        
        current_time = self.elapsed_time
        
        speed = df.iloc[idx].get("Speed", 0)
        throttle = df.iloc[idx].get("Throttle", 0)
        brake = df.iloc[idx].get("Brake", 0)
        gear = df.iloc[idx].get("Gear", 0)

        self.telemetry_history['speed'].append((current_time, speed))
        self.telemetry_history['throttle'].append((current_time, throttle))
        self.telemetry_history['brake'].append((current_time, brake))
        self.telemetry_history['gear'].append((current_time, gear))

        # Remove old data outside time window
        cutoff_time = current_time - TELEMETRY_HISTORY_SECONDS
        
        for key in self.telemetry_history:
            while self.telemetry_history[key] and self.telemetry_history[key][0][0] < cutoff_time:
                self.telemetry_history[key].popleft()

    def on_update(self, delta_time):
        if self.paused:
            return

        self.elapsed_time += delta_time * self.speed_multiplier
        
        leaderboard = self.get_leaderboard()
        current_standings = {d: i + 1 for i, (d, _) in enumerate(leaderboard)}

        # Track overall race progress based on leader
        if leaderboard:
            leader_driver = leaderboard[0][0]
            leader_df = self.drivers_data[leader_driver]
            leader_idx = self.driver_indices[leader_driver]
            lap_progress = leader_idx / len(leader_df)
            self.current_race_lap = self.driver_laps[leader_driver] + lap_progress

        for driver, df in self.drivers_data.items():
            self.driver_indices[driver] += self.speed_multiplier
            self.driver_times[driver] += delta_time * self.speed_multiplier

            if self.driver_indices[driver] >= len(df):
                self.driver_indices[driver] = 0.0
                self.driver_times[driver] = 0.0
                self.driver_laps[driver] += 1
                
                # Record position history at end of lap ONLY if we don't have full history
                if not self.has_full_history and self.driver_laps[driver] <= self.total_laps:
                    if driver in current_standings:
                        self.position_history[driver].append(current_standings[driver])
        self._update_weather_from_fastf1()

        self._update_camera(delta_time)
        self._update_telemetry_history()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.paused = not self.paused
        elif key == arcade.key.UP:
            self.speed_multiplier = min(self.speed_multiplier + 0.25, 10)
        elif key == arcade.key.DOWN:
            self.speed_multiplier = max(self.speed_multiplier - 0.25, 0.25)
        elif key == arcade.key.ESCAPE or key == arcade.key.BACKSPACE:
            if self.show_position_chart:
                self.show_position_chart = False
            elif self.focus_mode:
                self.focus_mode = False
                self.focused_driver = None
                for key in self.telemetry_history:
                    self.telemetry_history[key].clear()
            else:
                self.focused_driver = None

    def on_mouse_press(self, x, y, button, modifiers):
        """
        Detect clicks on leaderboard rows to enter/exit focus mode.
        """
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        # --- Position chart button click ---
        if self.position_chart_button:
            x1, y1, x2, y2 = self.position_chart_button
            if x1 <= x <= x2 and y1 <= y <= y2:
                self.show_position_chart = not self.show_position_chart
                return

        clicked_driver = None
        for driver, (x1, y1, x2, y2) in self.leaderboard_rows.items():
            if x1 <= x <= x2 and y1 <= y <= y2:
                clicked_driver = driver
                break

        if clicked_driver:
            if self.focused_driver == clicked_driver and self.focus_mode:
                # Exit focus mode
                self.focus_mode = False
                self.focused_driver = None
                for key in self.telemetry_history:
                    self.telemetry_history[key].clear()
            else:
                # Enter or switch focus mode
                self.focused_driver = clicked_driver
                self.focus_mode = True
                for key in self.telemetry_history:
                    self.telemetry_history[key].clear()
        else:
            # Clicked outside leaderboard
            if self.focus_mode:
                self.focus_mode = False
                self.focused_driver = None
                for key in self.telemetry_history:
                    self.telemetry_history[key].clear()
            else:
                self.focused_driver = None
    
    def _update_weather_from_fastf1(self):
        if self.weather_data is None or len(self.weather_data) == 0:
            return

        current_time = pd.Timedelta(seconds=self.elapsed_time)
        df = self.weather_data

        idx = (df["Time"] - current_time).abs().idxmin()
        row = df.loc[idx]

        condition = "WET" if row.get("Rainfall", 0) > 0 else "DRY"

        self.current_weather = {
        "track_temp": round(row.get("TrackTemp", 0), 1),
        "air_temp": round(row.get("AirTemp", 0), 1),
        "humidity": int(row.get("Humidity", 0)),
        "wind": round(row.get("WindSpeed", 0), 1),
        "condition": condition
    }


    
