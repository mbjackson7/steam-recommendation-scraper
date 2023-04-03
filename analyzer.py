import json
import re
import networkx as nx
import time
import random

def spreading_analysis(G, probability=0.2, iterations=10):
    
    def spread(root, G, node, probability, currIter, iterations, spreads):
        if currIter >= iterations:
            return
        for neighbor in G.neighbors(node):
            if random.random() < probability:
                spreads[root].append(neighbor)
                spread(root, G, neighbor, probability, currIter + 1, iterations, spreads)

    spreads = {}
    for node in G.nodes():
        currIter = 0
        spreads[node] = []
        spread(node, G, node, probability, currIter, iterations, spreads)
        
    return spreads
                
def main():
    VERSION = "0.0.1"
    G = nx.DiGraph()
    oldRecCount = False
    oldNodeCount = 0
    newPrompt = ""
    dlcList = []
    
    print("Welcome to Steam Recommendation Analyzer v" + VERSION)

    oldGraphName = input("Graph name? ")
    G = nx.read_gexf(f"./.graphs/{oldGraphName}")
    print("Loading graph...")
    print("Loaded graph with " + str(len(G.nodes())) + " nodes")
    nodeCount = int(oldGraphName.split("-")[0].replace("steam", ""))
    recCount = int(oldGraphName.split("-")[1])
    
    print("Analyzing graph...")
    print("Graph has " + str(len(G.nodes())) + " nodes")
    print("Graph has " + str(len(G.edges())) + " edges")
    print("Graph has " + str(nx.number_weakly_connected_components(G)) + " weakly connected components")
    print("Graph has " + str(nx.number_strongly_connected_components(G)) + " strongly connected components")
    print("Graph has " + str(nx.number_connected_components(G.to_undirected())) + " connected components")
    
    print("Calculating degree centrality...")
    degreeCentrality = nx.degree_centrality(G)
    print("Degree centrality is " + str(degreeCentrality))
    print("Calculating betweenness centrality...")
    betweennessCentrality = nx.betweenness_centrality(G)
    print("Betweenness centrality is " + str(betweennessCentrality))
    print("Calculating closeness centrality...")
    closenessCentrality = nx.closeness_centrality(G)
    print("Closeness centrality is " + str(closenessCentrality))

    print("Calculating spreading...")
    spreads = spreading_analysis(G)
    
    print("Saving results...")
    with open(f"./.analysis/{oldGraphName}.json", "w") as f:
        json.dump({
            "degreeCentrality": degreeCentrality,
            "betweennessCentrality": betweennessCentrality,
            "closenessCentrality": closenessCentrality,
            "spreads": spreads
        }, f)
        
    print("Done!")
if __name__ == "__main__":
    main()
