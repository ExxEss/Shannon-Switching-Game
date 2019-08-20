from math import pi as pi
import math


def angle(v1, v2):
    dot = v1[0] * v2[0] + v1[1] * v2[1]
    det = v1[0] * v2[1] - v1[1] * v2[0]

    if det < 0:
        return 360 + math.atan2(det, dot) * 180 / pi
    else:
        return math.atan2(det, dot) * 180 / pi


