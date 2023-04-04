import json
import networkx as nx
                
def main():
    VERSION = "0.0.1"
    G = nx.DiGraph()

    print("Welcome to Steam Recommendation Graph Sanitizer v" + VERSION)
    print("Let remove most of those pesky DLCs and bundles from your graph!")

    oldGraphName = input("Graph name? ")
    G = nx.read_gexf(f"./.graphs/{oldGraphName}")
    print("Loading graph...")
    print("Loaded graph with " + str(len(G.nodes())) + " nodes")
    nodeCount = int(oldGraphName.split("-")[0].replace("steam", ""))
    recCount = int(oldGraphName.split("-")[1])
    
    nodes = list(G.nodes()).copy()

    for node in nodes:
        if not node.isnumeric():
            G.remove_node(node)
            
    print("Saving graph...")
    nx.write_gexf(G, f"./.graphs/{oldGraphName[:-5]}-sanitized.gexf")
    
if __name__ == "__main__":
    main()
