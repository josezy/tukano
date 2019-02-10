from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def compute_data(func, *args, **kwargs):
    func(*args, **kwargs)

