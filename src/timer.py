import time
import settings

class Timer():
	timer_names = None
	last_tss = None

	def update_elapsed_times():
		now = time.time()
		self.last_tss = {tn: now for tn in self.timer_names}

	def __init__(self, names):
		self.timer_names = names
		now = time.time()
		self.last_tss = {tn: now for tn in self.timer_names}

	def can(self, data, timespan):
		now = time.time()
		elapsed_time = now - self.last_tss[data]

		can_collect_data = elapsed_time > timespan
		if can_collect_data:
			self.last_tss[data] = now
		return can_collect_data

	def can_collect_data(self):
		return self.can('collect_data', settings.DATA_COLLECT_TIMESPAN)

	def can_send_data(self):
		return self.can('send_data', settings.MAVLINK_SAMPLES_TIMESPAN)	

	def can_take_pic(self):
		return self.can('take_pic', settings.TAKE_PIC_TIMESPAN)
