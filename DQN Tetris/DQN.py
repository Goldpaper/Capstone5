import time
import copy
import tensorflow as tf
import numpy as np
import random
from tetris_dqn import Env
from collections import deque
from keras import backend as K
from keras.layers.convolutional import Conv2D
from keras.layers import Dense, Flatten
from keras.optimizers import RMSprop
from keras.models import Sequential

EPISODE = 50000
GAME_VELOCTY = 0.000001
ACTION_VELCOCITY = 0.000001

ret = [[0] * 84 for _ in range(84)]


class DQNAgent:
    def __init__(self, action_size):
        self.render = False
        #self.load_model = True
        # 상태와 행동의 크기 정의
        self.state_size = (84, 84, 4)
        self.action_size = action_size
        # DQN 하이퍼파라미터
        self.epsilon = 1.
        #입실론 시작, 종료 값
        self.epsilon_start, self.epsilon_end = 1.0, 0.1
        #입실론은 1부터 0.1까지 1000000 스텝동안 감소
        self.exploration_steps = 1000000.
        self.epsilon_decay_step = (self.epsilon_start - self.epsilon_end) \
                                  / self.exploration_steps
        #미니 배치 크기
        self.batch_size = 32
        #학습 시작 (50000스텝 후)
        self.train_start = 50000
        #타깃 모델 업데이트 주기
        self.update_target_rate = 10000
        #감가
        self.discount_factor = 0.99
        # 리플레이 메모리, 최대 크기 400000
        self.memory = deque(maxlen=40000)
        self.no_op_steps = 30
        # 모델과 타겟모델을 생성하고 타겟모델 초기화
        self.model = self.build_model()
        self.target_model = self.build_model()
        self.update_target_model()

        self.optimizer = self.optimizer()

        self.avg_q_max, self.avg_loss = 0, 0

        '''
        # 텐서보드 설정
        self.sess = tf.InteractiveSession()
        K.set_session(self.sess)
        '''

        self.summary_placeholders, self.update_ops, self.summary_op = \
            self.setup_summary()
        #self.summary_writer = tf.summary.FileWriter(
        #    'summary/breakout_dqn', self.sess.graph)
        #self.sess.run(tf.global_variables_initializer())

        #if self.load_model:
        #    self.model.load_weights("./save_model/breakout_dqn.h5")

    def load_model(self, filename):
        self.model.load_weights(filename)

        # Huber Loss를 이용하기 위해 최적화 함수를 직접 정의
    def optimizer(self):
        a = K.placeholder(shape=(None,), dtype='int32')
        y = K.placeholder(shape=(None,), dtype='float32')

        prediction = self.model.output

        a_one_hot = K.one_hot(a, self.action_size)
        q_value = K.sum(prediction * a_one_hot, axis=1)
        error = K.abs(y - q_value)

        quadratic_part = K.clip(error, 0.0, 1.0)
        linear_part = error - quadratic_part
        loss = K.mean(0.5 * K.square(quadratic_part) + linear_part)

        # lr = 0.00025
        optimizer = RMSprop(lr=0.001, epsilon=0.01)
        updates = optimizer.get_updates(self.model.trainable_weights, [], loss)
        train = K.function([self.model.input, a, y], [loss], updates=updates)

        return train

    # 상태가 입력, 큐함수가 출력인 인공신경망 생성
    def build_model(self):
        model = Sequential()
        model.add(Conv2D(32, (8, 8), strides=(4, 4), activation='relu',
                         input_shape=self.state_size))
        model.add(Conv2D(64, (4, 4), strides=(2, 2), activation='relu'))
        model.add(Conv2D(64, (3, 3), strides=(1, 1), activation='relu'))
        model.add(Flatten())
        model.add(Dense(50, activation='relu'))
        model.add(Dense(self.action_size))
        model.summary()
        return model

    # 타겟 모델을 모델의 가중치로 업데이트
    def update_target_model(self):
        self.target_model.set_weights(self.model.get_weights())

    # 입실론 탐욕 정책으로 행동 선택
    def get_action(self, history):
        history = np.float32(history / 255.0)
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        else:
            q_value = self.model.predict(history)
            return np.argmax(q_value[0])

    # 샘플 <s, a, r, s'>을 리플레이 메모리에 저장
    def append_sample(self, history, action, reward, next_history):
        self.memory.append((history, action, reward, next_history))

    # 리플레이 메모리에서 무작위로 추출한 배치로 모델 학습
    def train_model(self):
        if self.epsilon > self.epsilon_end:
            self.epsilon -= self.epsilon_decay_step

        mini_batch = random.sample(self.memory, self.batch_size)

        history = np.zeros((self.batch_size, self.state_size[0],
                            self.state_size[1], self.state_size[2]))
        next_history = np.zeros((self.batch_size, self.state_size[0],
                                 self.state_size[1], self.state_size[2]))
        target = np.zeros((self.batch_size,))
        action, reward = [], []

        for i in range(self.batch_size):
            history[i] = np.float32(mini_batch[i][0] / 255.)
            next_history[i] = np.float32(mini_batch[i][3] / 255.)
            action.append(mini_batch[i][1])
            reward.append(mini_batch[i][2])

        target_value = self.target_model.predict(next_history)

        for i in range(self.batch_size):
            target[i] = reward[i] + self.discount_factor * np.amax(target_value[i])

        loss = self.optimizer([history, action, target])
        self.avg_loss += loss[0]

    # 각 에피소드 당 학습 정보를 기록
    def setup_summary(self):
        episode_total_reward = tf.Variable(0.)
        episode_avg_max_q = tf.Variable(0.)
        episode_duration = tf.Variable(0.)
        episode_avg_loss = tf.Variable(0.)

        tf.summary.scalar('Total Reward/Episode', episode_total_reward)
        tf.summary.scalar('Average Max Q/Episode', episode_avg_max_q)
        tf.summary.scalar('Duration/Episode', episode_duration)
        tf.summary.scalar('Average Loss/Episode', episode_avg_loss)
        tf.train.AdamOptimizer
        summary_vars = [episode_total_reward, episode_avg_max_q,
                        episode_duration, episode_avg_loss]
        summary_placeholders = [tf.placeholder(tf.float32) for _ in
                                range(len(summary_vars))]
        update_ops = [summary_vars[i].assign(summary_placeholders[i]) for i in
                      range(len(summary_vars))]
        summary_op = tf.summary.merge_all()
        return summary_placeholders, update_ops, summary_op


"""
# 학습속도를 높이기 위해 흑백화면으로 전처리
def pre_processing(observe):
    processed_observe = np.uint8(
        resize(rgb2gray(observe), (84, 84), mode='constant') * 255)
    return processed_observe
"""

def pre_processing(curr_map,curr_block_pos):
    copy_map = copy.deepcopy(curr_map)
    ny, nx = 4.20, 10.5
    for n in curr_block_pos:
        copy_map[n[0]][n[1]] = 1
    for n in range(20):
        for m in range(4):
            for i in range(int(n * ny), int(n * ny + ny)):
                for j in range(int(m * nx), int(m * nx + nx)):
                    ret[i][j] = copy_map[n][m]
    return ret

"""
if __name__ == "__main__":
    # 환경과 DQN 에이전트 생성
    env = gym.make('BreakoutDeterministic-v4')
    agent = DQNAgent(action_size=3)

    scores, episodes, global_step = [], [], 0

    for e in range(EPISODES):
        done = False
        dead = False

        step, score, start_life = 0, 0, 5
        observe = env.reset()

        for _ in range(random.randint(1, agent.no_op_steps)):
            observe, _, _, _ = env.step(1)

        state = pre_processing(observe)
        history = np.stack((state, state, state, state), axis=2)
        history = np.reshape([history], (1, 84, 84, 4))

        while not done:
            if agent.render:
                env.render()
            global_step += 1
            step += 1

            # 바로 전 4개의 상태로 행동을 선택
            action = agent.get_action(history)
            # 1: 정지, 2: 왼쪽, 3: 오른쪽
            if action == 0:
                real_action = 1
            elif action == 1:
                real_action = 2
            else:
                real_action = 3

            # 선택한 행동으로 환경에서 한 타임스텝 진행
            observe, reward, done, info = env.step(real_action)
            # 각 타임스텝마다 상태 전처리
            next_state = pre_processing(observe)
            next_state = np.reshape([next_state], (1, 84, 84, 1))
            next_history = np.append(next_state, history[:, :, :, :3], axis=3)

            agent.avg_q_max += np.amax(
                agent.model.predict(np.float32(history / 255.))[0])

            if start_life > info['ale.lives']:
                dead = True
                start_life = info['ale.lives']

            reward = np.clip(reward, -1., 1.)
            # 샘플 <s, a, r, s'>을 리플레이 메모리에 저장 후 학습
            agent.append_sample(history, action, reward, next_history, dead)

            if len(agent.memory) >= agent.train_start:
                agent.train_model()

            # 일정 시간마다 타겟모델을 모델의 가중치로 업데이트
            if global_step % agent.update_target_rate == 0:
                agent.update_target_model()

            score += reward

            if dead:
                dead = False
            else:
                history = next_history

            if done:
                # 각 에피소드 당 학습 정보를 기록
                if global_step > agent.train_start:
                    stats = [score, agent.avg_q_max / float(step), step,
                             agent.avg_loss / float(step)]
                    for i in range(len(stats)):
                        agent.sess.run(agent.update_ops[i], feed_dict={
                            agent.summary_placeholders[i]: float(stats[i])
                        })
                    summary_str = agent.sess.run(agent.summary_op)
                    agent.summary_writer.add_summary(summary_str, e + 1)

                print("episode:", e, "  score:", score, "  memory length:",
                      len(agent.memory), "  epsilon:", agent.epsilon,
                      "  global_step:", global_step, "  average_q:",
                      agent.avg_q_max / float(step), "  average loss:",
                      agent.avg_loss / float(step))

                agent.avg_q_max, agent.avg_loss = 0, 0

        # 1000 에피소드마다 모델 저장
        if e % 1000 == 0:
            agent.model.save_weights("./save_model/breakout_dqn.h5")
"""

if __name__ == "__main__":
    # 환경과 DQN 에이전트 생성
    tetris = Env()
    agent = DQNAgent(action_size=3)
    #agent.load_model("./save_model/breakout_dqn.h5")
    """agent.predict_classes("./save_model/breakout_dqn.h5")"""

    #state 및 history 정의
    state = pre_processing(tetris.map, tetris._get_curr_block_pos())
    history = np.stack((state, state, state, state), axis = 2)
    history = np.reshape([history], (1, 84, 84, 4))

    start_time = time.time()
    action_time = time.time()
    global_step = 0

    for epi in range(EPISODE):
        step = 0
        #모델 저장하기
        if epi % 50 == 0:
            agent.model.save_weights("./save_model/breakout_dqn.h5")
        while True:
            end_time = time.time()
            if end_time - action_time >= ACTION_VELCOCITY:
                # 바로 전 4개의 상태로 행동을 선택
                global_step += 1
                step += 1
                action = agent.get_action(history)
                reward = tetris.step(action)

                # 다음 상태 전처리
                next_state = pre_processing(tetris.map, tetris._get_curr_block_pos())
                next_state = np.reshape([next_state], (1, 84, 84, 1))
                next_history = np.append(next_state, history[:, :, :, :3], axis=3)

                agent.avg_q_max += np.amax(agent.model.predict(np.float32(history / 255.))[0])
                agent.append_sample(history, action, reward, next_history)

                if len(agent.memory) >= agent.train_start:
                    agent.train_model()

                # 일정 시간마다 타겟모델을 모델의 가중치로 업데이트
                if global_step % agent.update_target_rate == 0:
                    agent.update_target_model()

                history = next_history

                action_time = time.time()

            if end_time - start_time >= GAME_VELOCTY:
                # game over
                if tetris.is_game_end():
                    '''
                    if global_step > agent.train_start:
                        stats = [tetris.score, agent.avg_q_max / float(global_step), global_step,
                                 agent.avg_loss / float(global_step)]
                        for i in range(len(stats)):
                            agent.sess.run(agent.update_ops[i], feed_dict={
                                agent.summary_placeholders[i]: float(stats[i])
                            })
                        summary_str = agent.sess.run(agent.summary_op)
                        agent.summary_writer.add_summary(summary_str, epi + 1)
                    '''
                    print('episode:{}, score:{}, epsilon:{}, global step:{}, avg_qmax:{}, memory:{}'.
                          format(epi, tetris.score, agent.epsilon, global_step,
                                 agent.avg_q_max / float(step), len(agent.memory)))
                    tetris.reset()
                    agent.avg_q_max, agent.avg_loss = 0, 0
                    break
                else:
                    buffer = tetris.step(0)
                start_time = time.time()

