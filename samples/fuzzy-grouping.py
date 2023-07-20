"""
Group child nodes of a selected node based on their names. Name comparison is 
done by fuzzy matching. The similarity threshold can be set in the script.
This way, nodes are grouped based on their names, even if they are not exactly matching
"""

from os import name
from fuzzywuzzy import fuzz

similarity = 90

print("[info] Start fuzzy grouping of nodes based on their names...")
print(f"[info] Similarity threshold: {similarity}%")
print("[info] Select a node to start...")

selectedNode = vrdNode(getSelectedNode())
print("[info] Selected node: ", selectedNode.getName())

parent = vrdNode(selectedNode.getParent())

childNodes = selectedNode.children
nodesDict = {}

print("[info] Building nodes dictionary...")
nodes = [*childNodes]
while (len(nodes) > 0):
    pathsToRemove = []

    for i in range(len(nodes)):
        node = nodes[i]
        name = node.getName()
        path = node.getPath()

        if path not in nodesDict:
            nodesDict[name] = [path]
            pathsToRemove.append(path)

        # Compare node with every other node
        for node in nodes:
            name_2 = node.getName()
            path_2 = node.getPath()

            if path == path_2:
                continue
            else:
                path_ratio = fuzz.ratio(path, path_2)
                print("Compare nodes", name, name_2, path_ratio)
                if path_ratio > similarity:
                    nodesDict[name].append(path_2)
                    pathsToRemove.append(path_2)

        # Remove nodes that have been compared
        nodes[:] = [node for node in nodes if node.getPath() not in pathsToRemove]
        pathsToRemove = []
        break

print("[info] Nodes dictionary: ")
for key, value in nodesDict.items():
    print(key, len(value))

print("[info] Create new group node...")
copyGroup = vrScenegraphService.createNode(
    vrScenegraphTypes.NodeType.TransformNode,
    parent,
    selectedNode.getName() + "_grouped"
)

print("[info] Duplicate nodes into new group node...")
for key, nodePaths in nodesDict.items():
    # Create new node to group child nodes
    if len(nodePaths) < 2:
        nodesToCopy = []
        for path in nodePaths:
            nodesToCopy.append(vrNodeService.findNodeWithPath(path))

        duplicatedNodes = vrScenegraphService.duplicateNodes(nodesToCopy)
        copyGroup.children.append(duplicatedNodes)

        continue

    newName = key
    newParent = copyGroup
    newGroup = vrScenegraphService.createNode(vrScenegraphTypes.NodeType.TransformNode, newParent, newName)

    nodesToCopy = []
    for path in nodePaths:
        nodesToCopy.append(vrNodeService.findNodeWithPath(path))

    duplicatedNodes = vrScenegraphService.duplicateNodes(nodesToCopy)
    newGroup.children.append(duplicatedNodes)

print("[info] Done...")
