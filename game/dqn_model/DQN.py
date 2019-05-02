import os
import random
import numpy as np
from operator import itemgetter
from collections import deque
from keras.models import Sequential, load_model
from keras.layers import Dense
import matplotlib.pyplot as plt

plt.style.use('seaborn')
plt.rcParams['font.family'] = 'IPAexGothic'


ROW=5
STATE_N = ROW*ROW
ACTION_N = ROW*ROW

class DQN():
    def __init__(self, memory = [], history_len=1, memory_size=2000, replay_start_size=32, gamma=0.9, eps=1.0, eps_min=1e-3, final_expl_step=4000, mb_size=32, C=20, n_episodes=1000, max_steps=10):
        self.history_len = history_len
        self.memory_size = memory_size
        self.replay_start_size = replay_start_size
        self.gamma = gamma
        self.eps = eps
        self.eps_min = eps_min
        self.eps_decay = (eps - eps_min) / final_expl_step
        self.final_expl_step = final_expl_step
        self.mb_size = mb_size
        self.C = C
        self.n_episodes = n_episodes
        self.max_steps = max_steps
        self.step = 0
        self.memory = deque(maxlen = self.memory_size)
        for i in memory:
            self.memory.append(i)
        if os.path.exists("Q_network.h5"):
            self.Q = load_model("Q_network.h5")
            print("loading Q-network model")
        else:
            self.Q = self._build_network()
            print("building Q-network model")

        self.target_Q = self._clone_network(self.Q)
        self.target_Q._make_predict_function()

    def _get_optimal_action(self, network, state):
        return np.argmax(network.predict(state.reshape(1, -1)))

    def get_action(self, state):
        if np.random.random() > self.eps:
            self.eps = max(self.eps - self.eps_decay, self.eps_min)
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
        history = np.array([s[0] for s in samples])
        Y = self.target_Q.predict(history)
        actions = [s[1] for s in samples]
        rewards = np.array([s[2] for s in samples])
        future_rewards = np.zeros(self.mb_size)
        new_states_idx = [i for i, s in enumerate(samples) if s[3] is not None]
        new_states = np.array([s[3] for s in itemgetter(*new_states_idx)(samples)])
        new_history = np.hstack([history[new_states_idx, self.env.observation_space.n:], new_states])
        future_rewards[new_states_idx] = np.max(self.target_Q.predict(new_history), axis=1)
        rewards += self.gamma*future_rewards
        for i, r in enumerate(Y):
            Y[i, actions] = rewards[i]
        return history, Y


    def _replay(self):
        history, Y = self._get_samples()
        for i in range(self.mb_size):
            self.Q.train_on_batch(history[i, :].reshape(1, -1), Y[i, :].reshape(1, -1))

    def learn(self, paths):
        self.Q = load_model("Q_network.h5")
        self.target_Q = self._clone_network(self.Q)
        self._replay()

        if self.step % self.C == 0:
            self.target_Q = self._clone_network(self.Q)


    def save_model(self):
        self.target_Q.save("Q_network.h5")



