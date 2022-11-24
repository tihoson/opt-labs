import networkx as nx
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing
from functools import partial
from random import randint
from math import inf
from time import time
import os


NODES = 200
EDGES = randint(NODES, NODES * 2)
MAX_WEIGHT = 5

# calculate
# 1) signle thread
# 2) multiple threads
def floyd_serial(dist: list[list[int]]) -> tuple[list[list[int]], list[list[int]]]:
    result = [list(row) for row in dist]
    next_node = [[j if dist[i][j] != inf else inf for j in range(NODES)] for i in range(NODES)]

    for k in range(NODES):
        for i in range(NODES):
            for j in range(NODES):
                if result[i][k] + result[k][j] < result[i][j]:
                    result[i][j] = result[i][k] + result[k][j] 
                    next_node[i][j] = next_node[i][k]

    return (result, next_node)

def inner_floyd_loop(
    i: int, 
    k: int, 
    result: list[list[int]], 
    next_node: list[list[int]]) -> tuple[int, list[int], list[int]]:
    for j in range(NODES):
        if result[i][k] + result[k][j] < result[i][j]:
            result[i][j] = result[i][k] + result[k][j] 
            next_node[i][j] = next_node[i][k]
    return (i, result[i], next_node[i])

def floyd_parallel(dist: list[list[int]]) -> tuple[list[list[int]], list[list[int]]]:
    result = [list(row) for row in dist]
    next_node = [[j if dist[i][j] != inf else inf for j in range(NODES)] for i in range(NODES)]
    
    with multiprocessing.Pool(multiprocessing.cpu_count()) as executor:
    # with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        for k in range(NODES):
            p = partial(inner_floyd_loop, k=k, result=result, next_node=next_node)
            res_list = executor.map(p, range(NODES))

            for r in res_list:
                result[r[0]] = r[1]
                next_node[r[0]] = r[2]

    
    return (result, next_node)

if __name__ == '__main__':
    # generate
    dist = [[inf for _ in range(NODES)] for _ in range(NODES)]
    for i in range(NODES):
        dist[i][i] = 0

    edges = []
    for i in range(EDGES):
        u, v = randint(0, NODES - 1),  randint(0, NODES - 1)
        while u == v or dist[u][v] != inf:
            u, v = randint(0, NODES - 1),  randint(0, NODES - 1)
        dist[u][v] = randint(0, MAX_WEIGHT)
        edges.append((u, v, {'weight': dist[u][v]}))

    G = nx.Graph()
    G.add_nodes_from(range(NODES)) 
    G.add_edges_from(edges)


    start = time()
    calculated_serial, next_serial = floyd_serial(dist)
    print(time() - start)

    start = time()
    calculated_parallel, next_parallel = floyd_parallel(dist)
    print(time() - start)

    # draw
    nx.draw(G, with_labels=True) 
    plt.show()

    # update
