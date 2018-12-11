# Pacman Artificial Intelligence Agents

This repository contains the coursework for Artificial Intelligence course.

  - [LeftTurnAgent](https://github.com/Cinkupis/PacmanArtificialIntelligence/blob/master/leftTurnAgents.py)
    - A pacman agent that whenever possible, tries to turn left. Has all of the information.
  - [HungryAgent](https://github.com/Cinkupis/PacmanArtificialIntelligence/blob/master/hungryAgents.py)
    - A pacman agent, whose main goal is to eat all the food. His information limited to up to 5 squares away from him.
  - [SurvivalAgent](https://github.com/Cinkupis/PacmanArtificialIntelligence/blob/master/survivalAgents.py)
    - A pacman agent, whose main goal is to stay alive as much as possible. His information limited to up to 5 squares away from him.
  - [PartialAgent](https://github.com/Cinkupis/PacmanArtificialIntelligence/blob/master/partialyAgents.py)
    - A pacman agent that only has information in his vicinity up to 5 squares down the hallway. He can also see whats one square right around the corner if being at an intersection and can hear what is behind the wall on the square perpendicular to him.
  - [RandomAgent](https://github.com/Cinkupis/PacmanArtificialIntelligence/blob/master/randomAgents.py)
    - A pacman agent that does a random move without any considerations.
  - [RandomishAgent](https://github.com/Cinkupis/PacmanArtificialIntelligence/blob/master/randomishAgents.py)
    - A pacman agent that chooses a random direction and continues going in that direction until hits a wall and chooses a different random direction.
  - [SensingAgent](https://github.com/Cinkupis/PacmanArtificialIntelligence/blob/master/sensingAgents.py)
    - A pacman agent that displays information about map. Doesn't move.
  - [MapAgent](https://github.com/Cinkupis/PacmanArtificialIntelligence/blob/master/mapAgents.py)
    - A pacman agent that creates an internal map of the layout and displays it. Makes random moves.
  - [MDPAgent](https://github.com/Cinkupis/PacmanArtificialIntelligence/blob/master/mdpAgents.py)
    - A pacman agent that uses Markov Decision Process to solve the best move to make. Uses Approximate Value Iteration algorithm to calculate utilities of each square. Chooses the next move based on Maximum Expected utility.

# Running Pacman

  - Requires Python 2.7 installed on your system
  - To run selected agent, type into the console:
    ```sh 
     python pacman.py --pacman <Selected Agents class name> -l mediumClassic
    ```
  - For a different maze layout:
    ```sh 
    python pacman.py --pacman <Selected Agents class name> --layout smallClassic
    ```
  - For a maze layout without ghosts:
    ```sh 
    python pacman.py --pacman <Selected Agents class name> --layout mediumClassicNoGhosts
    ```
  ---
  - List of available layouts:
    ```sh 
    bigCorners
    bigMaze
    bigSafeSearch
    bigSearch
    boxSearch
    capsuleClassic
    contestClassic
    contoursMaze
    greedySearch
    mediumClassic
    mediumClassicNoGhosts
    mediumMDPNoGhosts
    mediumCorners
    mediumDottedMaze
    mediumMaze
    mediumSafeSearch
    mediumScaryMaze
    mediumSearch
    minimaxClassic
    oddSearch
    openClassic
    openMaze
    openSearch
    originalClassic
    powerClassic
    smallClassic
    smallGrid
    smallMDPGrid
    smallMaze
    smallSafeSearch
    smallSearch
    testClassic
    testMaze
    testSearch
    tinyCorners
    tinyMaze
    tinySafeSearch
    tinySearch
    trappedClassic
    trickyClassic
    trickySearch
    ```