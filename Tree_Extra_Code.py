# algo
# find parents only first
# go in depth to leaf and come to parent
# check either the parent index is correct with first child or not
# find the correct parent index if not found delete
# before deleting insert all child inplace of its parent
# go until pointers not on head if it goes to first depth
# to check next child in parents sibling jo after len of inserted childs

def delParent(curr, parent):  # for deleting any child parent
    parent[-2].nodes = parent[-2].nodes[:curr] + \
        parent[-1].nodes+parent[-2].nodes[curr+1:]
    count = len(parent[-1].nodes)
    # del parent[-1]
    return count


def delHeadParent(curr, parent):  # for deleteing parent node of first level
    par = parent.nodes[curr]
    parent.nodes = parent.nodes[:curr] + \
        parent.nodes[curr].nodes+parent.nodes[curr+1:]
    curr = parent.nodes[curr].count
    del par
    parent.refreshNodes()
    return curr


def traverseNode(index, parentIndex, root, parent, indexes):
    if root.count == 0:
        if parent[-1].index > root.index:
            ind = [x for x in list(indexes.keys()) if x < root.index]
            k = len(ind)-1
            br = False
            curr = -1
            while k > 0:
                if indexes[ind[k]][2] == parent[-1].getData():
                    parent[-1].addIndex(ind[k])
                    br = True
                    break
                k = k-1
            if not br:
                # print("before delete", parent[-1].getData())
                curr = delParent(parentIndex, parent)
                # print("after delete", parent[-1].getData())
            return curr, br
        return -1, False
    else:
        i = 0
        parent.append(root)
        # print("parent", root.getData())
        # br = False
        # k = -1
        while i < len(root.nodes):
            k = -1
            # print('i=', i, [x.getData() for x in root.nodes])
            k, br = traverseNode(i, index, root.nodes[i], parent, indexes)
            # print('wapis', k, br, len(root.nodes))
            if not br:
                if k != -1:
                    i += k-1
                i += 1
            else:
                # print("return")
                break
        parent.pop()
        return -1, False


def correctTreeIndex(head, indexes):
    if head.count != 0:
        i = 0
        while i < len(head.nodes):
            k = -1
            k, br = traverseNode(i, i, head.nodes[i], [head], indexes)
            if k != -1:
                i += k-1
            i += 1
        i = 0
        while i < len(head.nodes):
            head.nodes[i].refreshNodeLists()
            head.nodes[i].countNodes()
            if head.nodes[i].count > 0:
                if head.nodes[i].index > head.nodes[i].nodes[0].index:
                    ind = [x for x in list(indexes.keys())
                           if x < head.nodes[i].nodes[0].index]
                    k = len(ind)-1
                    br = False
                    while k > 0:
                        if indexes[ind[k]][2] == head.nodes[i].getData():
                            head.nodes[i].addIndex(ind[k])
                            br = True
                            break
                        k = k-1
                    if not br:
                        delHeadParent(i, head)
            i += 1
    return head


def verifyAndDelete(n, index, parent, maxDepth):
    if n.count == 0:
        del parent.nodes[index]
        parent.refreshNodes()
        return
    else:
        for i, node in enumerate(n.nodes):
            if node.level < maxDepth:
                verifyAndDelete(node, i, n, maxDepth)


def deleteBullet(head, indexes):
    # print(head)
    head = correctTreeIndex(head, indexes)
    # print(head)
    return head
