import networkx as nx
G = nx.read_gpickle("law_graphTest.gpickle")
for node_id, data in G.nodes(data=True):
    if data.get("type") == "Article":
        print(node_id, data)
        print(type(data.get("title", "")))
        break  # only show the first one
