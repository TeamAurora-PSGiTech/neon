

def compute_vl_vr(v, w, L=1.0):
    """
    Compute left and right wheel velocities.

    v : linear velocity
    w : angular velocity
    L : distance between wheels (wheelbase)

    returns: (VL, VR)
    """
    VL = v - (w * L / 2)
    VR = v + (w * L / 2)   
    return VL, VR



def forward(v):
    """Move straight forward"""
    return compute_vl_vr(abs(v), 0.0)


def backward(v):
    """Move straight backward"""
    return compute_vl_vr(-abs(v), 0.0)


def radial_right(v, w):
    """Move forward while turning right (smooth curve)"""
    return compute_vl_vr(abs(v), -abs(w))


def radial_left(v, w):
    """Move forward while turning left (smooth curve)"""
    return compute_vl_vr(abs(v), abs(w))


def turn_90_right(w):
    """Rotate right in place (spot turn)"""
    return compute_vl_vr(0.0, -abs(w))


def turn_90_left(w):
    """Rotate left in place (spot turn)"""
    return compute_vl_vr(0.0, abs(w))


def stop():
    """Stop the robot"""
    return (0.0, 0.0)

