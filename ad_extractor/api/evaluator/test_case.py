from api.schema import AircraftConfiguration


async def create_test_aircraft() -> list[AircraftConfiguration]:
    return [
        AircraftConfiguration(aircraft_model="MD-11", msn=48123, modifications_applied=[]),
        AircraftConfiguration(aircraft_model="DC-10-30F", msn=47890, modifications_applied=[]),
        AircraftConfiguration(aircraft_model="Boeing 737-800", msn=30123, modifications_applied=[]),
        AircraftConfiguration(aircraft_model="A320-214", msn=5234, modifications_applied=[]),
        AircraftConfiguration(aircraft_model="A320-232", msn=6789, modifications_applied=["mod 24591 (production)"]),
        AircraftConfiguration(aircraft_model="A320-214", msn=7456, modifications_applied=["SB A320-57-1089 Rev 04"]),
        AircraftConfiguration(aircraft_model="A321-111", msn=8123, modifications_applied=[]),
        AircraftConfiguration(aircraft_model="A321-112", msn=364, modifications_applied=["mod 24977 (production)"]),
        AircraftConfiguration(aircraft_model="A319-100", msn=9234, modifications_applied=[]),
        AircraftConfiguration(aircraft_model="MD-10-10F", msn=46234, modifications_applied=[]),
    ]

async def create_verification_aircraft() -> list[AircraftConfiguration]:
    return [
        AircraftConfiguration(aircraft_model="MD-11F", msn=48400, modifications_applied=[]),
        AircraftConfiguration(aircraft_model="A320-214", msn=4500, modifications_applied=["mod 24591 (production)"]),
        AircraftConfiguration(aircraft_model="A320-214", msn=4500, modifications_applied=[]),
    ]