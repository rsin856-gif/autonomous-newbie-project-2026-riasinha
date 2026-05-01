# run_scenarios.py

from scenarios import scenarios
from controller import controller

summary = []

for scenario in scenarios:
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

    summary.append({
        "name": scenario["name"],
        "steering": steering,
        "speed_action": speed_action
    })

print("Summary:")
for item in summary:
    print(
        " ",
        item["name"] + ":",
        "steering =", item["steering"] + ",",
        "speed_action =", item["speed_action"]
    )
