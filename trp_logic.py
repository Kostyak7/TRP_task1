import numpy as np
import networkx as nx
import config as cf


class Logic:
    def __init__(self):
        self.P_dict = {
            1: cf.P1
            }
        self.V0 = cf.V0_A
        self.max_computed_t = 1
        self.N = cf.N
    
    def set_matrix(self, P_: np.matrix) -> None:
        self.P_dict = {
            1: P_
        }
        self.max_computed_t = 1
    
    def set_vector(self, V0_: np.array) -> None:
        self.V0 = V0_
    
    def get_dimension(self) -> int:
        return len(self.P_dict[1])

    def get_matrix(self, t_: int = 1) -> np.matrix:
        if t_ not in self.P_dict:
            for t in range(self.max_computed_t + 1, t_ + 1):
                self.P_dict[t] = np.dot(self.P_dict[t - 1], self.P_dict[1])
            self.max_computed_t = t_
        return self.P_dict[t_]

    def get_vector(self, t_: int = 1) -> np.array:
        if t_ == 0:
            return self.V0
        return np.array(np.dot(self.V0, self.get_matrix(t_)))[0]
    
    def get_graph(self, P_: np.matrix) -> nx.DiGraph:
        G = nx.from_numpy_array(P_, create_using=nx.DiGraph)
        for i in range(len(P_)):
            G.nodes[i]['label'] = str(i)
            G.nodes[i]['title'] = str(i)
            for j in range(len(P_)):
                if P_[i, j] > 0:
                    G[i][j]['label'] = str(round(P_[i, j], 2))
        return G
    
    def get_trajectory(self, t_: int) -> np.array:
        tr = np.zeros((t_ + 1), dtype=int)
        d = self.get_dimension()
        tr[0] = np.random.choice(np.arange(d), p=self.get_vector(0))
        for i in range(1, t_ + 1):
            v = np.zeros((d))
            P = self.get_matrix(i)
            for j in range(d):
                v[j] = P[tr[i - 1], j]
            tr[i] = np.random.choice(np.arange(d), p=v)
        return tr
    
    def get_trajectory_endings(self, t_: int) -> list:
        return [self.get_trajectory(t_)[-1] for _ in range(self.N)]

    def get_statistic_vector(self, t_: int) -> np.array:
        vec = np.zeros((self.get_dimension()))
        trs = self.get_trajectory_endings(t_)
        for i in range(len(trs)):
            vec[trs[i]] += 1
        # for i in range(len(self.P)):
        #     vec[i] /= N
        return vec / self.N


def print_matrix(P_: np.matrix, t_: int = 1) -> None:
    print(f'P({t_}) =', end='\t')
    for i in range(len(P_)):
        print(end='\t|\t')
        for j in range(len(P_[i])):
            print(round(P_[i][j], 2), end='\t')
        print('|\n')


def print_vector(V_: np.array, t_: int = 1) -> None:
    print(f'V({t_}) = (', end='')
    for i in range(len(V_)):
        if i + 1 == len(V_):
            print(round(V_[i], 2), end=')')
        else:
            print(round(V_[i], 2), end=',\t')
            