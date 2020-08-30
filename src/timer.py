import time


class Timer:
    def __init__(self, timers={}):
        now = time.time()
        self.timers = timers
        self.last_tss = {tn: now for tn in timers.keys()}

    def update_elapsed_times(self):
        now = time.time()
        self.elapsed_times = {
            tn: now - self.last_tss[tn] for tn in self.timers.keys()
        }

    def time_to(self, timer_name):
        assert timer_name in self.timers, \
            f"Timer {timer_name} does not exists: {self.timers}"
        if self.elapsed_times[timer_name] > self.timers[timer_name]:
            self.last_tss[timer_name] = time.time()
            return True
        return False
