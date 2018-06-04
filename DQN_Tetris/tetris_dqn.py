"""
인하대학교 컴퓨터공확과 캡스톤 5팀
 => OpenSource 테트리스 프로그램입니다.
Tetris 프로그램 실행 및 화면 구성 관리 코드
SourceCode : www.github.com/goldpaper/Capstone5

블럭 파괴 시 : (라인당) 10점
빈칸 생성시 패널티 1점, 빈칸 제거시 보상 1점
높이에 따른 보상 (0 ~ 1점을 2차함수 기반으로 적립)
"""

import time
import numpy as np
import tkinter as tk
from PIL import ImageTk, Image
import random


PhotoImage = ImageTk.PhotoImage
np.random.seed(1)
UNIT = 30  # 픽셀 수
HEIGHT = 20  # 그리드 세로
WIDTH = 10   # 그리드 가로
MID = (WIDTH / 2 - 1) * UNIT # 블록 시작 점
dy = [UNIT, 0, 0]       # ay
# ction에 해당하는 y좌표 plus값
dx = [0, UNIT, -UNIT]   # action에 해당하는 y좌표 plus값
PLUS_SCORE = 10.0
basic_counter_str = 'test : '
basic_score_str = 'score : '
blocks = 0
block_kinds = 0
zero_action = 0
PreY = 0
rote_action = 0
move_action = 0


class Env(tk.Tk):
    def __init__(self):
        super(Env, self).__init__()

        self.blocks = 0
        self.score = 0.0
        self.score_weight = []
        self.counter = 0
        self.PreY = 0
        self.zero_action = 0
        self.move_action = 0
        self.rote_action = 0
        #테트리스 화면 hole 갯수 파악
        self.hole=0
        for i in range(HEIGHT):
            if i <= 2:
                self.score_weight.append(0.0)
            else:
                self.score_weight.append((i-2)*(i-2)*0.00082976)
        self.action_space = ['d', 'l', 'r']
        self.action_size = len(self.action_space)
        self.color = ["white"]
        self.block_kind = len(self.color)

        self.curr_block = np.random.randint(self.block_kind)
        self.canvas, self.counter_board, self.score_board = self._build_canvas()
        self.map = [[0]*WIDTH for _ in range(HEIGHT)]

    def _get_curr_block_pos(self):
        ret = []
        for n in range(4):
            s = (self.canvas.coords(self.block[n]))
            y = int(s[1] / UNIT)
            x = int(s[0] / UNIT)
            ret.append([y,x])
        return ret

    def _clear_map(self):
        for n in range(HEIGHT):
            for m in range(WIDTH):
                self.map[n][m] = 0

    def _erase_down_canvas(self, iy):
        for crect in self.canvas.find_withtag("rect"):
            if int(self.canvas.coords(crect)[1]) == iy*UNIT:
                self.canvas.delete(crect)

    def _move_all_canvas_down(self, iy):
        for crect in self.canvas.find_withtag("rect"):
            if int(self.canvas.coords(crect)[1]) < iy*UNIT:
                self.canvas.move(crect, 0, UNIT)

    def _add_canvas(self):
        pos = self.make_block()

        rect1 = self.canvas.create_rectangle(pos[0][0], pos[0][1], pos[0][0] + UNIT,
                                             pos[0][1] + UNIT, fill=self.color[self.curr_block],
                                             tag="rect")
        rect2 = self.canvas.create_rectangle(pos[1][0], pos[1][1], pos[1][0] + UNIT,
                                             pos[1][1] + UNIT, fill=self.color[self.curr_block],
                                             tag="rect")
        rect3 = self.canvas.create_rectangle(pos[2][0], pos[2][1], pos[2][0] + UNIT,
                                             pos[2][1] + UNIT, fill=self.color[self.curr_block],
                                             tag="rect")
        rect4 = self.canvas.create_rectangle(pos[3][0], pos[3][1], pos[3][0] + UNIT,
                                             pos[3][1] + UNIT, fill=self.color[self.curr_block],
                                             tag="rect")

        self.block = [rect1, rect2, rect3, rect4]
        self.canvas.pack()

    def _build_canvas(self):
        canvas = tk.Canvas(self, bg='black',
                           height=HEIGHT * UNIT,
                           width=(WIDTH + 5)* UNIT)
        counter_board = canvas.create_text((WIDTH + 3) * UNIT, int(HEIGHT / 4 * UNIT),
                           fill = "white",
                           font = "Times 10 bold",
                           text = basic_counter_str + str(int(self.counter)))

        score_board = canvas.create_text((WIDTH + 3)*UNIT, int(HEIGHT/2*UNIT),
                           fill = "white",
                           font = "Times 10 bold",
                           text = basic_score_str + str(int(self.score)))

        # 그리드 생성
        for c in range(0, (WIDTH + 1)* UNIT, UNIT):  # 0~400 by 80
            x0, y0, x1, y1 = c, 0, c, HEIGHT * UNIT
            canvas.create_line(x0, y0, x1, y1, fill = 'white')
        '''
        for r in range(0, HEIGHT * UNIT, UNIT):  # 0~400 by 80
            x0, y0, x1, y1 = 0, r, HEIGHT * UNIT, r
            canvas.create_line(x0, y0, x1, y1)
        '''

        # 캔버스에 이미지 추가
        pos = self.make_block()
        #self.zero_action = 0
        rect1 = canvas.create_rectangle(pos[0][0], pos[0][1], pos[0][0] + UNIT,
                                        pos[0][1] + UNIT, fill=self.color[self.curr_block],
                                        tag="rect")
        rect2 = canvas.create_rectangle(pos[1][0], pos[1][1], pos[1][0] + UNIT,
                                        pos[1][1] + UNIT, fill=self.color[self.curr_block],
                                        tag="rect")
        rect3 = canvas.create_rectangle(pos[2][0], pos[2][1], pos[2][0] + UNIT,
                                        pos[2][1] + UNIT, fill=self.color[self.curr_block],
                                        tag="rect")
        rect4 = canvas.create_rectangle(pos[3][0], pos[3][1], pos[3][0] + UNIT,
                                        pos[3][1] + UNIT, fill=self.color[self.curr_block],
                                        tag="rect")
        self.block = [rect1,rect2,rect3,rect4]
        canvas.pack()
        return canvas,counter_board,score_board

    def make_block(self):
        #print("b")



        x, y = 0, -UNIT
        #pos = [[[x, y], [x + UNIT, y], [x + UNIT, y + UNIT], [x, y + UNIT]],
        #       [[x, y], [x + UNIT, y], [x + UNIT, y + UNIT], [x, y + UNIT]],
        #       [[x, y], [x + UNIT, y], [x + UNIT, y + UNIT], [x, y + UNIT]],
        #       [[x, y], [x + UNIT, y], [x + UNIT, y + UNIT], [x, y + UNIT]], ]
        pos = [#[[x, y], [x + UNIT, y], [x + UNIT, y + UNIT], [x + UNIT + UNIT, y]],
               #[[x, y], [x, y + UNIT], [x, y + UNIT + UNIT], [x - UNIT, y+UNIT]],
               #[[x, y], [x + UNIT, y], [x + UNIT, y - UNIT], [x + UNIT + UNIT, y]],
               #[[x, y], [x, y + UNIT], [x, y +UNIT + UNIT], [x + UNIT, y + UNIT]],
               #[[x, y], [x, y - UNIT], [x - UNIT, y], [x, y - UNIT - UNIT]],
               #[[x, y], [x + UNIT, y], [x + UNIT, y + UNIT], [x + UNIT + UNIT, y]],
               [[x, y], [x + UNIT, y], [x + UNIT, y + UNIT], [x, y + UNIT]],
               [[x, y], [x, y + UNIT], [x, y + UNIT +UNIT], [x, y + UNIT  + UNIT + UNIT]]]
        #return pos[0]
        self.block_kinds = random.randrange(0, 2)
        return pos[self.block_kinds]

    def rotate_line(self):
        abc = self._get_curr_block_pos()
        #for n in range(4) :
        #    print(abc[n][1], abc[n][0])
        #    self.map[abc[n][0]][abc[n][1]] = 1

        #time.sleep(1)
        if abc[1][0]  < HEIGHT /3 :
            if self.blocks == 0:
                if abc[1][1] < MID:
                    x = abc[1][1] * UNIT
                    y = abc[1][0] *UNIT
                elif abc[1][1] > MID :
                    x = (abc[1][1] - 3) *UNIT
                    y = abc[1][0] *UNIT
            elif self.blocks == 1:
                x = abc[1][1] *UNIT
                y = abc[0][0] *UNIT

            if x >= 6*UNIT:
                x = 6* UNIT
            if y >= (HEIGHT-4)*UNIT :
                y = (HEIGHT-4)*UNIT



            #print(x, y)
            pos = [[[x, y], [x + UNIT, y], [x+ UNIT+ UNIT, y], [x+ UNIT+ UNIT+ UNIT, y]],
                   [[x, y], [x, y + UNIT], [x , y + UNIT + UNIT], [x, y+ UNIT+ UNIT+ UNIT]]]
            conc = 0
            for n in range(4):
                FutY = int(pos[self.blocks][n][1] / UNIT)
                FutX = int(pos[self.blocks][n][0] / UNIT)
                if self.map[FutY][FutX] == 1 :
                    conc = 1
                    break;
            if conc == 0 :
                for n in range(4) :
                    self.canvas.delete(self.block[n])
                self._add_canvas_line(pos[self.blocks])
                self.blocks = self.blocks + 1
                self.blocks = self.blocks % 2



    def _add_canvas_line(self, pos):

        rect1 = self.canvas.create_rectangle(pos[0][0], pos[0][1], pos[0][0] + UNIT,
                                             pos[0][1] + UNIT, fill=self.color[self.curr_block],
                                             tag="rect")
        rect2 = self.canvas.create_rectangle(pos[1][0], pos[1][1], pos[1][0] + UNIT,
                                             pos[1][1] + UNIT, fill=self.color[self.curr_block],
                                             tag="rect")
        rect3 = self.canvas.create_rectangle(pos[2][0], pos[2][1], pos[2][0] + UNIT,
                                             pos[2][1] + UNIT, fill=self.color[self.curr_block],
                                             tag="rect")
        rect4 = self.canvas.create_rectangle(pos[3][0], pos[3][1], pos[3][0] + UNIT,
                                             pos[3][1] + UNIT, fill=self.color[self.curr_block],
                                             tag="rect")

        self.block = [rect1, rect2, rect3, rect4]

       # self.canvas.update()
        #self.canvas.pack()

        #self.canvas.coords(self.block)

    def reset(self):
        self.score = 0.0
        self.counter += 1
        self.canvas.itemconfigure(self.counter_board,
                                  text=basic_counter_str + str(int(self.counter)))
        self.canvas.itemconfigure(self.score_board,
                                  text=basic_score_str + str(int(self.score)))
        self.update()
        self.canvas.delete("rect")
        self._clear_map()
        self._add_canvas()

    def step(self, action):
        self.render()
        reward = self.move(action)
        if reward >= 0.00000:
            # make new block!
            self.curr_block = np.random.randint(self.block_kind)
            self._add_canvas()
        self.canvas.tag_raise(self.block)
        if reward < 0.00000:
            return 0.0
        else:
            return reward

    def rotate(self):
        #print(self.curr_block)
        if self.block_kinds == 0 : # ㅁ
            return ;
    #    elif self.curr_block == 1 : # ㄴ

    #    elif self.curr_block == 2: # ㄱ

        elif self.block_kinds == 1: # ㅣ
            #print("llll")
            #if self.aaa == 0 :
            #self.blocks = self.blocks % 2
            self.rotate_line()
            #self.aaa = 1

    def blockdown(self):
        abc = self._get_curr_block_pos()
        for n in range(4) :
            for m in range(HEIGHT - abc[n][0]) :
                if map[abc[n][1]] == 1 :
                    return 1


    def possible_to_move(self, action):

        #if action ==3:
            #print("rotate")
        #    self.rotate()
        #    return 4
        for n in range(len(self.block)):
            s = self.canvas.coords(self.block[n])
            y = s[1] + dy[action]
            x = s[0] + dx[action]

            # 범위밖 - stay
            if x >= WIDTH * UNIT or x < 0:
                return 1
            ny = int(y/UNIT)
            nx = int(x/UNIT)

            # 마지막줄 - add canvas
            if y >= HEIGHT * UNIT:
                return 2
            if self.map[ny][nx] == 1:
                if action == 0:
                    return 2
                else:
                    return 1
        # 이동가능함 - move
        return 3

    def is_map_horizon(self):
        for n in range(HEIGHT - 1, 0, -1):
            cnt = 0
            for m in range(WIDTH):
                if self.map[n][m] != 1:
                    break
                cnt += 1
            if cnt == WIDTH:
                return n
        return -1

    def moves(self, mov):
        self.move_action = int(mov / 3)
        self.rote_action = mov % 3
        base_action = np.array([0, 0])
        for n in range(self.rote_action) :
            self.rotate()
        #print(self.move_action)
        #for n in range(self.move_action):
            #base_action[1] += dy[2]
        base_action[0] += (self.move_action)*dx[1]
        #print("move", self.move_action,"base",base_action[0])
        a = base_action[0]

        for n in range(4):
            k = self._get_curr_block_pos()[n][1]*UNIT + a
            if k >= (WIDTH) * UNIT:
                base_action[0] -= UNIT

        for n in range(4):
            self.canvas.move(self.block[n], base_action[0], base_action[1])





    def move(self, action):
        #self.zero_action = 1
       # print(action)
        #self.move_action = action / 3
        #self.rote_action = action % 3
        #self.zero_action = 1

        ret = 0.0
        base_action = np.array([0, 0])
        #time.sleep(0.1)
        if self.zero_action == 0:
            self.zero_action = 1
            #print(action)
            if action != 0:
                self.moves(action-1)
            #print(action)
            #time.sleep(1)
            action = 0
            #flag = self.possible_to_move(action)
            flag = 0
        else :
            action = 0
            flag = self.possible_to_move(action)

        # 해당 자리에 고정시켜줌
        if flag == 2:
            self.zero_action = 0
            #print(self.zero_action)
            self.blocks = 0
            for n in range(4):
                s = (self.canvas.coords(self.block[n]))
                y = int(s[1] / UNIT)
                x = int(s[0] / UNIT)

                # Heuristic1 (높이에 따른 보상)
                self.score += self.score_weight[y]
                ret += self.score_weight[y]
                self.map[y][x] = 1

            # Heuristic1 (높이에 따른 보상 차등 추가)
            self.score = (y * y) / 400

            # Heuristic2 (빈칸에 따른 점수)
            temp_hole = 0;
            for j in range(0, 18):
                for k in range(0, 10):
                    if self.map[j][k] > self.map[j+1][k]:
                        temp_hole = temp_hole + 1
            self.score += self.hole - temp_hole
            self.hole = temp_hole

            # 한줄이 꽉차있으면 비워주고 점수를 더해줌
            break_cnt = 0
            while True:
                y = self.is_map_horizon()
                if y == -1:
                    break
                self._erase_down_canvas(y)
                self._move_all_canvas_down(y)
                break_cnt += 1
                for m in range(WIDTH):
                    for n in range(y , 2, -1):
                        self.map[n][m] = self.map[n-1][m]
            self.score += PLUS_SCORE * break_cnt
            ret += PLUS_SCORE * break_cnt
            self.canvas.itemconfigure(self.score_board,
                                  text = basic_score_str + str(int(self.score)))
            print(ret)
            return ret

        # move
        elif flag == 3:
            base_action[1] += dy[action]
            base_action[0] += dx[action]
            for n in range(4):
                self.canvas.move(self.block[n], base_action[0], base_action[1])

        self.canvas.coords(self.block)
        return -1.0

    def is_game_end(self):
        for n in range(1):
            for m in range(WIDTH):
                if self.map[n][m] == 1:
                    return True
        return False

    def render(self):
        # 게임 속도 조정
        self.update()


