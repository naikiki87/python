from collections import defaultdict
import networkx as nx
from itertools import combinations
# from networkx.algorithms.community import k_clique_communities


# __author__ = """\n""".join(['Conrad Lee <conradlee@gmail.com>',
#                             'Aric Hagberg <aric.hagberg@gmail.com>'])
# __all__ = ['k_clique_communities']

def k_clique_communities(G, k, cliques=None):
    """Find k-clique communities in graph using the percolation method.

    A k-clique community is the union of all cliques of size k that
    can be reached through adjacent (sharing k-1 nodes) k-cliques.

    Parameters
    ----------
    G : NetworkX graph

    k : int
       Size of smallest clique

    cliques: list or generator       
       Precomputed cliques (use networkx.find_cliques(G))

    Returns
    -------
    Yields sets of nodes, one for each k-clique community.

    Examples
    --------
    >>> G = nx.complete_graph(5)
    >>> K5 = nx.convert_node_labels_to_integers(G,first_label=2)
    >>> G.add_edges_from(K5.edges())
    >>> c = list(nx.k_clique_communities(G, 4))
    >>> list(c[0])
    [0, 1, 2, 3, 4, 5, 6]
    >>> list(nx.k_clique_communities(G, 6))
    []

    References
    ----------
    .. [1] Gergely Palla, Imre Derényi, Illés Farkas1, and Tamás Vicsek,
       Uncovering the overlapping community structure of complex networks 
       in nature and society Nature 435, 814-818, 2005,
       doi:10.1038/nature03607
    """
    if k < 2:
        raise nx.NetworkXError("k=%d, k must be greater than 1."%k)
    if cliques is None:
        cliques = nx.find_cliques(G)
    cliques = [frozenset(c) for c in cliques if len(c) >= k]

    # First index which nodes are in which cliques
    membership_dict = defaultdict(list)
    for clique in cliques:
        for node in clique:
            membership_dict[node].append(clique)

    # For each clique, see which adjacent cliques percolate
    perc_graph = nx.Graph()
    perc_graph.add_nodes_from(cliques)
    for clique in cliques:
        for adj_clique in _get_adjacent_cliques(clique, membership_dict):
            if len(clique.intersection(adj_clique)) >= (k - 1):
                perc_graph.add_edge(clique, adj_clique)

    # Connected components of clique graph with perc edges
    # are the percolated cliques
    for component in nx.connected_components(perc_graph):
        yield(frozenset.union(*component))

def _get_adjacent_cliques(clique, membership_dict):
    adjacent_cliques = set()
    for n in clique:
        for adj_clique in membership_dict[n]:
            if clique != adj_clique:
                adjacent_cliques.add(adj_clique)
    return adjacent_cliques

# G = nx.complete_graph(5)
# K5 = nx.convert_node_labels_to_integers(G,first_label=2)
# G.add_edges_from(K5.edges())


## generate Graph G
G = nx.Graph()

# SUBJECT = "NIKE"
SUBJECT = "ADIDAS"
EXCEPT = ["the", "and", "a", "of", "for", "on", "in", "as", "by", "at", "was", "to", "but", "were", "that", "this", "its", "with", "which", "is", "an", "has", "had", "it", "from"]

filename = SUBJECT + ".txt"
file = open(filename, 'r', encoding='utf8')
s = file.read()
data = s.split('\n')

pre = ''
cur = ''
no_in = 0

for i in range(len(data)) :
    words = data[i].split(' ')
    if words[0] == '' :
        a = 1
    else :
        for j in range(len(words)) :
            words[j] = words[j].strip()         # 공백 제거

            if '[' in words[j] :
                t = words[j].index('[')
                words[j] = words[j][0:t]

            if ']' in words[j] :
                for k in range(len(words[j])) :
                    if words[j][k] == '[' :
                        words[j] = words[j][0:k]
                        break
                    
                    if k == (len(words[j]) - 1) :
                        no_in = 1
                
                if no_in == 1 :
                    no_in = 0
                    continue

            words[j] = words[j].lower()         # make lower character
            words[j] = words[j].strip(',."?!:')         # 공백 제거

            if words[j] in EXCEPT :
                continue
            else :
                G.add_node(words[j])                # add node

                if cur != '' :
                    G.add_edge(cur, words[j])
                    cur = words[j]
                else :
                    cur = words[j]


c = list(k_clique_communities(G, 4))
print(nx.info(G))
print("c : ", c)