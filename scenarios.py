# scenarios.py
#
# Sign convention:
# lane_offset_m:
#   negative = vehicle is left of lane center
#   positive = vehicle is right of lane center
#
# heading_error_deg:
#   negative = vehicle heading points left of desired direction
#   positive = vehicle heading points right of desired direction

scenarios = [
    {
        "name": "Clear Path, Centered",
        "inputs": {
            "obstacle_distance_m": 999.0,
            "lane_offset_m": 0.0,
            "heading_error_deg": 0.0,
            "speed_mps": 2.0,
            "e_stop": False,
            "left_clear": True,
            "right_clear": True,
            "sensor_valid": True
        }
    },
    {
        "name": "Close Obstacle Ahead, No Safe Side",
        "inputs": {
            "obstacle_distance_m": 0.8,
            "lane_offset_m": 0.0,
            "heading_error_deg": 0.0,
            "speed_mps": 2.5,
            "e_stop": False,
            "left_clear": False,
            "right_clear": False,
            "sensor_valid": True
        }
    },
    {
        "name": "Obstacle Ahead, Left Clear",
        "inputs": {
            "obstacle_distance_m": 1.8,
            "lane_offset_m": 0.0,
            "heading_error_deg": 0.0,
            "speed_mps": 3.0,
            "e_stop": False,
            "left_clear": True,
            "right_clear": False,
            "sensor_valid": True
        }
    },
    {
        "name": "Obstacle Ahead, Right Clear",
        "inputs": {
            "obstacle_distance_m": 1.8,
            "lane_offset_m": 0.0,
            "heading_error_deg": 0.0,
            "speed_mps": 3.0,
            "e_stop": False,
            "left_clear": False,
            "right_clear": True,
            "sensor_valid": True
        }
    },
    {
        "name": "Large Heading Error at Speed",
        "inputs": {
            "obstacle_distance_m": 999.0,
            "lane_offset_m": 0.1,
            "heading_error_deg": 22.0,
            "speed_mps": 4.5,
            "e_stop": False,
            "left_clear": True,
            "right_clear": True,
            "sensor_valid": True
        }
    },
    {
        "name": "Emergency Stop Active",
        "inputs": {
            "obstacle_distance_m": 2.0,
            "lane_offset_m": -0.4,
            "heading_error_deg": -12.0,
            "speed_mps": 3.0,
            "e_stop": True,
            "left_clear": True,
            "right_clear": False,
            "sensor_valid": True
        }
    },
    {
        "name": "Obstacle Plus Heading Conflict",
        "inputs": {
            "obstacle_distance_m": 1.7,
            "lane_offset_m": -0.2,
            "heading_error_deg": 18.0,
            "speed_mps": 3.5,
            "e_stop": False,
            "left_clear": False,
            "right_clear": True,
            "sensor_valid": True
        }
    },
    {
        "name": "Mild Drift, No Obstacle",
        "inputs": {
            "obstacle_distance_m": 999.0,
            "lane_offset_m": 0.25,
            "heading_error_deg": 5.0,
            "speed_mps": 2.2,
            "e_stop": False,
            "left_clear": True,
            "right_clear": True,
            "sensor_valid": True
        }
    }
]
