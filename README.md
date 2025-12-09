# Palamedes

This repo contains the code of an Arduino SCARA Robot playing and winning at chess using image recognition and interpretation. Follow this link to see it in action [(LinkedIn link)](https://www.linkedin.com/posts/thomas-philip-b988a4235_robotics-computervision-mechatronics-activity-7150122722851790848-VY0i?utm_source=share&utm_medium=member_desktop&rcm=ACoAADqvu6QBlCZ45tFJxWi7nlGuZzm5lyRW3Bc)  

---

# How It Works

- A phone is connected to a PC running python programs
- A photo is taken to calibrate the system (`calibration.py`)
- After the calibration, the coordinates of each cell of the chessboard is known
- The chess pieces are placed and a photo is taken
- The player plays and then press a button on the HMI
- Another photo is taken, and each cell is compared with the previous one using image processing (`diffCheck.py`)
- If the image processing doesn't return a clear score, a neural network is used to tell if the cell has changed
- `moves.py` is used to "understand" what the player's move was and keep track of the game
- the move is translated and passed to stockfish engine to know what the optimal move is
- Cartesian coordinates are sent to the arduino by the PC for the pick and place
- The Arduino computes Inverse Kinematics and the gripping

---
