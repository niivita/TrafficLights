# TrafficLights
Regulating Traffic Lights at 4-Way Stop 


Requires Python 3.11 and pygame

## Build instructions
* Make sure you have installed the pygame library
* Run simulation.py by navigating to the library where the file is located and running `python3 simulation.py`

## Design Details
* The intersection is designed to have two lanes per direction, where the left lane is a left only turn at the intersection and the right lane is a straight or right turn only lane.

* Picture shown for the intersection:
![bg_intersection](https://github.com/niivita/TrafficLights/assets/102556053/0b835bf4-4505-4b27-a755-318d1d228b3c)

* The light to the right of the lane corresponds to that lane (shown below with numbers pairing lane and light):
  ![intersection_diagram](https://github.com/niivita/TrafficLights/assets/102556053/57d01601-0d75-4b1a-9f63-2f3cc4ed4392)


## Secure and Unsecure States
### Secure states
* All traffic lights red- secure when the intersection is empty.
* Only one direction green- secure when no vehicles are crossing paths.
* Yellow with enough time for cars at the intersection to exit the intersection before red comes up.
  * To ensure that no cars will be in the intersection when the red light happens, we ensured that (Speed of the car) * (time of yellow light) > (length of intersection)
* Pedestrian crossing light on when red light is on for the parallel direction.
 
## Unsecure states
* Light change from red to green in one direction when another direction is still yellow.
* When vehicle is turning left, ensure that it does not run into a crossroads with the car that's coming in the opposite direction.
* Pedestrian light is on to cross when the green/yellow light is on for the direction perpendicular to the pedestrian crossing.

# Assignment Instructions:

## Specifications:
* Using Traffic and Pedestrian Lights at the 4-way crossing, actively manage both vehicle and pedestrian traffic.
* At most one set of lights facing cross streets at an intersection is green for Vehicular traffic
* Safely move pedestrian traffic across the intersections while allowing movable vehicle traffic in other directions.
* Safely pass right, left and through-pass vehicle traffic at the intersection.
## Design
* Synch the timing of color changes timing of lights facing the opposite directions (i.e. light facing north and south should be the same color at the same time)
* When north/south facing lights are green or yellow then east/west facing lights should be red ( and v.v.)
* Transition of colors should be green for x seconds then yellow for y seconds then red for z seconds then back to green
* Anticipate all secure and unsecure states and implement mechanisms (traffic light sequences) to ensure a secure state
## Implementation
* Write and test code to satisfy the design of the secure state for both vehicle and pedestrian traffic
* Code in any language (Python preferred) but MUST present running code and simulated traffic lights in code GUI
