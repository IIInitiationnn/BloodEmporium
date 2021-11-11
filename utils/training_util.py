import cv2
from scipy.optimize import basinhopping
from skimage.metrics import structural_similarity

from matcher import CircleMatcher, HoughTransform

class CircleTrainer:
    '''to find best parameters for matching circles'''
    def __init__(self):
        '''targets = {}
        for base in [os.path.join(subdir, file) for (subdir, dirs, files) in os.walk("training_data/bases") for file in files]:
            targets[base] = cv2.imread(base, cv2.IMREAD_GRAYSCALE)'''

        self.path_to_base = "training_data/bases/shaderless/base_nurse.png"
        self.target = cv2.imread("training_data/bases/shaderless/base_nurse_target.png", cv2.IMREAD_GRAYSCALE)
        self.c_blur = 15

        self.lowest = 9999
        self.lowest_set = ()
        self.i = 0

        minimizer_kwargs = {"method": "L-BFGS-B", "bounds": ((1, 40), (20, 60))}
        result = basinhopping(self.ssim, (10, 30), stepsize=1, niter=1000, minimizer_kwargs=minimizer_kwargs)
        print('Status : %s' % result['message'])
        print('Total Evaluations: %d' % result['nfev'])
        solution = result['x']
        evaluation = self.ssim(solution)
        print('Solution: f(%s) = %.5f' % (solution, evaluation))
        # solution = (31.9, 46.5) # blur=9
        # solution = (9.5, 30.7) # blur=15

        HoughTransform(self.path_to_base, self.c_blur, solution[0], solution[1], 5, 85, 40, 30, 25)
        cv2.imshow("target", self.target)
        cv2.imshow("solution", CircleMatcher.match(self.path_to_base, self.c_blur, solution[0], solution[1]))
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        '''for i in range(10000):
            circle_blur = 11
            hough_1 = 8 + random.uniform(0, 4)
            hough_2 = 43 + random.uniform(0, 4)

            print(circle_blur, hough_1, hough_2)

            success = True
            matches = {}
            for base in [file for (subdir, dirs, files) in os.walk("training_data/bases") for file in files]:
                match = CircleMatcher(base, circle_blur, hough_1, hough_2)
                matches[base] = match.output
                circles = match.circles.copy()

                missed = []

                for target_circle in targets[base].copy():
                    success = False
                    for circle in circles:
                        if circles_are_overlapping(target_circle, circle):
                            success = True
                            circles.remove(circle)
                            break

                    if not success:
                        missed.append(target_circle)

                if not success or len(circles) > 10 or len(missed) > 10:
                    success = False
                    break

            if success:
                path = f"circle_trainer/successes/blur={circle_blur}_hough1={hough_1}_hough2={hough_2}/"
                os.mkdir(path)
                for base, match in matches.items():
                    cv2.imwrite(f"{path}/{base}", match)
            else:
                path = f"circle_trainer/failures/blur={circle_blur}_hough1={hough_1}_hough2={hough_2}/"
                os.mkdir(path)
                for base, match in matches.items():
                    cv2.imwrite(f"{path}/{base}", match)'''

    def ssim(self, params):
        self.i += 1
        param1, param2 = params
        s = structural_similarity(self.target, CircleMatcher.match(self.path_to_base, self.c_blur, param1, param2))
        print(self.c_blur, param1, param2, 1 - s)

        if 1 - s < self.lowest:
            self.lowest = 1 - s
            self.lowest_set = self.c_blur, param1, param2
            print(f"\n\n\n{self.i}\n", self.lowest_set, self.lowest, "\n\n\n")

        return 1 - s
