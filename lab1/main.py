import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import numba as nb
import multiprocessing
from functools import partial
from random import randint
from time import time


NODES = 200
EDGES = randint(NODES, NODES * 2)
MAX_WEIGHT = 5

@nb.njit
def init_res(dist: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    result = dist.copy()
    next_node = np.full((NODES, NODES), np.inf)

    for i in range(NODES):
        for j in range(NODES):
            if dist[i, j] != np.inf:
                next_node[i, j] = j

    return result, next_node
    
def floyd_serial(dist: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    result, next_node = init_res(dist)

    for k in range(NODES):
        for i in range(NODES):
            for j in range(NODES):
                if result[i][k] + result[k][j] < result[i][j]:
                    result[i][j] = result[i][k] + result[k][j] 
                    next_node[i][j] = next_node[i][k]

    return result, next_node

def inner_floyd_loop_mp(
    i: int, 
    k: int, 
    result: np.ndarray,
    next_node: np.ndarray,
) -> tuple[int, np.ndarray, np.ndarray]:
    for j in range(NODES):
        if result[i][k] + result[k][j] < result[i][j]:
            result[i][j] = result[i][k] + result[k][j] 
            next_node[i][j] = next_node[i][k]
    return i, result[i], next_node[i]

def floyd_mp(dist: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    result, next_node = init_res(dist)

    with multiprocessing.Pool(multiprocessing.cpu_count()) as executor:
        for k in range(NODES):
            p = partial(inner_floyd_loop_mp, k=k, result=result, next_node=next_node)
            res_list = executor.map(p, range(NODES))

            for r in res_list:
                result[r[0]] = r[1]
                next_node[r[0]] = r[2]

    
    return result, next_node

@nb.njit
def inner_floyd_loop(
    k: int,
    i: int,
    result: np.ndarray,
    next_node: np.ndarray,
):
    for j in range(NODES):
        if result[i, k] + result[k, j] < result[i, j]:
            result[i, j] = result[i, k] + result[k, j]
            next_node[i, j] = next_node[i, k]

@nb.njit
def floyd_numba_parallel(dist: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    result, next_node = init_res(dist)

    for k in range(NODES):
        for i in nb.prange(NODES):
            inner_floyd_loop(k, i, result, next_node)

    return result, next_node

if __name__ == '__main__':
    # generate
    dist = np.full((NODES, NODES), np.inf)

    edges = []
    for i in range(EDGES):
        u, v = randint(0, NODES - 1),  randint(0, NODES - 1)
        while u == v or dist[u][v] != np.inf:
            u, v = randint(0, NODES - 1),  randint(0, NODES - 1)
        dist[u][v] = randint(1, MAX_WEIGHT)
        edges.append((u, v, {'weight': dist[u][v]}))

    G = nx.Graph()
    G.add_nodes_from(range(NODES)) 
    G.add_edges_from(edges)


    start = time()
    calculated_serial, next_serial = floyd_serial(dist)
    print(time() - start)

    start = time()
    calculated_mp, next_mp = floyd_mp(dist)
    print(time() - start)

    start = time()
    calculated_nb, next_np = floyd_numba_parallel(dist)
    print(time() - start)

    assert (calculated_serial == calculated_mp).all()
    assert (calculated_serial == calculated_nb).all()

    start, end = randint(0, NODES - 1), randint(0, NODES - 1)
    while start == end or calculated_serial[start][end] == np.inf:
        start, end = randint(0, NODES - 1),  randint(0, NODES - 1)
    
    path = []
    n = start
    while n != end:
        n = int(n)
        path.append(n)
        n = next_serial[n, end] 
    else:
        path.append(end)
    
    print(f'path from {start} to {end} is  {path}')

    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True)
    nx.draw_networkx_edge_labels(G, pos, nx.get_edge_attributes(G, "weight"))
    nx.draw_networkx_edges(
        G,
        pos,
        edgelist=list(nx.utils.pairwise(path)),
        arrowstyle="->",
        arrowsize=15,
        edge_color='red',
        width=3,
    )
    plt.show()
