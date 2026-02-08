import arcade
import math

# ================= WINDOW =================
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_TITLE = "F1 Telemetry Replay"

# ================= TRACK STYLE =================
TRACK_COLOR = arcade.color.LIGHT_GRAY
TRACK_WIDTH = 8

START_FINISH_INDEX = 0  # first telemetry point

# ================= DRIVER COLORS =================
DRIVER_COLORS = {
    "16": arcade.color.RED,
    "55": arcade.color.YELLOW,
    "1": arcade.color.BLUE,
}


class TrackView(arcade.Window):
    def __init__(self, drivers_data):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

        self.drivers_data = drivers_data
        self.driver_indices = {driver: 0 for driver in drivers_data.keys()}
        self.speed_multiplier = 1.0
        self.paused = False

        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()

        # ================= DRAW TRACK =================
        first_driver_df = next(iter(self.drivers_data.values()))

        for i in range(len(first_driver_df) - 1):
            x1 = first_driver_df.iloc[i]["screen_x"]
            y1 = first_driver_df.iloc[i]["screen_y"]
            x2 = first_driver_df.iloc[i+1]["screen_x"]
            y2 = first_driver_df.iloc[i+1]["screen_y"]

            arcade.draw_line(
                x1, y1,
                x2, y2,
                TRACK_COLOR,
                TRACK_WIDTH
            )

        # ================= START / FINISH LINE =================
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

            LINE_HALF = 10

            arcade.draw_line(
                sf_x1 + px * LINE_HALF,
                sf_y1 + py * LINE_HALF,
                sf_x1 - px * LINE_HALF,
                sf_y1 - py * LINE_HALF,
                arcade.color.WHITE,
                3
            )

        # ================= DRAW CARS =================
        for driver, df in self.drivers_data.items():
            idx = self.driver_indices[driver]

            x = df.iloc[idx]["screen_x"]
            y = df.iloc[idx]["screen_y"]

            color = DRIVER_COLORS.get(driver, arcade.color.WHITE)

            # Car body
            arcade.draw_circle_filled(x, y, 6, color)

            # Thin outline so car does NOT merge with track
            arcade.draw_circle_outline(
                x, y,
                6,
                arcade.color.BLACK,
                2
            )

        # ================= HUD =================
        arcade.draw_text(
            f"Speed {self.speed_multiplier:.2f}x",
            20,
            WINDOW_HEIGHT - 30,
            arcade.color.WHITE,
            14
        )

        if self.paused:
            arcade.draw_text(
                "PAUSED",
                WINDOW_WIDTH // 2 - 35,
                WINDOW_HEIGHT - 35,
                arcade.color.WHITE,
                14
            )

    def on_update(self, delta_time):
        if self.paused:
            return

        for driver, df in self.drivers_data.items():
            idx = self.driver_indices[driver]
            idx += self.speed_multiplier

            if idx >= len(df):
                idx = 0

            self.driver_indices[driver] = int(idx)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.paused = not self.paused

        elif key == arcade.key.UP:
            self.speed_multiplier = min(self.speed_multiplier + 0.25, 10)

        elif key == arcade.key.DOWN:
            self.speed_multiplier = max(self.speed_multiplier - 0.25, 0.25)
