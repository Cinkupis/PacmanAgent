# Pacman Artificial Intelligence Agents

This repository contains the coursework for Artificial Intelligence course. For code written by me, please refer to [sampleAgents.py](www.google.com) file.

  - GoLeftAgent
    - A pacman agent that whenever possible, tries to turn left
  - HungryAgent
    - A pacman agent, whose main goal is to eat all the food
  - SurvivalAgent
    - A pacman agent, whose main goal is to stay alive as much as possible
  - HungrySurvivalCornerSeekingAgent
    - A pacman agent that combines SurvivalAgent's and HungerAgent's philosophy, with the addition that if neither can be achieved, targets clearing maze corcers.

# Running Pacman

  - Requires Python 2.7 installed on your system
  - To run selected agent, type into the console:
    - ```sh 
        python pacman.py --pacman <Selected Agents class name>
        ```
  - For a different maze layout:
    - ```sh 
        python pacman.py --pacman <Selected Agents class name> --layout smallClassic
        ```