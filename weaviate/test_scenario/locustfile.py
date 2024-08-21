from locust import HttpUser, task, between, LoadTestShape

class DuplicateDetectionUser(HttpUser):
    wait_time = between(1, 2)
    host = "http://localhost:8000" 

    @task(1)
    def test_duplicate_detection(self):
        payload = {
            "place_name": "میدان کتاب",
            "location": {
                "latitude": 35.7774394,
                "longitude": 51.355904
            },
            "address": "تهران، منطقه ۲، سرو، نزدیک بزرگراه ایت الله هاشمی رفسنجانی",
            "tag": "square"
            }
        self.client.post("/search_duplicate", json=payload)

class StagesShape(LoadTestShape):
    stages = [
        {"duration": 60, "users": 100, "spawn_rate": 10},
        {"duration": 180, "users": 1000, "spawn_rate": 10},
    ]

    def tick(self):
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage["duration"]:
                tick_data = (stage["users"], stage["spawn_rate"])
                return tick_data
        return None  
