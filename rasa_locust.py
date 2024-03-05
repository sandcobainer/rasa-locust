from locust import HttpUser, TaskSet, task, between
from locust import events
import requests
import socketio
import time
import random


class UserBehavior(TaskSet):
    statements = ['hey', 'how to reset password', 'set my user type to Business', 'forgot username']

    def on_start(self):
        # no need of certifi
        http_session = requests.Session()
        http_session.verify = False

        # establish connection
        sio = socketio.Client(http_session=http_session)
        ws_url = "https://chatbot-service.rasaurl/"

        # get user session id for testing
        sio.connect(ws_url, transports="polling",)
        self.ws = sio
        self.user_id = sio.sid
        # body = json.dumps(["session_confirm", self.user_id])
        body = '{"session_request", {"session_id": "' + self.user_id + '"}}'
        self.ws.emit(body)

    def on_quit(self):
        self.ws.disconnect()

    @task(1)
    def say_hello(self):
        start_at = time.time()

        body = {"message": "Hello", "customData": {"language": "en"}, "session_id": self.user_id}

        # self.ws.send(body)
        self.ws.emit('user_uttered', data=body)

        events.request.fire(
            request_type='WebSocket Sent',
            name='test/ws/echo',
            response_time=int((time.time() - start_at) * 1000000),
            response_length=len(body),
        )

    @task(2)
    def say_random(self):
        start_at = time.time()

        statement = random.choice(self.statements)

        body = {"message": statement, "customData": {"language": "en"}, "session_id": self.user_id}

        # self.ws.send(body)
        self.ws.emit('user_uttered', data=body)

        events.request.fire(
            request_type='WebSocket Sent',
            name='test/ws/echo',
            response_time=int((time.time() - start_at) * 1000000),
            response_length=len(body),
        )


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(5, 15)

# 5c57023864bc4cf4bf82cf370d1b9349
# 0484184e70fa11eaad0ca45e60dc2e59
