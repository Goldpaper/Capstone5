import os
import time

pid = os.fork()

if pid == 0:
    os.system('python ./DQN\0Tetris/DQN.py')
    print('인공지능 실행')

else:
    #사람 실행 파일 호출
    print('사람 실행')
