# MAVSDK-Python

This repository houses our code for the course DD1369, written in Python.

Our project: We are to create a system that will allow a drone to fly from one point to another, taking safety and efficiency into account.

## Instructions

***Starting a simulation***

Run the simulation using the usual "make px4_sitl (Name of simulator)" command. (Of course you need to download all necessary programs first. How to do this is detailed here: https://docs.px4.io/master/en/dev_setup/dev_env.html and https://docs.px4.io/master/en/dev_setup/building_px4.html)

Important: The simulation will not work as intended unless it starts in a specific location, so *before* running the simulation, type the following into the terminal:

```
export PX4_HOME_LAT=59.347372137351705
export PX4_HOME_LON=18.073428604055536
```  

It may also be a good idea to speed up the simulation:

```
export PX4_SIM_SPEED_FACTOR=10
```

***Adding an obstacle***

We couldn't figure out how to use QGroundControl to identify high buildings or populated areas, so these must be added manually in the code. We apologise for the inconvenience.

Use the following steps to add an obstacle:

1. Use google maps to identify the longitude and latitude of the centre of your obstacle. This can be done by right clicking on a geographical point and copying the desired data (in google maps).  
2. Find the obstacle_coordinates variable in the script. It's at the top of the prepare_before_run method.
3. Add the coordinates (latitude first, then longitude) as shown in the script, and specify whether it's an obstacle or a populated area. How to do this is also detailed in the script, right above the variable in question.

***Running the script***

All necessary information specified by the user is entered using the input function, so make sure you use an IDE with an easy to access console. We recommend PyCharm.

Important: If the drone is in the air when you run the code you will get an error, so make sure the drone is on the ground and not armed before running it.

***To keep in mind***

This is something we didn't discover until after finishing the project. We tested the obstacle avoidance algorithm on 10 times the normal simulation speed. The problem is that the algorithm is based on time (timed events) rather than distance, meaning a slower simulation will *dramatically* slow down the drone when flying around an obstacle. For this reason it is highly advised that you speed up the simulation by 10 using 'export PX4_SIM_SPEED_FACTOR=10' – as explained and shown above – before running it.  

***Bugs***

1. At times QGroundControl will disconnect from the simulation. This is not due to our code as this can happen at any time, even when no "homemade" code is used to effect the drone's behaviour. This bug may be due to a flimsy internet connection or possibly due to an unsolved problem in the PX4 source code. No idea how to solve it.

2. It has happened that the drone flies over obstacles it should circumvent. This happens without rhyme or reason and after much testing (and hair pulling at times) we have not managed to find a solution. We believe this is due to a bug in the PX4 source code, although of course the problem could be rooted in our code as well, but we find this highly unlikely.  
