import arcade

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_TITLE = "F1 Telemetry Replay"


class TrackView(arcade.Window):
    def __init__(self, telemetry_df):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

        self.telemetry_df = telemetry_df
        self.current_index = 0
        self.speed_multiplier = 1.0
        self.paused = False

        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()

        # Draw track
        for i in range(len(self.telemetry_df) - 1):
            x1 = self.telemetry_df.iloc[i]["screen_x"]
            y1 = self.telemetry_df.iloc[i]["screen_y"]
            x2 = self.telemetry_df.iloc[i + 1]["screen_x"]
            y2 = self.telemetry_df.iloc[i + 1]["screen_y"]

            arcade.draw_line(
                x1, y1,
                x2, y2,
                arcade.color.DARK_GRAY,
                2
            )

        # Draw car
        car_x = self.telemetry_df.iloc[int(self.current_index)]["screen_x"]
        car_y = self.telemetry_df.iloc[int(self.current_index)]["screen_y"]

        arcade.draw_circle_filled(
            car_x,
            car_y,
            6,
            arcade.color.RED
        )

        # Speed HUD (always visible)
        arcade.draw_text(
            f"Speed: {self.speed_multiplier:.2f}x",
            20,
            WINDOW_HEIGHT - 30,
            arcade.color.WHITE,
            14
        )

        # Pause indicator
        if self.paused:
            arcade.draw_text(
                "PAUSED",
                WINDOW_WIDTH // 2 - 40,
                WINDOW_HEIGHT - 40,
                arcade.color.YELLOW,
                16
            )

    def on_update(self, delta_time):
        if self.paused:
            return

        self.current_index += self.speed_multiplier

        if self.current_index >= len(self.telemetry_df):
            self.current_index = 0

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.paused = not self.paused

        elif key == arcade.key.UP:
            self.speed_multiplier += 0.25
            if self.speed_multiplier > 10:
                self.speed_multiplier = 10

        elif key == arcade.key.DOWN:
            self.speed_multiplier -= 0.25
            if self.speed_multiplier < 0.25:
                self.speed_multiplier = 0.25
