import arcade
import math

# ================= WINDOW =================
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_TITLE = "F1 Telemetry Replay"

# ================= TRACK STYLE =================
TRACK_BASE_COLOR = arcade.color.DARK_SLATE_GRAY
TRACK_LINE_COLOR = arcade.color.LIGHT_GRAY

TRACK_BASE_WIDTH = 10
TRACK_LINE_WIDTH = 4

START_FINISH_INDEX = 0

# ================= DRIVER COLORS =================
DRIVER_COLORS = {
    "16": arcade.color.RED,        # Leclerc
    "55": arcade.color.YELLOW,     # Sainz
    "1": arcade.color.BLUE,        # Verstappen
}


class TrackView(arcade.Window):
    def __init__(self, drivers_data):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

        self.drivers_data = drivers_data
        self.driver_indices = {driver: 0 for driver in drivers_data.keys()}
        self.speed_multiplier = 1.0
        self.paused = False

        # ===== TIMER =====
        self.elapsed_time = 0.0  # seconds

        arcade.set_background_color(arcade.color.BLACK)

    # ================= TIME FORMAT =================
    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:06.3f}"

    # ================= LEADERBOARD SORT =================
    def get_leaderboard(self):
        """
        Sort drivers by progress (higher index = ahead)
        """
        return sorted(
            self.driver_indices.items(),
            key=lambda item: item[1],
            reverse=True
        )

    def on_draw(self):
        self.clear()

        first_driver_df = next(iter(self.drivers_data.values()))

        # ================= TRACK BASE =================
        for i in range(len(first_driver_df) - 1):
            x1 = first_driver_df.iloc[i]["screen_x"]
            y1 = first_driver_df.iloc[i]["screen_y"]
            x2 = first_driver_df.iloc[i + 1]["screen_x"]
            y2 = first_driver_df.iloc[i + 1]["screen_y"]

            arcade.draw_line(
                x1, y1, x2, y2,
                TRACK_BASE_COLOR,
                TRACK_BASE_WIDTH
            )

        # ================= RACING LINE =================
        for i in range(0, len(first_driver_df) - 1, 2):
            x1 = first_driver_df.iloc[i]["screen_x"]
            y1 = first_driver_df.iloc[i]["screen_y"]
            x2 = first_driver_df.iloc[i + 1]["screen_x"]
            y2 = first_driver_df.iloc[i + 1]["screen_y"]

            arcade.draw_line(
                x1, y1, x2, y2,
                TRACK_LINE_COLOR,
                TRACK_LINE_WIDTH
            )

        # ================= START / FINISH =================
        sf_x1 = first_driver_df.iloc[START_FINISH_INDEX]["screen_x"]
        sf_y1 = first_driver_df.iloc[START_FINISH_INDEX]["screen_y"]
        sf_x2 = first_driver_df.iloc[START_FINISH_INDEX + 1]["screen_x"]
        sf_y2 = first_driver_df.iloc[START_FINISH_INDEX + 1]["screen_y"]

        dx = sf_x2 - sf_x1
        dy = sf_y2 - sf_y1
        length = math.sqrt(dx * dx + dy * dy)

        if length != 0:
            px = -dy / length
            py = dx / length
            half = 14

            arcade.draw_line(
                sf_x1 + px * half, sf_y1 + py * half,
                sf_x1 - px * half, sf_y1 - py * half,
                arcade.color.BLACK, 6
            )

            arcade.draw_line(
                sf_x1 + px * half, sf_y1 + py * half,
                sf_x1 - px * half, sf_y1 - py * half,
                arcade.color.WHITE, 3
            )

        # ================= DRAW CARS =================
        for driver, df in self.drivers_data.items():
            idx = self.driver_indices[driver]
            x = df.iloc[idx]["screen_x"]
            y = df.iloc[idx]["screen_y"]

            color = DRIVER_COLORS.get(driver, arcade.color.WHITE)

            arcade.draw_circle_outline(x, y, 7, arcade.color.BLACK, 2)
            arcade.draw_circle_filled(x, y, 5, color)

        # ================= HUD (TOP-LEFT) =================
        arcade.draw_text(
            f"Speed  {self.speed_multiplier:.2f}x",
            20,
            WINDOW_HEIGHT - 32,
            arcade.color.WHITE,
            15,
            bold=True
        )

        # ================= TIMER (TOP-RIGHT) =================
        time_text = self.format_time(self.elapsed_time)
        arcade.draw_text(
            f"Time  {time_text}",
            WINDOW_WIDTH - 230,
            WINDOW_HEIGHT - 32,
            arcade.color.WHITE,
            15,
            bold=True
        )

        # ================= LEADERBOARD (BOTTOM-RIGHT) =================
        leaderboard = self.get_leaderboard()

        start_x = WINDOW_WIDTH - 230
        start_y = 220           # distance from bottom
        line_height = 18

        arcade.draw_text(
            "Leaderboard",
            start_x,
            start_y + (len(leaderboard) + 1) * line_height,
            arcade.color.WHITE,
            14,
            bold=True
        )

        for pos, (driver, _) in enumerate(leaderboard, start=1):
            color = DRIVER_COLORS.get(driver, arcade.color.WHITE)

            arcade.draw_text(
                f"{pos}. Driver {driver}",
                start_x,
                start_y + (len(leaderboard) - pos) * line_height,
                color,
                13
            )

        if self.paused:
            arcade.draw_text(
                "PAUSED",
                WINDOW_WIDTH // 2 - 38,
                WINDOW_HEIGHT - 38,
                arcade.color.WHITE,
                16,
                bold=True
            )

    def on_update(self, delta_time):
        if self.paused:
            return

        # ===== TIMER =====
        self.elapsed_time += delta_time * self.speed_multiplier

        for driver, df in self.drivers_data.items():
            idx = self.driver_indices[driver]
            idx += self.speed_multiplier

            if idx >= len(df):
                idx = 0
                self.elapsed_time = 0.0

            self.driver_indices[driver] = int(idx)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.paused = not self.paused

        elif key == arcade.key.UP:
            self.speed_multiplier = min(self.speed_multiplier + 0.25, 10)

        elif key == arcade.key.DOWN:
            self.speed_multiplier = max(self.speed_multiplier - 0.25, 0.25)
