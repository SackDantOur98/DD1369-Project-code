# MAVSDK-Python

This repository houses our code for the course DD1369, written in Python.

Our project: We are to create a system that will allow a drone to fly from one point to another, taking into account safety and efficiency.

## Instructions

**Starting a simulation**

Run the simulation using the usual "make px4_sitl <type of simulator>" command. (Of course you need to download all necessary programs first. How to do this is detailed here: https://docs.px4.io/master/en/dev_setup/dev_env.html and https://docs.px4.io/master/en/dev_setup/building_px4.html)

<Important:> The simulation will not work as intended unless it starts in a specific location, so *before* running the simulation, type the following into the terminal:

'''
export PX4_HOME_LAT=59.347372137351705
export PX4_HOME_LON=18.073428604055536
'''  

It may also be a good idea to speed up the simulation:

'''
export PX4_SIM_SPEED_FACTOR=10
'''

**To keep in mind**

This is something we didn't discover until after finishing the project. The obstacle avoidance algorithm is based on speed rather than distance, meaning a slower simulation will *dramatically* slow down the drone when flying around an obstacle. For this reason it is highly advised that you speed up the simulation by 10 – as explained and shown above – before running it.  
