import time


class Timer:
    PRINT = False

    def __init__(self):
        self.timers = [time.time()]

    def update(self, message):
        self.timers.append(time.time())
        if Timer.PRINT:
            print(f"timer for {message} | {round(1000 * (self.timers[-1] - self.timers[-2]), 1)}ms")