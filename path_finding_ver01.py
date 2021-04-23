import asyncio
from mavsdk import System

import math


async def run():
    current_location = "E"
    fly_to_new_location = False
    location_E = [59.347372137351705, 18.073428604055536]
    location_Q = [59.349954061446454, 18.067289782044295]
    location_M = [59.35337996235275, 18.065071080920088]

    drone = System()
    await drone.connect()

    print("Waiting for drone...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"Drone discovered with UUID: {state.uuid}")
            break

    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok:
            print("Global position estimate ok")
            break

    print("Fetching amsl altitude at home location....")
    async for terrain_info in drone.telemetry.home():
        absolute_altitude = terrain_info.absolute_altitude_m
        break
    flying_alt = absolute_altitude + 100

    repeat = True
    while repeat:
        while not fly_to_new_location:

            print("Chose a new location to fly to.")
            print('"Location 1: write "E"')
            print('"Location 2: write "Q"')
            print('"Location 3: write "M"')

            new_location = input("Command: ")

            new_location = new_location.upper()

            if new_location == "E" or new_location == "Q" or new_location == "M":
                if new_location == current_location:
                    print("Drone already occupies specified location.")
                    await asyncio.sleep(1.5)
                else:
                    print("Input accepted.")
                    fly_to_new_location = True
                    await asyncio.sleep(1.5)
            else:
                print("Invalid location.")
                await asyncio.sleep(1.5)

        print("-- Arming")
        await drone.action.arm()
        print("-- Taking off")
        await drone.action.takeoff()

        print("Getting current latitude.")
        async for terrain_info in drone.telemetry.position():
            current_latitude = terrain_info.latitude_deg
            break

        print("Getting current longitude.")
        async for terrain_info in drone.telemetry.position():
            current_longitude = terrain_info.longitude_deg
            break

        print("reaching desired altitude")
        await drone.action.goto_location(current_latitude, current_longitude, flying_alt, 0)

        check_again = True
        while check_again:
            await asyncio.sleep(5)
            async for terrain_info in drone.telemetry.position():
                current_altitude = terrain_info.relative_altitude_m
                break

            if current_altitude > 99:
                check_again = False

        print("-- Flying to location " + '"' + new_location + '"')
        save_lat_long = []
        if new_location == "E":
            save_lat_long = [round(location_E[0], 6), round(location_E[1], 6)]
            await drone.action.goto_location(location_E[0], location_E[1], flying_alt, 0)
        elif new_location == "Q":
            save_lat_long = [round(location_Q[0], 6), round(location_Q[1], 6)]
            await drone.action.goto_location(location_Q[0], location_Q[1], flying_alt, 0)
        elif new_location == "M":
            save_lat_long = [round(location_M[0], 6), round(location_M[1], 6)]
            await drone.action.goto_location(location_M[0], location_M[1], flying_alt, 0)

        check_again = True
        while check_again:
            await asyncio.sleep(5)

            async for terrain_info in drone.telemetry.position():
                current_latitude = terrain_info.latitude_deg
                break

            async for terrain_info in drone.telemetry.position():
                current_longitude = terrain_info.longitude_deg
                break

            current_latitude = round(current_latitude, 6)
            current_longitude = round(current_longitude, 6)

            if math.isclose(current_latitude, save_lat_long[0]) and math.isclose(current_longitude, save_lat_long[1]):
                check_again = False

        print("Location reached.")
        print("-- Landing")
        await drone.action.land()

        check_again = True
        while check_again:
            await asyncio.sleep(5)
            async for terrain_info in drone.telemetry.position():
                current_altitude = terrain_info.relative_altitude_m
                break

            if current_altitude < 1:
                current_location = new_location
                fly_to_new_location = False
                check_again = False

        print("Would you like to exit? Yes or no?")
        yes_or_no = input("Command: ")
        yes_or_no = yes_or_no.upper()

        if yes_or_no == "YES":
            repeat = False


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
