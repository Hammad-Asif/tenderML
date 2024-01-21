# Algo
# 1 go in depth of each node
# 2 find the unit in between the siblings if it find then the bullet will remian else it will be deleted from the nodes list
# 3 after all siblings to be check with units parent's index must be smaller than its first child
# else parent will be deleted and its parent's child will be its parents siblings
# finally find the depth of each node and delete the nodes before leaf nodes on each level wehere there is no child of the node
import re


class DFS:
    def __init__(self, head, df):
        self.head = head
        self.df = df
        units = ['h', 'm²Wo', 'mWo', 'cm', 'to', 'sqft', 'Satz' 'Mt', 'qm', 'cbm', 'lfdm', 'Stk', 'St', 'PA', 'd', 'Monat', 'Jahre', 'ldm', 'pauschal', 'Stück',
                 'Stck', 'Psch', 'Psh', 'm[23]', 'Pau', 'm', 'mm', 'm²', 'm³', 'Std.', 'Std', 'psh.', 'lfm', 'Wo', 'm2Wo', 'StWo', 't', 'Mon', 'kg', 'Woche']
        self.unitsOnly = "("
        for un in units:
            self.unitsOnly += "("+un+")\\b|"+"(" + \
                un.upper()+")\\b|"+"("+un.lower()+")\\b|"
        self.unitsOnly = self.unitsOnly[:-1]
        self.unitsOnly += ")"
        self.onlyUnits = "("
        for un in units:
            self.onlyUnits += "\\b("+un+")\\b|"+"\\b(" + \
                un.upper()+")\\b|"+"\\b("+un.lower()+")\\b|"
        self.onlyUnits = self.onlyUnits[:-1]
        self.onlyUnits += ")"
        self.unitsRegx = "([0-9]+(\.|\,)*)+(\ )*"+self.unitsOnly

    def searchUnits(self, txt):
        sx = re.finditer(self.unitsRegx, txt)
        s = re.search(self.unitsRegx, txt)
        if s != None:
            units = tuple({x.start(): x.group()} for x in sx)
            return units
        return None

    def findUnit(self, curr, next, parent, root):
        if next < len(parent[-1].nodes):
            txt = ' '.join(
                [x['Text'] for id, x in self.df.iloc[parent[-1].nodes[curr].index:parent[-1].nodes[next].index].iterrows()])
            if self.searchUnits(txt) != None:
                return True
            return False
        else:
            i = -1
            val = False
            br = False
            while i > (-1)*len(parent):
                ind = parent[i-1].nodesData.index(parent[i].getData())
                if ind < len(parent[i-1].nodesData)-1:
                    if root.index < parent[i-1].nodes[ind+1].index:
                        if parent[i-1].nodes[ind+1].index-root.index > 300:
                            txt = ' '.join(
                                [x['Text'] for id, x in self.df.iloc[root.index:root.index+25].iterrows()])
                            if self.searchUnits(txt) != None:
                                br = True
                                val = True
                                break
                            else:
                                return False
                        txt = ' '.join(
                            [x['Text'] for id, x in self.df.iloc[root.index:parent[i-1].nodes[ind+1].index].iterrows()])
                        if self.searchUnits(txt) != None:
                            br = True
                            val = True
                            break
                        br = True
                        break
                    else:
                        i = (-1)*len(parent)
                i = i-1
            else:
                if not br:
                    txt = ' '.join(
                        [x['Text'] for id, x in self.df.iloc[parent[-1].nodes[curr].index:parent[-1].nodes[curr].index+25].iterrows()])
                    if self.searchUnits(txt) != None:
                        return True
                    return False
            return val

    def delNode(self, curr, parent):
        del parent.nodes[curr]
        del parent.nodesData[curr]
        parent.refreshNodes()

    def traverseNode(self, index, root, parent):
        if root.count == 0:
            unit = self.findUnit(index, index+1, parent, root)
            if unit:
                return False
            else:
                self.delNode(index, parent[-1])
                return True
        else:
            i = 0
            parent.append(root)
            root.refreshNodes()
            while i < len(root.nodes):
                d = self.traverseNode(i, root.nodes[i], parent)
                if not d:
                    i += 1
            parent.pop()
            if len(root.nodes) <= 0:
                self.delNode(index, parent[-1])
                return True

    def traverseTree(self):
        # traverse tree in DFS manner
        if self.head.count != 0:
            i = 0
            while i < len(self.head.nodes):
                br = self.traverseNode(i, self.head.nodes[i], [self.head])
                if i < len(self.head.nodes):
                    if self.head.nodes[i].count == 0:
                        self.delNode(i, self.head)
                    else:
                        if not br:
                            i += 1
        self.deleteChildLess()
        return self.head

    def verifyAndDelete(self, n, index, parent, maxDepth):
        if n.count == 0:
            del parent.nodes[index]
            parent.refreshNodes()
            return
        else:
            for i, node in enumerate(n.nodes):
                if node.level < maxDepth:
                    self.verifyAndDelete(node, i, n, maxDepth)

    def deleteChildLess(self):
        # find depth of each first child and delete every child greater than last without
        # child and delete them
        for i, node in enumerate(self.head.nodes):
            if node.count != 0:
                maxDepth = node.findSelfDepth()
                self.verifyAndDelete(node, i, self.head, maxDepth)


def driveDFS(head, df):
    algo = DFS(head, df)
    algo.traverseTree()
    return head
