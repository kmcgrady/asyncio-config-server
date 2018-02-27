from locust import HttpLocust, TaskSet, task

class UserBehavior(TaskSet):
  def on_start(self):
    pass

  @task(1)
  def get(self):
    self.client.get("/")

  def post(self):
    self.client.post("/config", json={
      "tenant": "acme",
      "integration_type": "flight-information-system",
      "configuration": {
        "username": "acme_user",
        "password": "acme54321",
        "wsdl_urls": {
          "session_url": "https://session.manager.svc",
          "booking_url": "https://booking.manager.svc"
        }
      }
    }, headers={
      'Content-Type': 'application/json'
    })

class WebsiteUser(HttpLocust):
  task_set = UserBehavior
  min_wait = 5000
  max_wait = 9000
