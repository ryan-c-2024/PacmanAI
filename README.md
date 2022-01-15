# PacmanAI
Python-implemented AI for Pacman

PacmanAI is an AI project written in Python that leverages core artificial intelligence programming techniques and concepts and applies them to the realm of Pacman. The end result is a fully automatic AI capable of beating baseline bots and even other AI in a Capture-The-Flag Pacman game without any user input required. The project uses Berkeley's Pacman Project as a base and expands on it. 

Artificial intelligence concepts utilizes include:
1. Minimax - used to evaluate moves to maximize benefit, even if an adversary is in the area (optimized features and weightings were chosen for the evaluation function to boost performance). Depth is limited as to preserve performance.
2. Particle filtering - A Monte Carlo algorithm used for rapid Bayesian statistical inference to determine adversarial locations. Though it compromises some accuracy, in the context of the Pacman game, particle filtering was found to be signficiantly more efficient to run than other means of inference.

Compatible on a number of map layouts, the algorithm proved to be efficient and highly effective in both defending, seeking food, and attacking enemies.

Collaboration project with Taichi Kato (https://github.com/taixhi/)
