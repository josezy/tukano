import time

class Timer():
	timer_names = ['data_collect', 'data_send', 'take_pic']
	last_tss = None

	def __init__(self):
		now = time.time()
		self.last_tss = {tn: now for tn in self.timer_names}
		