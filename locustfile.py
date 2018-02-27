from locust import HttpLocust, TaskSet, task
from config_schema import sample_config

class UserBehavior(TaskSet):
  def on_start(self):
    pass

  @task(1)
  def get(self):
    self.client.get("/")

  def post(self):
    self.client.post("/config", json=sample_config, headers={
      'Content-Type': 'application/json'
    })

class WebsiteUser(HttpLocust):
  task_set = UserBehavior
  min_wait = 5000
  max_wait = 9000
