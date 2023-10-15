# TrafficLights
Regulating Traffic Lights at 4-Way Stop 


Requires Python 3.11 and brew install python-tk@3.11

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
