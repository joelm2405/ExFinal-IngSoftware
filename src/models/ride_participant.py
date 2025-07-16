class RideParticipant:
    def __init__(self, ride_id, alias, destination, occupiedSpaces):
        self.ride_id = ride_id
        self.alias = alias
        self.destination = destination
        self.occupiedSpaces = occupiedSpaces
        self.confirmation = None  # confirmed, rejected, None
        self.status = "waiting"  # waiting, inprogress, completed, missing, notmarked

    def get_participant_info(self, stats=None):
        return {
            "confirmation": self.confirmation,
            "participant": {
                "alias": self.alias,
                "previousRidesTotal": stats.get("total", 0) if stats else 0,
                "previousRidesCompleted": stats.get("completed", 0) if stats else 0,
                "previousRidesMissing": stats.get("missing", 0) if stats else 0,
                "previousRidesNotMarked": stats.get("not_marked", 0) if stats else 0,
                "previousRidesRejected": stats.get("rejected", 0) if stats else 0,
            },
            "destination": self.destination,
            "occupiedSpaces": self.occupiedSpaces,
            "status": self.status
        }

# Diccionario de participantes (clave = (ride_id, alias))
ride_participants_db = {}
