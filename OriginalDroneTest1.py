'''
This script flies a drone to a new location, and then flies back to launch
once the new location has been reached.
'''

import asyncio
from mavsdk import System

import math

async def run():

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

    'Comment: Get launch position... I think. NOT the current position... I think.'
    print("Fetching amsl altitude at home location....")
    async for terrain_info in drone.telemetry.home():
        absolute_altitude = terrain_info.absolute_altitude_m
        break

    print("Fetching latitude....")
    async for terrain_info in drone.telemetry.home():
        home_latitude = terrain_info.latitude_deg
        break

    print("Fetching longitude....")
    async for terrain_info in drone.telemetry.home():
        home_longitude = terrain_info.longitude_deg
        break

    print("-- Arming")
    await drone.action.arm()

    print("-- Taking off")
    await drone.action.takeoff()

    print("-- Flying to new location.")
    'Comment: flying_alt is a float specifying the altitude at launch + 20 units into the air.'
    flying_alt = absolute_altitude + 20.0
    new_latitude = home_latitude + 0.001
    'Comment: Maintains the same longitude but flies to new latitude, and altitude.'
    await drone.action.goto_location(new_latitude, home_longitude, flying_alt, 0)

    '''
    The while loop below is used to check every ten seconds whether the drone 
    has reached the target position or not. 
    '''
    checkAgain = True
    while checkAgain:

        'Comment: terrain_info stores current coordinate information, so we know where we are.'
        async for terrain_info in drone.telemetry.position():
            current_latitude = terrain_info.latitude_deg
            break

        '''
        Comment: latitude and longitude is VERY precise. Even more precise than the drone
        itself in fact, which is why we need to round the variables. 
        '''
        current_latitude_round = round(current_latitude, 6)
        new_latitude_round = round(new_latitude, 6)

        '''
        Comment: As mentioned before, the variables inside math.isclose() below needed
        to be rounded as otherwise the function wouldn't have recognized them as the
        same position even when they're next to each other. 
        '''
        if math.isclose(current_latitude_round, new_latitude_round):
            checkAgain = False

        print("current: " + str(current_latitude_round) + "!! home: " + str(new_latitude_round))
        'Comment: Ensure the loop only checks once every 5 seconds.'
        await asyncio.sleep(5)

    print("-- Returning home.")
    await drone.action.goto_location(home_latitude, home_longitude, absolute_altitude, 0)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())