import json

class DataHandler:
    def __init__(self, filename='data.json'):
        self.filename = filename
        self.users = []
        self.rides = []
        self.ride_participants = []
        self.load_data()

    def save_data(self):
        data = {
            'users': self.users,
            'rides': self.rides,
            'ride_participants': self.ride_participants
        }
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=4)

    def load_data(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                self.users = data.get('users', [])
                self.rides = data.get('rides', [])
                self.ride_participants = data.get('ride_participants', [])
        except FileNotFoundError:
            self.users = []
            self.rides = []
            self.ride_participants = []