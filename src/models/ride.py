class Ride:
    def __init__(self, ride_id, driver_alias, rideDateAndTime, finalAddress, capacity):
        self.id = ride_id
        self.driver = driver_alias
        self.rideDateAndTime = rideDateAndTime  # string: "YYYY/MM/DD HH:MM"
        self.finalAddress = finalAddress
        self.capacity = capacity
        self.status = "ready"  # ready, inprogress, finished
        self.participants = []  # lista de alias (vinculados a RideParticipant)

    def get_ride_info(self):
        return {
            "id": self.id,
            "rideDateAndTime": self.rideDateAndTime,
            "finalAddress": self.finalAddress,
            "driver": self.driver,
            "status": self.status,
            "capacity": self.capacity,
            "participants": self.participants  # lista de alias o ids
        }

# Diccionario de rides (clave = ride_id)
rides_db = {}
