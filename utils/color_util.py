import math

class ColorUtil:
    taupe_hex = "#969664"
    taupe_rgb = (150, 150, 100)

    red_hex = "#C80A0A"
    red_rgb = (200, 10, 10)

    neutral_hex = "#37323C"
    neutral_rgb = (55, 50, 60)

    black_hex = "#000000"
    black_rgb = (0, 0, 0)

    @staticmethod
    def diff(color1, color2):
        r1, g1, b1 = color1
        r2, g2, b2 = color2

        r_dash = (r1 + r2) / 2

        return (2 + r_dash / 256) * math.pow(r1 - r2, 2) + \
               4 * math.pow(g1 - g2, 2) + \
               (2 + (255 - r_dash) / 256) * math.pow(b1 - b2, 2)