import pytest
from src.models.usuario import Usuario
from src.models.ride import Ride
from src.models.ride_participant import RideParticipant

def test_usuario_get_info():
    usuario = Usuario(alias="jperez", name="Juan Pérez", email="jperez@utec.edu.pe")
    info = usuario.get_user_info()
    assert info["alias"] == "jperez"
    assert info["name"] == "Juan Pérez"
    assert info["email"] == "jperez@utec.edu.pe"
    assert "stats" in info
    assert info["stats"] == {
        "total": 0,
        "completed": 0,
        "missing": 0,
        "not_marked": 0,
        "rejected": 0
    }

def test_ride_get_info():
    ride = Ride(
        ride_id=1,
        driver_alias="jperez",
        rideDateAndTime="2025/07/15 22:00",
        finalAddress="Av Javier Prado 456",
        capacity=3
    )
    ride.participants = ["lgomez"]
    info = ride.get_ride_info()
    assert info["id"] == 1
    assert info["driver"] == "jperez"
    assert info["rideDateAndTime"] == "2025/07/15 22:00"
    assert info["finalAddress"] == "Av Javier Prado 456"
    assert info["capacity"] == 3
    assert info["status"] == "ready"
    assert info["participants"] == ["lgomez"]

def test_ride_participant_get_info_with_stats():
    stats = {
        "total": 5,
        "completed": 3,
        "missing": 1,
        "not_marked": 0,
        "rejected": 1
    }
    rp = RideParticipant(
        ride_id=1,
        alias="lgomez",
        destination="Av Aramburú",
        occupiedSpaces=1
    )
    rp.confirmation = "confirmed"
    rp.status = "inprogress"
    info = rp.get_participant_info(stats)
    assert info["confirmation"] == "confirmed"
    assert info["participant"]["alias"] == "lgomez"
    assert info["participant"]["previousRidesTotal"] == 5
    assert info["participant"]["previousRidesCompleted"] == 3
    assert info["participant"]["previousRidesMissing"] == 1
    assert info["participant"]["previousRidesNotMarked"] == 0
    assert info["participant"]["previousRidesRejected"] == 1
    assert info["destination"] == "Av Aramburú"
    assert info["occupiedSpaces"] == 1
    assert info["status"] == "inprogress"

def test_ride_participant_get_info_without_stats():
    rp = RideParticipant(
        ride_id=2,
        alias="jlopez",
        destination="Av Arequipa",
        occupiedSpaces=2
    )
    info = rp.get_participant_info()
    assert info["participant"]["previousRidesTotal"] == 0
    assert info["participant"]["previousRidesCompleted"] == 0
    assert info["participant"]["previousRidesMissing"] == 0
    assert info["participant"]["previousRidesNotMarked"] == 0
    assert info["participant"]["previousRidesRejected"] == 0