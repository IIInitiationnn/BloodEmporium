import cv2

class Images:
    interpolation = cv2.INTER_CUBIC

    def __init__(self):
        origin_basic = cv2.split(cv2.imread("training_data/bases/base_larger.png", cv2.IMREAD_UNCHANGED))
        self.origin_basic_r = origin_basic[2]
        self.origin_basic_a = origin_basic[3]

        # same with prestige

    def origin_basic_r_resize(self, dim):
        return cv2.resize(self.origin_basic_r, (dim, dim), interpolation=Images.interpolation)

    def origin_basic_a_resize(self, dim):
        return cv2.resize(self.origin_basic_a, (dim, dim), interpolation=Images.interpolation)
