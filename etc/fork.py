import os
import time

if __name__ == '__main__':
    pid = os.fork()
    if pid == 0:
        print('AI execute')
        os.execl('../Heuristic_Tetris/Heuristic.py','../Heuristic_Tetris/Heuristic.py')
    else:
        print('Human Execute')
        os.execl('../Heuristic_Tetris/tetris.py','../Heuristic_Tetris/tetris.py')


