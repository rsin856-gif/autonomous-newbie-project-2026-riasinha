# visualize.py

import tkinter as tk
import math
import os

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from scenarios import scenarios
from controller import controller


WINDOW_W = 980
WINDOW_H = 640

CANVAS_W = 640
CANVAS_H = 540

ROAD_LEFT = 180
ROAD_RIGHT = 460
ROAD_TOP = 0
ROAD_BOTTOM = 500
ROAD_CENTER_X = (ROAD_LEFT + ROAD_RIGHT) // 2

ROAD_WIDTH_M = 2.0
PIXELS_PER_METER_X = (ROAD_RIGHT - ROAD_LEFT) / ROAD_WIDTH_M

SIDE_ROAD_WIDTH_M = 0.75
SIDE_ROAD_WIDTH_PX = SIDE_ROAD_WIDTH_M * PIXELS_PER_METER_X

MID_SIDE_ROAD_TOP = 210
MID_SIDE_ROAD_BOTTOM = 320
TOP_SIDE_ROAD_BOTTOM = MID_SIDE_ROAD_TOP

VEHICLE_BASE_Y = 420
VEHICLE_HIT_RADIUS = 18

FRAME_DELAY_MS = 35
MOTION_PIXELS_PER_MPS = 55.0
MAX_ANIMATION_FRAMES = 140

TURN_RATE_LEFT_DEG_PER_S = -35.0
TURN_RATE_RIGHT_DEG_PER_S = 35.0

STOP_DECEL_MPS2 = 4.0
SLOW_APPROACH_MPS2 = 2.0
ACCEL_MPS2 = 2.5

SLOW_TARGET_MPS = 1.5
ACCEL_MIN_TARGET_MPS = 4.5
ACCEL_OFFSET_TARGET_MPS = 1.0

VEHICLE_IMAGE_WIDTH = 30
VEHICLE_IMAGE_HEIGHT = 40

# If the vehicle sprite appears to face the wrong direction, change this.
# Common values to try are 0, 90, 180, -90.
VEHICLE_IMAGE_ROTATION_OFFSET_DEG = 0


class VisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Autonomous Newbie Project Visualizer")

        self.index = 0
        self.animating = False
        self.after_id = None
        self.frame_i = 0

        self.vehicle_x = ROAD_CENTER_X
        self.vehicle_y = VEHICLE_BASE_Y
        self.vehicle_heading_deg = 0.0
        self.vehicle_speed_mps = 0.0
        self.initial_speed_mps = 0.0

        self.command_steering = "STRAIGHT"
        self.command_speed_action = "SLOW"

        self.crashed = False
        self.crash_reason = ""
        self.explosion_x = None
        self.explosion_y = None

        self.asset_dir = os.path.join(
            os.path.dirname(__file__), "visualize_assets")

        self.bg_images = {}
        self.obstacle_image = None
        self.explosion_image = None

        self.vehicle_pil_base = None
        self.vehicle_rotated_cache = {}

        self.load_visual_assets()

        self.title_label = tk.Label(
            root,
            text="Autonomous Newbie Project Visualizer",
            font=("Arial", 16, "bold"),
            pady=8,
        )
        self.title_label.pack()

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill="both", expand=True, padx=12, pady=8)

        self.canvas = tk.Canvas(
            self.main_frame,
            width=CANVAS_W,
            height=CANVAS_H,
            bg="white",
            highlightthickness=1,
            highlightbackground="black",
        )
        self.canvas.pack(side="left", padx=(0, 14))

        self.info_frame = tk.Frame(self.main_frame, width=300)
        self.info_frame.pack(side="left", fill="y")

        self.scenario_name_label = tk.Label(
            self.info_frame,
            text="",
            font=("Arial", 13, "bold"),
            anchor="w",
            justify="left",
            wraplength=290,
        )
        self.scenario_name_label.pack(anchor="w", pady=(0, 10))

        self.inputs_title = tk.Label(
            self.info_frame,
            text="Inputs",
            font=("Arial", 11, "bold"),
            anchor="w",
        )
        self.inputs_title.pack(anchor="w")

        self.inputs_label = tk.Label(
            self.info_frame,
            text="",
            font=("Courier New", 10),
            anchor="w",
            justify="left",
            wraplength=290,
        )
        self.inputs_label.pack(anchor="w", pady=(4, 12))

        self.output_title = tk.Label(
            self.info_frame,
            text="Controller Output",
            font=("Arial", 11, "bold"),
            anchor="w",
        )
        self.output_title.pack(anchor="w")

        self.output_label = tk.Label(
            self.info_frame,
            text="",
            font=("Courier New", 10),
            anchor="w",
            justify="left",
            wraplength=290,
        )
        self.output_label.pack(anchor="w", pady=(4, 12))

        self.status_title = tk.Label(
            self.info_frame,
            text="Visualizer Status",
            font=("Arial", 11, "bold"),
            anchor="w",
        )
        self.status_title.pack(anchor="w")

        self.status_label = tk.Label(
            self.info_frame,
            text="Ready",
            font=("Courier New", 10),
            anchor="w",
            justify="left",
            wraplength=290,
        )
        self.status_label.pack(anchor="w", pady=(4, 12))

        self.note_label = tk.Label(
            self.info_frame,
            text=(
                "Main road width = 2.0 m.\n"
                "Side roads = 0.75 m each.\n\n"
                "Obstacle collision and road-boundary collision both crash.\n"
                "Playback follows controller outputs"
            ),
            font=("Arial", 9),
            fg="gray30",
            justify="left",
            wraplength=290,
        )
        self.note_label.pack(anchor="w", pady=(10, 0))

        self.controls = tk.Frame(root)
        self.controls.pack(pady=8)

        self.prev_button = tk.Button(
            self.controls,
            text="Previous",
            width=12,
            command=self.prev_scenario
        )
        self.prev_button.pack(side="left", padx=6)

        self.play_button = tk.Button(
            self.controls,
            text="Play",
            width=12,
            command=self.play_scenario
        )
        self.play_button.pack(side="left", padx=6)

        self.reset_button = tk.Button(
            self.controls,
            text="Reset",
            width=12,
            command=self.reset_current
        )
        self.reset_button.pack(side="left", padx=6)

        self.next_button = tk.Button(
            self.controls,
            text="Next",
            width=12,
            command=self.next_scenario
        )
        self.next_button.pack(side="left", padx=6)

        self.root.bind("<Left>", lambda event: self.prev_scenario())
        self.root.bind("<Right>", lambda event: self.next_scenario())
        self.root.bind("<space>", lambda event: self.play_scenario())
        self.root.bind("r", lambda event: self.reset_current())

        self.reset_vehicle_state()
        self.refresh_view()

    def load_visual_assets(self):
        bg_files = {
            "bg": "bg.png",
            "bg_left": "bg_left.png",
            "bg_right": "bg_right.png",
            "bg_leftright": "bg_leftright.png",
        }

        for key, filename in bg_files.items():
            path = os.path.join(self.asset_dir, filename)
            try:
                self.bg_images[key] = tk.PhotoImage(file=path)
            except tk.TclError:
                self.bg_images[key] = None

        obstacle_path = os.path.join(self.asset_dir, "obstacle.png")
        explosion_path = os.path.join(self.asset_dir, "explosion.png")

        try:
            self.obstacle_image = tk.PhotoImage(file=obstacle_path)
        except tk.TclError:
            self.obstacle_image = None

        try:
            self.explosion_image = tk.PhotoImage(file=explosion_path)
        except tk.TclError:
            self.explosion_image = None

        if PIL_AVAILABLE:
            vehicle_path = os.path.join(self.asset_dir, "vehicle.png")
            try:
                vehicle_img = Image.open(vehicle_path).convert("RGBA")
                self.vehicle_pil_base = vehicle_img.resize(
                    (VEHICLE_IMAGE_WIDTH, VEHICLE_IMAGE_HEIGHT),
                    Image.Resampling.LANCZOS
                )
            except Exception:
                self.vehicle_pil_base = None

    def get_background_key(self, inputs):
        left_clear = inputs["left_clear"]
        right_clear = inputs["right_clear"]

        if left_clear and right_clear:
            return "bg_leftright"
        elif left_clear:
            return "bg_left"
        elif right_clear:
            return "bg_right"
        else:
            return "bg"

    def current_scenario(self):
        return scenarios[self.index]

    def run_controller_for_current_scenario(self):
        scenario = self.current_scenario()
        inputs = scenario["inputs"]

        steering, speed_action = controller(
            inputs["obstacle_distance_m"],
            inputs["lane_offset_m"],
            inputs["heading_error_deg"],
            inputs["speed_mps"],
            inputs["e_stop"],
            inputs["left_clear"],
            inputs["right_clear"],
            inputs["sensor_valid"]
        )

        return steering, speed_action

    def lane_offset_to_x(self, lane_offset_m):
        return ROAD_CENTER_X + lane_offset_m * PIXELS_PER_METER_X

    def x_to_lane_offset_m(self, x):
        return (x - ROAD_CENTER_X) / PIXELS_PER_METER_X

    def obstacle_y_from_distance(self, distance_m):
        if distance_m >= 999.0:
            return None

        distance_clamped = max(0.5, min(distance_m, 3.0))

        nearest_y = 360.0
        farthest_y = 140.0

        t = (distance_clamped - 0.5) / (3.0 - 0.5)
        return nearest_y + t * (farthest_y - nearest_y)

    def obstacle_rect_from_inputs(self, inputs):
        obstacle_y = self.obstacle_y_from_distance(
            inputs["obstacle_distance_m"])
        if obstacle_y is None:
            return None

        return (270, obstacle_y - 20, 370, obstacle_y + 20)

    def vehicle_hits_rect(self, cx, cy, radius, rect):
        x1, y1, x2, y2 = rect

        closest_x = min(max(cx, x1), x2)
        closest_y = min(max(cy, y1), y2)

        dx = cx - closest_x
        dy = cy - closest_y

        return (dx * dx + dy * dy) <= (radius * radius)

    def distance_point_to_segment(self, px, py, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1

        if dx == 0 and dy == 0:
            return math.hypot(px - x1, py - y1)

        t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
        t = max(0.0, min(1.0, t))

        closest_x = x1 + t * dx
        closest_y = y1 + t * dy

        return math.hypot(px - closest_x, py - closest_y)

    def vehicle_hits_segment(self, cx, cy, radius, segment):
        x1, y1, x2, y2 = segment
        dist = self.distance_point_to_segment(cx, cy, x1, y1, x2, y2)
        return dist <= radius

    def get_road_obstacle_segments(self):
        segments = []

        segments.append((ROAD_LEFT, ROAD_BOTTOM, ROAD_RIGHT, ROAD_BOTTOM))
        segments.append(
            (ROAD_LEFT, MID_SIDE_ROAD_BOTTOM, ROAD_LEFT, ROAD_BOTTOM))
        segments.append(
            (ROAD_RIGHT, MID_SIDE_ROAD_BOTTOM, ROAD_RIGHT, ROAD_BOTTOM))

        segments.append(
            (0, TOP_SIDE_ROAD_BOTTOM, ROAD_LEFT, TOP_SIDE_ROAD_BOTTOM))
        segments.append((ROAD_RIGHT, TOP_SIDE_ROAD_BOTTOM,
                        CANVAS_W, TOP_SIDE_ROAD_BOTTOM))

        segments.append((0, MID_SIDE_ROAD_TOP, ROAD_LEFT, MID_SIDE_ROAD_TOP))
        segments.append(
            (0, MID_SIDE_ROAD_BOTTOM, ROAD_LEFT, MID_SIDE_ROAD_BOTTOM))

        segments.append((ROAD_RIGHT, MID_SIDE_ROAD_TOP,
                        CANVAS_W, MID_SIDE_ROAD_TOP))
        segments.append((ROAD_RIGHT, MID_SIDE_ROAD_BOTTOM,
                        CANVAS_W, MID_SIDE_ROAD_BOTTOM))

        return segments

    def check_obstacle_collision(self):
        inputs = self.current_scenario()["inputs"]
        rect = self.obstacle_rect_from_inputs(inputs)
        if rect is None:
            return False

        return self.vehicle_hits_rect(
            self.vehicle_x,
            self.vehicle_y,
            VEHICLE_HIT_RADIUS,
            rect
        )

    def check_road_boundary_collision(self):
        for segment in self.get_road_obstacle_segments():
            if self.vehicle_hits_segment(
                self.vehicle_x,
                self.vehicle_y,
                VEHICLE_HIT_RADIUS,
                segment
            ):
                return True
        return False

    def rotated_points(self, cx, cy, points, deg):
        rad = math.radians(deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)

        rotated = []
        for px, py in points:
            rx = px * cos_a - py * sin_a
            ry = px * sin_a + py * cos_a
            rotated.extend([cx + rx, cy + ry])

        return rotated

    def get_rotated_vehicle_image(self, heading_deg):
        if self.vehicle_pil_base is None:
            return None

        rounded_deg = int(
            round(heading_deg + VEHICLE_IMAGE_ROTATION_OFFSET_DEG))

        if rounded_deg not in self.vehicle_rotated_cache:
            rotated = self.vehicle_pil_base.rotate(
                -rounded_deg,
                expand=True,
                resample=Image.Resampling.BICUBIC
            )
            self.vehicle_rotated_cache[rounded_deg] = ImageTk.PhotoImage(
                rotated)

        return self.vehicle_rotated_cache[rounded_deg]

    def reset_vehicle_state(self):
        scenario = self.current_scenario()
        inputs = scenario["inputs"]

        self.vehicle_x = self.lane_offset_to_x(inputs["lane_offset_m"])
        self.vehicle_y = VEHICLE_BASE_Y
        self.vehicle_heading_deg = inputs["heading_error_deg"]
        self.vehicle_speed_mps = inputs["speed_mps"]
        self.initial_speed_mps = inputs["speed_mps"]

        self.command_steering, self.command_speed_action = self.run_controller_for_current_scenario()

        self.frame_i = 0

        self.crashed = False
        self.crash_reason = ""
        self.explosion_x = None
        self.explosion_y = None

        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.animating = False

    def reset_current(self):
        self.reset_vehicle_state()
        self.status_label.config(text="Reset current scenario")
        self.refresh_view()

    def prev_scenario(self):
        if self.animating:
            return

        self.index = (self.index - 1) % len(scenarios)
        self.reset_vehicle_state()
        self.status_label.config(text="Moved to previous scenario")
        self.refresh_view()

    def next_scenario(self):
        if self.animating:
            return

        self.index = (self.index + 1) % len(scenarios)
        self.reset_vehicle_state()
        self.status_label.config(text="Moved to next scenario")
        self.refresh_view()

    def play_scenario(self):
        if self.animating:
            return

        self.reset_vehicle_state()
        self.animating = True
        self.status_label.config(
            text=(
                f"Animating controller output: "
                f"{self.command_steering} + {self.command_speed_action}"
            )
        )
        self.animate_step()

    def apply_controller_speed_action(self, dt):
        if self.command_speed_action == "STOP":
            self.vehicle_speed_mps = max(
                0.0,
                self.vehicle_speed_mps - STOP_DECEL_MPS2 * dt
            )

        elif self.command_speed_action == "SLOW":
            if self.vehicle_speed_mps > SLOW_TARGET_MPS:
                self.vehicle_speed_mps = max(
                    SLOW_TARGET_MPS,
                    self.vehicle_speed_mps - SLOW_APPROACH_MPS2 * dt
                )
            else:
                self.vehicle_speed_mps = min(
                    SLOW_TARGET_MPS,
                    self.vehicle_speed_mps + SLOW_APPROACH_MPS2 * dt
                )

        elif self.command_speed_action == "ACCELERATE":
            accel_target = max(
                ACCEL_MIN_TARGET_MPS,
                self.initial_speed_mps + ACCEL_OFFSET_TARGET_MPS
            )
            self.vehicle_speed_mps = min(
                accel_target,
                self.vehicle_speed_mps + ACCEL_MPS2 * dt
            )

    def apply_controller_steering(self, dt):
        if self.command_steering == "LEFT":
            self.vehicle_heading_deg += TURN_RATE_LEFT_DEG_PER_S * dt

        elif self.command_steering == "RIGHT":
            self.vehicle_heading_deg += TURN_RATE_RIGHT_DEG_PER_S * dt

        if self.vehicle_heading_deg > 90.0:
            self.vehicle_heading_deg = 90.0
        elif self.vehicle_heading_deg < -90.0:
            self.vehicle_heading_deg = -90.0

    def animate_step(self):
        if not self.animating:
            return

        dt = FRAME_DELAY_MS / 1000.0
        self.frame_i += 1

        heading_locked = abs(self.vehicle_heading_deg) >= 90.0

        if not heading_locked:
            self.apply_controller_speed_action(dt)
            self.apply_controller_steering(dt)
        else:
            if self.vehicle_heading_deg > 0:
                self.vehicle_heading_deg = 90.0
            else:
                self.vehicle_heading_deg = -90.0

        distance_px = self.vehicle_speed_mps * MOTION_PIXELS_PER_MPS * dt
        heading_rad = math.radians(self.vehicle_heading_deg)

        dx = math.sin(heading_rad) * distance_px
        dy = -math.cos(heading_rad) * distance_px

        self.vehicle_x += dx
        self.vehicle_y += dy

        if self.check_obstacle_collision():
            self.animating = False
            self.crashed = True
            self.crash_reason = "Collided with obstacle"
            self.explosion_x = self.vehicle_x
            self.explosion_y = self.vehicle_y
            self.status_label.config(text="Collision with obstacle")
            self.refresh_view()
            return

        if self.check_road_boundary_collision():
            self.animating = False
            self.crashed = True
            self.crash_reason = "Hit road boundary"
            self.explosion_x = self.vehicle_x
            self.explosion_y = self.vehicle_y
            self.status_label.config(text="Collision with road boundary")
            self.refresh_view()
            return

        self.refresh_view()

        out_of_bounds = (
            self.vehicle_x < -40
            or self.vehicle_x > CANVAS_W + 40
            or self.vehicle_y < -40
            or self.vehicle_y > CANVAS_H + 40
        )

        stopped_from_command = (
            self.command_speed_action == "STOP"
            and self.vehicle_speed_mps <= 0.02
            and self.frame_i > 8
        )

        finished_by_length = self.frame_i >= MAX_ANIMATION_FRAMES

        if out_of_bounds or stopped_from_command or finished_by_length:
            self.animating = False
            self.after_id = None
            self.status_label.config(text="Playback complete")
            return

        self.after_id = self.root.after(FRAME_DELAY_MS, self.animate_step)

    def draw_road_network(self):
        road_fill = "#6f7175"
        road_outline = "black"

        self.canvas.create_rectangle(
            ROAD_LEFT, ROAD_TOP, ROAD_RIGHT, ROAD_BOTTOM,
            fill=road_fill,
            outline=road_outline,
            width=2
        )

        self.canvas.create_rectangle(
            0,
            ROAD_TOP,
            ROAD_LEFT,
            TOP_SIDE_ROAD_BOTTOM,
            fill=road_fill,
            outline=road_outline,
            width=2
        )

        self.canvas.create_rectangle(
            ROAD_RIGHT,
            ROAD_TOP,
            CANVAS_W,
            TOP_SIDE_ROAD_BOTTOM,
            fill=road_fill,
            outline=road_outline,
            width=2
        )

        self.canvas.create_rectangle(
            0,
            MID_SIDE_ROAD_TOP,
            ROAD_LEFT,
            MID_SIDE_ROAD_BOTTOM,
            fill=road_fill,
            outline=road_outline,
            width=2
        )

        self.canvas.create_rectangle(
            ROAD_RIGHT,
            MID_SIDE_ROAD_TOP,
            CANVAS_W,
            MID_SIDE_ROAD_BOTTOM,
            fill=road_fill,
            outline=road_outline,
            width=2
        )

        self.canvas.create_line(
            ROAD_CENTER_X, ROAD_TOP, ROAD_CENTER_X, ROAD_BOTTOM,
            fill="white",
            dash=(10, 10),
            width=2
        )

        self.canvas.create_text(
            ROAD_LEFT + 18,
            ROAD_BOTTOM + 18,
            text="-1.0 m",
            font=("Arial", 9)
        )
        self.canvas.create_text(
            ROAD_CENTER_X,
            ROAD_BOTTOM + 18,
            text="0.0 m",
            font=("Arial", 9, "bold")
        )
        self.canvas.create_text(
            ROAD_RIGHT - 18,
            ROAD_BOTTOM + 18,
            text="+1.0 m",
            font=("Arial", 9)
        )

    def draw_explosion_overlay(self, cx, cy):
        outer_r = 34
        inner_r = 16
        points = []

        for i in range(16):
            angle = (2.0 * math.pi * i) / 16.0
            radius = outer_r if i % 2 == 0 else inner_r
            px = cx + math.cos(angle) * radius
            py = cy + math.sin(angle) * radius
            points.extend([px, py])

        self.canvas.create_polygon(
            points,
            fill="#ffb347",
            outline="#d83a2e",
            width=3
        )
        self.canvas.create_text(
            cx,
            cy,
            text="X",
            font=("Arial", 22, "bold"),
            fill="#8b0000"
        )

    def draw_obstacle_visual(self, inputs):
        rect = self.obstacle_rect_from_inputs(inputs)
        if rect is None:
            return

        x1, y1, x2, y2 = rect
        obstacle_cx = (x1 + x2) / 2.0
        obstacle_cy = (y1 + y2) / 2.0

        if self.obstacle_image is not None:
            self.canvas.create_image(
                obstacle_cx,
                obstacle_cy,
                image=self.obstacle_image
            )
        else:
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill="#e2634f",
                outline="black",
                width=2
            )
            self.canvas.create_text(
                obstacle_cx,
                obstacle_cy,
                text=f"OBSTACLE\n{inputs['obstacle_distance_m']:.1f} m",
                font=("Arial", 9, "bold"),
                justify="center"
            )

    def draw_explosion_visual(self, cx, cy):
        if self.explosion_image is not None:
            self.canvas.create_image(
                cx,
                cy,
                image=self.explosion_image
            )
        else:
            self.draw_explosion_overlay(cx, cy)

    def draw_vehicle_visual(self):
        rotated_vehicle_img = self.get_rotated_vehicle_image(
            self.vehicle_heading_deg)

        if rotated_vehicle_img is not None:
            self.canvas.create_image(
                self.vehicle_x,
                self.vehicle_y,
                image=rotated_vehicle_img
            )
            return

        vehicle_shape = [
            (-15, 16),
            (15, 16),
            (0, -22),
        ]

        rotated_vehicle = self.rotated_points(
            self.vehicle_x,
            self.vehicle_y,
            vehicle_shape,
            self.vehicle_heading_deg
        )

        vehicle_fill = "#ffb3a8" if self.crashed else "#87ceeb"

        self.canvas.create_polygon(
            rotated_vehicle,
            fill=vehicle_fill,
            outline="black",
            width=2
        )

    def refresh_view(self):
        scenario = self.current_scenario()
        inputs = scenario["inputs"]
        steering, speed_action = self.run_controller_for_current_scenario()

        self.command_steering = steering
        self.command_speed_action = speed_action

        self.scenario_name_label.config(
            text=f"Scenario {self.index + 1}/{len(scenarios)}\n{scenario['name']}"
        )

        input_lines = []
        for key, value in inputs.items():
            input_lines.append(f"{key}: {value}")
        self.inputs_label.config(text="\n".join(input_lines))

        output_text = (
            f"steering:     {steering}\n"
            f"speed_action: {speed_action}"
        )
        self.output_label.config(text=output_text)

        self.draw_scene(inputs, steering, speed_action)

    def draw_scene(self, inputs, steering, speed_action):
        self.canvas.delete("all")

        bg_key = self.get_background_key(inputs)
        bg_image = self.bg_images.get(bg_key)

        if bg_image is not None:
            self.canvas.create_image(0, 0, anchor="nw", image=bg_image)
        else:
            self.canvas.create_rectangle(
                0, 0, CANVAS_W, CANVAS_H,
                fill="#dceccf",
                outline=""
            )
            self.draw_road_network()

        self.draw_obstacle_visual(inputs)
        self.draw_vehicle_visual()

        self.canvas.create_text(
            self.vehicle_x,
            self.vehicle_y + 34,
            text="Go-Kart",
            font=("Arial", 10, "bold")
        )

        live_offset_m = self.x_to_lane_offset_m(self.vehicle_x)

        vehicle_state_text = (
            f"heading: {self.vehicle_heading_deg:.1f} deg\n"
            f"offset:  {live_offset_m:.2f} m\n"
            f"speed:   {self.vehicle_speed_mps:.1f} m/s"
        )

        self.canvas.create_text(
            self.vehicle_x,
            self.vehicle_y + 64,
            text=vehicle_state_text,
            font=("Courier New", 9),
            justify="center"
        )

        if self.crashed and self.explosion_x is not None and self.explosion_y is not None:
            self.draw_explosion_visual(self.explosion_x, self.explosion_y)

        if self.crashed:
            banner_fill = "#f2b0a8"
            banner_text = f"FAILURE: {self.crash_reason}"
        else:
            if speed_action == "STOP":
                banner_fill = "#f4d46c"
            elif speed_action == "SLOW":
                banner_fill = "#eadf98"
            else:
                banner_fill = "#bce6bc"

            banner_text = f"Decision: {steering} + {speed_action}"

        self.canvas.create_rectangle(
            180, 510, 460, 535,
            fill=banner_fill,
            outline="black"
        )
        self.canvas.create_text(
            320, 522,
            text=banner_text,
            font=("Arial", 10, "bold")
        )


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry(f"{WINDOW_W}x{WINDOW_H}")
    app = VisualizerApp(root)
    root.mainloop()
