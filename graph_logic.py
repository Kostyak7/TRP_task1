import numpy as np
import networkx as nx
import config as cf


P_dict = {  
    1: cf.P1
}
V0 = cf.V0_A
max_computed_t = 1


def get_matrix(t_: int = 1) -> np.matrix:
    global P_dict
    if t_ not in P_dict:
        for t in (max_computed_t + 1, t_ + 1):
            P_dict[t] = np.dot(P_dict[t - 1], P_dict[t - 1])
        max_computed_t = t_
    return P_dict[t_]


def get_vector(t_: int = 1) -> np.array:
    return np.dot(V0, get_matrix(t_))


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
            

def get_graph(P_: np.matrix) -> nx.DiGraph:
    G = nx.from_numpy_array(P_, create_using=nx.DiGraph)
    for i in range(len(P_)):
        G.nodes[i]['label'] = str(i)
        for j in range(len(P_)):
            if P_[i, j] > 0:
                G[i][j]['label'] = str(round(P_[i, j], 2))
    return G
