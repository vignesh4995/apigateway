from locust import HttpUser, TaskSet, task, between

class APITestTasks(TaskSet):
    @task
    def call_root(self):
        with self.client.get("/", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Failed with status code {response.status_code}")
            else:
                response.success()

class WebsiteUser(HttpUser):
    tasks = [APITestTasks]
    wait_time = between(1, 5)
