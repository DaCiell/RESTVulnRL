"""
This part of code is the Q learning brain, which is a brain of the agent.
All decisions are made in here.

View more on my tutorial page: https://morvanzhou.github.io/tutorials/
"""

import numpy as np
import pandas as pd


class QLearningTable:
    def __init__(self, actions, learning_rate=0.01, reward_decay=0.9, e_greedy=0.9):
        self.actions = actions  # a list
        self.lr = learning_rate
        self.gamma = reward_decay
        self.epsilon = e_greedy
        self.q_table = pd.DataFrame(columns=self.actions, dtype=np.float64)
        pd.set_option('display.max_columns', None)
        pd.options.display.float_format = lambda x: '' if x == 0 else '{:.2f}'.format(x)

    def choose_action(self, observation, additional_data, excluded_actions=[]):
        self.check_state_exist(observation, additional_data)
        # action selection
        available_actions = [action for action in self.actions if action not in excluded_actions]
        if np.random.uniform() < self.epsilon:
            # choose best action
            state_action = self.q_table.loc[observation, available_actions]
            # some actions may have the same value, randomly choose on in these actions
            action = np.random.choice(state_action[state_action == np.max(state_action)].index)
        else:
            # choose random action
            action = np.random.choice(available_actions)
        return action

    def choose_action_restrict(self, observation, additional_data, sequence):
        self.check_state_exist(observation, additional_data)
        columns = []
        for parameter in sequence:
            columns.append(parameter.num)
        restrict_table = self.q_table.loc[:, columns]
        state_action = restrict_table.loc[observation, :]
        if np.random.uniform() < self.epsilon:
            # some actions may have the same value, randomly choose on in these actions
            action = np.random.choice(state_action[state_action == np.max(state_action)].index)
        else:
            # choose random action
            action = np.random.choice(columns)
        return action

    def learn(self, s, a, r, s_, additional_data):
        self.check_state_exist(s_, additional_data)
        q_predict = self.q_table.loc[s, a]
        if s_ != 'terminal':
            q_target = r + self.gamma * self.q_table.loc[s_, :].max()  # next state is not terminal
        else:
            q_target = r  # next state is terminal
        self.q_table.loc[s, a] += self.lr * (q_target - q_predict)  # update

    def check_state_exist(self, state, additional_data=None):
        if state not in self.q_table.index:
            self.q_table.loc[state] = 0.0
            if additional_data:
                for col in additional_data:
                    self.q_table[col] = self.q_table[col].add(additional_data[col])
