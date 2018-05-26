"""
Implements S², an Efficient Graph-Based Active Learning Algorithm.

@inproceedings{dasarathy2015s2,
  title={S2: An efficient graph based active learning algorithm with application to nonparametric classification},
  author={Dasarathy, Gautam and Nowak, Robert and Zhu, Xiaojin},
  booktitle={Conference on Learning Theory},
  pages={503--522},
  year={2015}
}
"""

import networkx as nx
import random
import itertools


def s2(G, oracle, shortest_path):
    """
    Runs the S² algorithm on a graph, returning the unzipped graph.

    Parameters
    ----------
    G : nx.Graph
        The input graph to the algorithm.
    oracle : fn(vertex) -> bool
        An oracle function, taking a vertex and returning the label as a `bool`.
    shortest_path : fn(G : nx.Graph, u : vertex, v : vertex) -> list of vertices or `None`
        A function which, given a graph and a pair of vertices, returns a path between the pair of vertices, or
        None if one cannot be found.
    """
    G = G.copy()

    # number of vertices
    n = G.order()

    # labeled set. represented as a list of (vert, label) pairs.
    L = []

    while True:
        if len(L) == n:
            break

        # pick a random vertex
        vert = random.choice(G.nodes())

        while True:
            # query the current vertex
            y = oracle(vert)
            # add the current vertex to the labeled set
            L.append((vert, y))
            # mark it as labeled
            G.node[vert]['label'] = y

            # find obvious cuts
            cuts = find_obvious_cuts(G, L)
            # unzip
            G.remove_edges_from(cuts)

            # try to pick a new vertex via midpoint of shortest shortest path
            vert = find_mssp(G, L, shortest_path)

            # if it's bad, break out of the inner loop and get a new random vert
            if vert is None:
                break

    return G

def find_obvious_cuts(G, L=None):
    """
    Find obvious cuts between adjacent verts of different labels.

    Parameters
    ----------
    G : nx.Graph
        The input graph, with nodes with known label marked with the data attribute `label`.
    L : optional list of (vert, label)
        A list of tuples of vertices with known labels, and their corresponding label.

        Is only used to accelerate slightly so we don't have to re-search the graph; if None,
        we do our own search for `label`s.
    """
    
    if L is None:
        labeled_nodes = [v[0] for v in G.nodes_iter(data=True) if v[1].get('label') is not None]
    else:
        labeled_nodes = [l[0] for l in L]

    labeled_subgraph = G.subgraph(labeled_nodes)

    cuts = []
    # for every pair of labeled vertices
    for edge in labeled_subgraph.edges_iter():
        # for every cut pair of labels
        if G.node[edge[0]]['label'] != G.node[edge[1]]['label']:
            cuts.append(edge)

    return cuts

def find_mssp(G, L, shortest_path):
    ssp = find_ssp(G, L, shortest_path)
    if ssp is None:
        return None

    return ssp[len(ssp)//2]

def find_ssp(G, L, shortest_path):
    labeled_nodes = [l[0] for l in L]
    paths = []
    # for every pair of labeled vertices
    for (u, v) in itertools.combinations(labeled_nodes, r=2):
        # for every cut pair of labels
        if G.node[u]['label'] != G.node[v]['label']:
            try:
                P = shortest_path(G, u, v)
            except nx.NetworkXNoPath:
                # we don't have a path, so skip adding it to the list
                continue

            paths.append(P)

    # if we found no paths, return None
    if paths == []:
        return None

    # find the shortest shortest path
    ssp = min(paths, key=lambda path: len(path))

    return ssp
