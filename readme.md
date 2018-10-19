# Pacman Artificial Intelligence Agents

This repository contains the coursework for Artificial Intelligence course. For code written by me, please refer to [sampleAgents.py](www.google.com) file.

  - GoLeftAgent
    - A pacman agent that whenever possible, tries to turn left. Has all of the information.
  - HungryAgent
    - A pacman agent, whose main goal is to eat all the food. His information limited to up to 5 squares away from him.
  - SurvivalAgent
    - A pacman agent, whose main goal is to stay alive as much as possible. His information limited to up to 5 squares away from him.
  - PartialAgent
    - A pacman agent that only has information in his vicinity up to 5 squares down the hallway. He can also see whats one square right around the corner if being at an intersection and can hear what is behind the wall on the square perpendicular to him.

# Running Pacman

  - Requires Python 2.7 installed on your system
  - To run selected agent, type into the console:
    ```sh 
     python pacman.py --pacman <Selected Agents class name>
    ```
  - For a different maze layout:
    ```sh 
    python pacman.py --pacman <Selected Agents class name> --layout smallClassic
    ```
  - For a maze layout without ghosts:
    ```sh 
    python pacman.py --pacman <Selected Agents class name> --layout mediumClassicNoGhosts
    ```