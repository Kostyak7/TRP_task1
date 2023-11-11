from pyvis.network import Network
from graph_logic import *
import dash_core_components as dcc


def main() -> None:
    viz = Network(directed=True, notebook=False)
    
    G = get_graph(get_matrix(1))
    viz.from_nx(G, show_edge_weights=True)
    
    viz.show('test1.html', notebook=False)