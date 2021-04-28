import asyncio
import geopy.distance
import numpy as np
from mavsdk import System

import math


async def circumvent_obstacle(drone, obstacle_coordinates, flying_alt):
    current_latitude = await get_GPS(drone, "latitude")
    current_longitude = await get_GPS(drone, "longitude")

    back_away_latitude = current_latitude - obstacle_coordinates[0]
    back_away_longitude = current_longitude - obstacle_coordinates[1]

    await drone.action.goto_location(current_latitude + (back_away_latitude/2),
                                     current_longitude + (back_away_longitude/2),
                                     flying_alt, 0)
    await asyncio.sleep(2)

    await drone.action.goto_location(current_latitude - back_away_longitude,
                                     current_longitude + back_away_latitude,
                                     flying_alt, 0)
    await asyncio.sleep(3)


async def check_distance(drone, obstacle_coordinates):
    async for terrain_info in drone.telemetry.position():
        current_drone_latitude = terrain_info.latitude_deg
        break

    async for terrain_info in drone.telemetry.position():
        current_drone_longitude = terrain_info.longitude_deg
        break

    for obstacle_coordinate in obstacle_coordinates:
        obstacle_point = (obstacle_coordinate[0], obstacle_coordinate[1])
        drone_point = (current_drone_latitude, current_drone_longitude)

        if geopy.distance.distance(obstacle_point, drone_point).m < 50:
            return obstacle_coordinate


async def prepare_before_run():
    current_location = "E"

    location_E = [59.347372137351705, 18.073428604055536]
    location_Q = [59.349954061446454, 18.067289782044295]
    location_M = [59.35337996235275, 18.065071080920088]

    '''
    The first coordinates are the KTH library. 
    The other two are different endings of the B-building. 
    '''
    obstacle_coordinates = [[59.348001208303316, 18.072331990932845],
                            [59.35148919491157, 18.06850836848911],
                            [59.35186805689535, 18.067843079316706]]

    fly_to_new_location = False

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
    await run(drone, current_location, fly_to_new_location, location_E, location_Q, location_M, repeat,
              flying_alt, obstacle_coordinates)


async def get_GPS(drone, type_of_GPS):
    if type_of_GPS == "latitude":
        async for terrain_info in drone.telemetry.position():
            current_latitude = terrain_info.latitude_deg
            break
        return current_latitude
    elif type_of_GPS == "longitude":
        async for terrain_info in drone.telemetry.position():
            current_longitude = terrain_info.longitude_deg
            break
        return current_longitude
    elif type_of_GPS == "altitude":
        async for terrain_info in drone.telemetry.position():
            current_altitude = terrain_info.relative_altitude_m
            break
        return current_altitude


async def run(drone, current_location, fly_to_new_location, location_E, location_Q, location_M, repeat,
              flying_alt, obstacle_coordinates):
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

        current_latitude = await get_GPS(drone, "latitude")
        current_longitude = await get_GPS(drone, "longitude")

        print("reaching desired altitude")
        await drone.action.goto_location(current_latitude, current_longitude, flying_alt, 0)

        check_again = True
        while check_again:
            await asyncio.sleep(5)
            current_altitude = await get_GPS(drone, "altitude")

            if current_altitude > 99:
                check_again = False

        print("-- Flying to location " + '"' + new_location + '"')
        save_lat_long = []
        save_actual_lat_long = []
        if new_location == "E":
            save_lat_long = [round(location_E[0], 6), round(location_E[1], 6)]
            save_actual_lat_long = [location_E[0], location_E[1]]
            await drone.action.goto_location(location_E[0], location_E[1], flying_alt, 0)
        elif new_location == "Q":
            save_lat_long = [round(location_Q[0], 6), round(location_Q[1], 6)]
            save_actual_lat_long = [location_Q[0], location_Q[1]]
            await drone.action.goto_location(location_Q[0], location_Q[1], flying_alt, 0)
        elif new_location == "M":
            save_lat_long = [round(location_M[0], 6), round(location_M[1], 6)]
            save_actual_lat_long = [location_M[0], location_M[1]]
            await drone.action.goto_location(location_M[0], location_M[1], flying_alt, 0)

        check_again = True
        while check_again:
            await asyncio.sleep(0.2)

            coordinates_to_circumvent = await check_distance(drone, obstacle_coordinates)

            if coordinates_to_circumvent is None:
                current_latitude = await get_GPS(drone, "latitude")
                current_longitude = await get_GPS(drone, "longitude")

                current_latitude = round(current_latitude, 6)
                current_longitude = round(current_longitude, 6)

                if math.isclose(current_latitude, save_lat_long[0]) and math.isclose(current_longitude, save_lat_long[1]):
                    check_again = False
            else:
                await circumvent_obstacle(drone, coordinates_to_circumvent, flying_alt)
                await drone.action.goto_location(save_actual_lat_long[0], save_actual_lat_long[1],
                                                 flying_alt, 0)

        print("Location reached.")
        print("-- Landing")
        await drone.action.land()

        check_again = True
        while check_again:
            await asyncio.sleep(5)
            current_altitude = await get_GPS(drone, "altitude")

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
    loop.run_until_complete(prepare_before_run())
