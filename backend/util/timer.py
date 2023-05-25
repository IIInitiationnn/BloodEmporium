import time


class Timer:
    PRINT = False

    def __init__(self, descriptor):
        self.timers = [time.time()]
        self.descriptor = descriptor

    def update(self):
        self.timers.append(time.time())
        if Timer.PRINT:
            print(f"timer for {self.descriptor} | {round(1000 * (self.timers[-1] - self.timers[-2]), 1)}ms")