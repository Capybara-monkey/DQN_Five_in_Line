import os
import random
import numpy as np
from operator import itemgetter
from collections import deque
from keras.models import Sequential, load_model
from keras.layers import Dense
import matplotlib.pyplot as plt
import tensorflow as tf
from ..models import Epsilon

plt.style.use('seaborn')
plt.rcParams['font.family'] = 'IPAexGothic'

graph = tf.get_default_graph()
ROW=15
STATE_N = ROW*ROW
ACTION_N = ROW*ROW

class DQN():
    def __init__(self, memory_size=2000, gamma=0.9, eps=1.0, eps_min=1e-3, final_expl_step=4000, mb_size=20, C=20):
        self.memory_size = memory_size
        self.gamma = gamma
        self.eps_db = Epsilon.objects.get(data_id=1)
        self.eps = self.eps_db.eps
        self.eps_min = eps_min
        self.eps_decay = (eps - eps_min) / final_expl_step
        self.mb_size = mb_size
        self.step = 0
        self.memory = deque(maxlen = self.memory_size)
        if os.path.exists("Q_network.h5"):
            self.Q = load_model("Q_network.h5")
            print("loading Q-network model")
        else:
            self.Q = self._build_network()
            print("building Q-network model")

        if os.path.exists("Q_Target_network.h5"):
            self.target_Q = load_model("Q_Target_network.h5")
        else:
            self.target_Q = self._clone_network(self.Q)

        self.target_Q._make_predict_function()


    def set_memory(self, memory):
        self.memory = deque(maxlen = self.memory_size)
        for i in memory:
            self.memory.append(i)

    def get_memory(self):
        return list(self.memory)

    def _get_optimal_action(self, network, state):
        return network.predict(state.reshape(1, -1))

    def get_action(self, state):
        if np.random.rand() < self.eps:
            self.eps = max(self.eps - self.eps_decay, self.eps_min)
            self.eps_db.eps = self.eps
            self.eps_db.save()
            print("Random Action")
            return np.random.randint(0,ACTION_N)
        else:
            print("Optimal Action")
            return self._get_optimal_action(self.target_Q, state)

    def remember(self, state, action, reward, new_state, done):
        self.memory.append([state, action, reward, new_state if not done else None])

    def _build_network(self):
        nn = Sequential()
        nn.add(Dense(64, activation="relu", input_dim=STATE_N))
        nn.add(Dense(64, activation="relu"))
        nn.add(Dense(32, activation="relu"))
        nn.add(Dense(ACTION_N))
        nn.compile(optimizer='adam', loss='mse', metrics=['mae'])
        return nn

    def _clone_network(self, nn):
        clone = self._build_network()
        clone.set_weights(nn.get_weights())
        return clone

    def _get_samples(self):
        samples = random.sample(self.memory, self.mb_size)
        states = np.array([s[0] for s in samples])
        Y = self.target_Q.predict(states)
        actions = [s[1] for s in samples]
        rewards = np.array([s[2] for s in samples])
        future_rewards = np.zeros(self.mb_size)
        new_states_idx = [i for i, s in enumerate(samples) if s[3] is not None]
        print(new_states_idx)
        new_states = np.array([s[3] for s in itemgetter(*new_states_idx)(samples)])
        future_rewards[new_states_idx] = np.max(self.target_Q.predict(new_states), axis=1)
        rewards += self.gamma*future_rewards
        for i, r in enumerate(Y):
            Y[i, actions] = rewards[i]
        return states, Y

    def replay(self):
        if len(self.memory) >= self.mb_size:
            print("Start Replay")
            states, Y = self._get_samples()
            for i in range(self.mb_size):
                global graph
                with graph.as_default():
                    self.Q.fit(states.reshape(-1, STATE_N), Y.reshape(-1, ACTION_N))
                print("finish training")

    def save_Q_Target(self):
        self.Q_target.save("Q_Target_network.h5")

    def save_Q(self):
        self.Q.save("Q_network.h5")

    def update_target_Q(self):
        global graph
        with graph.as_default():
            self.Q_target = self._clone_network(self.Q)
        print("Update Q_target")
