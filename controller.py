# Improve controller safety logic
# controller.py
#
# Faulty decision logic for the 2026 Autonomous Newbie Project.
# Recruits will mainly modify this file.
#
# Sign convention:
# lane_offset_m:
#   negative = vehicle is left of lane center
#   positive = vehicle is right of lane center
#
# heading_error_deg:
#   negative = vehicle heading points left of desired direction
#   positive = vehicle heading points right of desired direction
#
# Steering output semantics:
# "LEFT" means command the vehicle to steer / move left.
# "RIGHT" means command the vehicle to steer / move right.
# Therefore:
# - positive lane_offset_m means vehicle is right of center, so LEFT is corrective
# - positive heading_error_deg means vehicle points right of desired direction, so LEFT is corrective




# my updated logic:
# 1. If sensor invalid --> STOP
# 2. If e_stop --> STOP
# 3. If obstacle dangerously close:
#       - if no clear path --> STOP
#       - if one side clear --> steer there + SLOW
#       - if both clear --> choose safer correction + SLOW
# 4. If obstacle moderately close:
#       - be cautious + SLOW
# 5. If lane/heading error is large:
#       - correct + SLOW
# 6. If lane/heading error is mild:
#       - correct + maybe ACCELERATE/SLOW depending speed
# 7. Else:
#       - STRAIGHT + ACCELERATE


VALID_STEERING = {"LEFT", "RIGHT", "STRAIGHT"}
VALID_SPEED = {"ACCELERATE", "SLOW", "STOP"}


def controller(
    obstacle_distance_m,
    lane_offset_m,
    heading_error_deg,
    speed_mps,
    e_stop,
    left_clear,
    right_clear,
    sensor_valid
):
    """
    Returns:
        (steering, speed_action)

        steering:
            "LEFT", "RIGHT", "STRAIGHT"

        speed_action:
            "ACCELERATE", "SLOW", "STOP"
    """

    DANGER_OBSTACLE_M = 1.0
    CAUTION_OBSTACLE_M = 2.0

    MILD_HEADING_DEG = 3.0
    LARGE_HEADING_DEG = 15.0

    MILD_OFFSET_M = 0.15
    LARGE_OFFSET_M = 0.40

    HIGH_SPEED_MPS = 3.0

    # P controller constant
    Kp = 1.0

    ERROR_DEADBAND = 3.0
    LARGE_CONTROL_OUTPUT = 15.0

    # combine heading error and lane offset into one error score
    error_score = heading_error_deg + (lane_offset_m * 20)

    # SAFETY CHECKS
    if not sensor_valid:
        return "STRAIGHT", "STOP"

    if e_stop:
        return "STRAIGHT", "STOP"

    # OBSTACLE CHECKS
    if obstacle_distance_m <= DANGER_OBSTACLE_M:

        if not left_clear and not right_clear:
            return "STRAIGHT", "STOP"

        elif right_clear and not left_clear:
            return "RIGHT", "SLOW"

        elif left_clear and not right_clear:
            return "LEFT", "SLOW"

        elif left_clear and right_clear:
            if error_score > ERROR_DEADBAND:
                return "LEFT", "SLOW"
            elif error_score < -ERROR_DEADBAND:
                return "RIGHT", "SLOW"
            else:
                return "STRAIGHT", "STOP"

    elif obstacle_distance_m <= CAUTION_OBSTACLE_M:

        if not left_clear and not right_clear:
            return "STRAIGHT", "STOP"

        elif right_clear and not left_clear:
            return "RIGHT", "SLOW"

        elif left_clear and not right_clear:
            return "LEFT", "SLOW"

        elif left_clear and right_clear:
            if error_score > ERROR_DEADBAND:
                return "LEFT", "SLOW"
            elif error_score < -ERROR_DEADBAND:
                return "RIGHT", "SLOW"
            else:
                return "STRAIGHT", "SLOW"

    # P CONTROLLER
    control_output = (Kp * error_score)

    if control_output > LARGE_CONTROL_OUTPUT:
        return "LEFT", "SLOW"

    elif control_output < -LARGE_CONTROL_OUTPUT:
        return "RIGHT", "SLOW"

    elif control_output > ERROR_DEADBAND:
        if speed_mps >= HIGH_SPEED_MPS:
            return "LEFT", "SLOW"
        else:
            return "LEFT", "ACCELERATE"

    elif control_output < -ERROR_DEADBAND:
        if speed_mps >= HIGH_SPEED_MPS:
            return "RIGHT", "SLOW"
        else:
            return "RIGHT", "ACCELERATE"

    else:
        return "STRAIGHT", "ACCELERATE"

# SITUATION:            Expected steering:       Expected speed action:
#sensor invalid              STRAIGHT                STOP
#e-stop activated            STRAIGHT                STOP
#obstacle very close, left clear, right blocked     LEFT                    SLOW
#obstacle very close, right clear, left blocked     RIGHT                   SLOW
#obstacle very close, both clear, heading/lane error suggests left correction     LEFT     SLOW
#obstacle very close, both clear, heading/lane error suggests right correction    RIGHT    SLOW
#obstacle very close, both clear, no significant heading/lane           STRAIGHT                STOP
#obstacle moderately close, left clear, right blocked     LEFT                    SLOW
#obstacle moderately close, right clear, left blocked     RIGHT                   SLOW
#obstacle moderately close, both clear, heading/lane error suggests left correction     LEFT
