def close_proximity_circle_to_circle(a, b):
    '''
    used for proximity between centres of two circles
    '''
    x1 = a[0]
    y1 = a[1]
    x2 = b[0]
    y2 = b[1]
    return abs(x1 - x2) < 20 and abs(y1 - y2) < 20

def close_proximity_line_to_circle(a, b):
    '''
    used for line endpoint proximity to centre of circle
    '''
    x1 = a[0]
    y1 = a[1]
    x2 = b[0]
    y2 = b[1]
    # return True
    return pow(x1 - x2, 2) + pow(y1 - y2, 2) < 3000