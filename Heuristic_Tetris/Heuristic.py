#!/usr/bin/env python3
# Run this file to run the engine according to an analytic policy.

import time
import socket
import os
from tetris_heuristic import TetrisEngine
##from tetris_qt import *

#결과 높이를 기반으로 점수를 계산합니다.
def compute_dropped_score_height(engine, good_ijs, cleared):
    score = 0
    for i, c in enumerate(engine.board):
        buf = 0
        for j, v in enumerate(c):
            if j in cleared:
                buf += 1
            elif v or (i, j) in good_ijs:
                score += engine.height - j - buf
    return score

#떨어 뜨린 조각이 얼마나 남았는지에 따라 점수를 계산합니다.
def compute_dropped_score_left(engine, good_ijs, cleared):
    score = 0
    board = engine.board.T
    for j, c in enumerate(board):
        if j in cleared:
            continue
        flag = None
        for i, v in enumerate(c):
            v = v or (i, j) in good_ijs
            if flag is not None and flag != v:
                score += 1
            flag = v
    return score

#생성 된 "구멍"의 수를 기반으로 점수를 계산합니다.
def compute_dropped_score_holes(engine, good_ijs, cleared):
    score = 0
    for i, c in enumerate(engine.board):
        flag = 0
        for j, v in enumerate(c):
            if j in cleared:
                continue
            v = v or (i, j) in good_ijs
            if flag == 0 and v:
                flag = 1
            elif flag == 1 and not v:
                flag = 2
            if flag == 2:
                score += 1
    return score

#휴리스틱 기법을 결합하여 계산
def compute_combined_heuristic(engine, good_ijs, cleared):
    height_score = compute_dropped_score_height(engine, good_ijs, cleared)
    holes_score = compute_dropped_score_holes(engine, good_ijs, cleared)
    left_score = compute_dropped_score_left(engine, good_ijs, cleared)
    return (
        holes_score +
        height_score * 1e-4 +
        left_score
    )

#떨어질 때 점수를 계산
def compute_dropped_score(engine, board, shape, anchor):
    shape, anchor = engine.actions.hard_drop(shape, anchor, board)
    good_ijs = set((anchor[0] + s[0], anchor[1] + s[1]) for s in shape)
    score = 0

    # Finds lines that are cleared.
    board_t = board.T
    cleared = set(
        j
        for j, c in enumerate(board_t)
        if all(v or (i, j) in good_ijs for i, v in enumerate(c))
    )

    # return compute_dropped_score_height(engine, good_ijs, cleared)
    # return compute_dropped_score_holes(engine, good_ijs, cleared)
    return compute_combined_heuristic(engine, good_ijs, cleared)


def compute_helper(engine, shape, anchor, action):
    board = engine.board
    actions = []
    min_score = 10000000
    for i in range(engine.width):
        new_score = compute_dropped_score(engine, board, shape, anchor)
        if new_score < min_score:
            actions = [action] * i + [engine.actions.HARD_DROP]
            min_score = new_score
        if engine.has_dropped(shape, anchor, board):
            break
        shape, new_anchor = engine.actions[action](shape, anchor, board)
        if new_anchor == anchor:
            break
        shape, anchor = engine.actions.soft_drop(shape, new_anchor, board)

    return actions, min_score

#최적화된 steps 계산
def compute_optimal_steps(engine):
    actions = []
    min_score = 10000000  # 매우 큰 숫자
    board = engine.board
    possible_pre_actions = [
        [],
        [engine.actions.ROTATE_LEFT],
        [engine.actions.ROTATE_LEFT, engine.actions.ROTATE_LEFT],
        [engine.actions.ROTATE_RIGHT],
    ]

    for pre_actions in possible_pre_actions:
        shape, anchor = engine.shape, engine.anchor

        # pre-action을 적용합니다.
        for a in pre_actions:
            shape, anchor = engine.actions[a](shape, anchor, board)
            shape, anchor = engine.actions.soft_drop(shape, anchor, board)

        # Tests the best sequence of post-actions.
        for action in [engine.actions.LEFT, engine.actions.RIGHT]:
            new_actions, new_score = compute_helper(engine, shape, anchor, action)
            if new_score < min_score:
                actions = pre_actions + new_actions
                min_score = new_score

    return actions


if __name__ == '__main__':
    """
    app = QApplication([])  # 앱 생성
    tetris = Shape()  # 테트리스 객체 생성
    app.exec_()
    while True:
        steps = compute_optimal_steps(app)
        for step in steps:
            app.step(step)
            print(app)
            time.sleep(0.05)
    """
    os.system('clear')
    engine = TetrisEngine(width=10, height=20)
    steps = compute_optimal_steps(engine)
    #engine.draw_board()

    host = '127.0.0.1'
    port = 9191
    serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv_sock.bind((host,port))
    serv_sock.listen(0)
    clnt_sock, addr = serv_sock.accept()

    os.system('clear')
    for i in range(5):
        print('AI와의 대결을 시작합니다.')
        print(5 - i)
        time.sleep(1)
        os.system('clear')
    while True :
        if engine.line >= 10:
            break
        steps = compute_optimal_steps(engine)
        for step in steps:
            engine.step(step)
            print(engine)
            time.sleep(0.1)

    #clnt_sock.send("\nAWinner is AI!!!".encode())
    print("\nAWinner is AI!!!")



