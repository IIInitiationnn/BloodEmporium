def close_proximity(a, b):
    a_x = a[0]
    a_y = a[1]
    b_x = b[0]
    b_y = b[1]
    return abs(a_x - b_x) < 20 and abs(a_y - b_y) < 20