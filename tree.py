from natsort import natsorted
import json
import re
from Tree_Extra_Code import deleteBullet
import DFS


class Node:
    def __init__(self):
        # this list contain the childs of type Node
        self.nodes = []
        # this list contain the data of childs
        self.nodesData = []
        # data if current node
        self.data = ''
        # this count is the count of child
        self.count = 0
        # the level of current node
        self.level = 0
        # this is the index of current bullet in the dataframe
        self.index = 0

    def countNodes(self):
        self.count = len(self.nodes)

    def addData(self, data):
        self.data = data

    def addLevel(self, level):
        self.level = level

    def addChild(self, bullet, sep, index=0):
        # add child in tree by checking if there is no parent

        global treeLevel
        if self.countNodes == 0:
            newNode = Node()
            newNode.addData(bullet)
            newNode.addLevel(self.level+1)
            newNode.addIndex(index)
            treeLevel = max(treeLevel, self.level+1)
            self.nodes.append(newNode)
            self.countNodes()
        else:
            self.pushNode(bullet, self.nodes, index, sep)

    def addIndex(self, index):
        self.index = index

    def pushNode(self, bullet, nodeList, index, sep):
        # first it check if it is in first level then find the parent using seperator like . or space and it goes on
        # if parent is not in the node list then append the bullet in the current list
        global treeLevel
        if bullet in self.nodesData:
            ind = self.nodesData.index(bullet)
            self.nodes[ind].addIndex(index)
            return
        lev = self.getLevel(bullet, sep, self.level)
        if len(lev) > 0:
            n = True
            for l in lev:
                if l in self.nodesData:
                    ind = self.nodesData.index(l.strip())
                    if bullet[-1] == '.':
                        try:
                            if self.nodesData.index(bullet[:-1]) != -1:
                                n = False
                            return
                        except:
                            pass
                    n = False
                    self.nodes[ind].pushNode(
                        bullet, self.nodes[ind].nodes, index, sep)
                    return
            if n:
                newNode = Node()
                newNode.addData(bullet)
                newNode.addLevel(self.level+1)
                newNode.addIndex(index)
                treeLevel = max(treeLevel, self.level+1)
                self.nodes.append(newNode)
                self.nodesData.append(bullet.strip())
                self.countNodes()
        else:
            newNode = Node()
            newNode.addData(bullet)
            self.nodes.append(newNode)
            newNode.addLevel(self.level+1)
            newNode.addIndex(index)
            treeLevel = max(treeLevel, self.level+1)
            self.nodesData.append(bullet.strip())
            self.countNodes()

    def __str__(self, level=0):
        # prints the tree with level
        ret = "\t"*level+repr(self.data)+","+repr(self.index)+"\n"
        for child in self.nodes:
            ret += child.__str__(level+1)
        return ret

    def getData(self):
        return self.data

    def getNodes(self):
        return self.nodes

    def getLevel(self, bullet, sep, level=0):
        # make the probable parent with or without separator
        bul = bullet.split(sep)
        levels = []
        levels.append(sep.join(bul[:level+1]))
        levels.append(sep.join(bul[:level+1])+sep)
        return levels

    def filterNode(self):
        # remove nodes with 0 child
        self.nodes = [n for n in self.nodes if n.count != 0]
        self.refreshNodes()
        self.countNodes()

    def removeNodes(self):
        # remove nodes with 0 child before leaf node
        global treeLevel
        if self.level == treeLevel:
            return
        for node in self.nodes:
            node.removeNodes()
        self.filterNode()

    def refreshNodes(self):
        # refresh nodedata when the nodes change
        self.nodesData = [n.getData() for n in self.getNodes()]

    def refreshNodeLists(self):
        # refresh complete tree data
        if self.count == 0:
            return
        for n in self.nodes:
            n.refreshNodeLists()
        # n.refreshNodes()
        self.refreshNodes()

    def makeList(self):
        # convert tree to list in the way first is parent then its child and then next parent node
        bullets = self.traverse()
        return bullets.split("@")[2:]

    def traverse(self):
        ret = "@{\""+self.data+"\":"+repr(self.index)+"}"
        for child in self.nodes:
            ret += child.traverse()
        return ret

    def makeSeparable(self, nbr, sep):
        try:
            return int(''.join([x for x in re.split(sep, nbr) if x != '']))
        except:
            return ''

    def countChild(self):
        # count the child of called node
        if self.count == 0:
            return 0
        ch = self.count
        for node in self.nodes:
            ch += node.countChild()
        return ch

    def findZeroPattern(self):
        # find if the parent nodes follows 0 pattern like 01, 02 or not like 1,2
        zero = 0
        single = 0
        for i in self.nodesData:
            x = self.makeSeparable(i, '\.?\ ?')
            if x != '' and x < 10:
                if i[0] == '0':
                    zero += 1
                else:
                    single += 1
        print(single,zero)
        if single > zero:
            return False
        if single == zero:
            return None
        return True

    def verifySequence(self):
        # select all the parent which follows pattern found
        find = []
        pattern = self.findZeroPattern()
        for id, x in enumerate(self.nodesData):
            if x == '0' or x == '0.':
                find.append(id)
                continue
            if id+1 != len(self.nodesData):
                f = self.makeSeparable(x, '\.?\ ?')
                s = self.makeSeparable(self.nodesData[id+1], '\.?\ ?')
                if f != '' or s != '':
                    if f == s:
                        if s < 10 or pattern != None:
                            if pattern:
                                if x[0] != '0':
                                    find.append(id)
                                elif self.nodesData[id+1][0] != '0':
                                    find.append(id+1)
                            else:
                                if x[0] == '0':
                                    find.append(id)
                                else:
                                    if self.nodesData[id+1][0] == '0':
                                        find.append(id+1)
                        else:
                            if self.nodes[id].countChild() > self.nodes[id+1].countChild():
                                find.append(id+1)
                            # elif self.nodes[id].countChild() == self.nodes[id+1].countChild():
                            #     find.append(id+1)
                            else:
                                find.append(id)
                else:
                    find.append(id)
        self.nodes = [x for id, x in enumerate(self.nodes) if id not in find]

    def findDebth(self):
        # find the depth of tree
        global treeLevel
        for x in self.nodes:
            x.findDebth()
            treeLevel = max(treeLevel, x.level)
        return treeLevel

    def findSelfDepth(self, treeLevel=0):
        # fnd depth of called node
        for x in self.nodes:
            treeLevel = x.findSelfDepth(treeLevel)
            treeLevel = max(treeLevel, x.level)
        return treeLevel

    def sortNodes(self):
        # sort teh nodes and the child
        newNodes = natsorted(enumerate(self.nodesData), key=lambda i: i[1])
        nodes = list(self.nodes)
        self.nodes = [nodes[id] for id, x in newNodes]

    def findPattern(self):
        # find pattern if it follows . or not
        spDot = 0
        self.refreshNodes()
        for id, x in enumerate(self.nodesData):
            if re.search('\.(\s)+', x) != None:
                spDot += 1
                self.nodesData[id] = self.nodes[id].data.replace(' ', '0')
        if spDot > 0:
            self.sortNodes()
            self.refreshNodes()

    def properSort(self):
        if self.count == 0:
            return
        for node in self.nodes:
            node.properSort()
        self.findPattern()

    def sortTree(self):
        # sort the tree
        if self.count == 0:
            return
        for n in self.nodes:
            n.sortTree()
        self.sortNodes()

    def sortHead(self):
        # find the max frequency of differences in head data and select according to it
        ls = []
        global treeLevel
        if treeLevel != 1:
            idsx = []
            for id, n in enumerate(self.nodes):
                if n.count == 0:
                    idsx.append(id)
            self.nodes = [x for id, x in enumerate(
                self.nodes) if id not in idsx]
            self.refreshNodes()
        for i, x in enumerate(self.nodesData):
            try:
                ls.append(int(x.replace('.', '')) -
                          int(self.nodesData[i - 1].replace('.', '')))
            except:
                continue
        ls = ls[1:]
        if len(ls) > 0:
            d = max(ls, key=ls.count)
            ids = []
            for id, x in enumerate(self.nodesData):
                if id == 0:
                    ids.append(id)
                    continue
                if id+1 == len(self.nodesData):
                    if int(x.replace('.', ''))-int(self.nodesData[id-1].replace('.', '')) == d:
                        ids.append(id)
                    break
                try:
                    if int(self.nodesData[id+1].replace('.', ''))-int(x.replace('.', '')) == d:
                        ids.extend([id, id+1])
                    else:
                        # ids.append(id)
                        break
                except:
                    pass
            ids = list(set(ids))
            print(ids)
            self.nodes = [x for id, x in enumerate(self.nodes) if id in ids]


def driveCode(indexes, space, df):
    global treeLevel
    treeLevel = 0
    head = Node()
    head.addData('/')
    values = []
    indices = []
    print(indexes)
    # indexes = {k: v for k, v in indexes.items() if v != []}
    for key, v in indexes.items():
        if 'Titel ' in v[2]:
            v[0] = v[0]+len('Titel ')
            v[2] = v[2].replace('Titel ', '')
            v[1] = v[0]+len(v[2])
            indexes[key] = v
        elif 'Kapitel ' in v[2]:
            v[0] = v[0]+len('Kapitel ')
            v[2] = v[2].replace('Kapitel ', '')
            v[1] = v[0]+len(v[2])
            indexes[key] = v
        elif 'Abschnitt ' in v[2]:
            v[0] = v[0]+len('Abschnitt ')
            v[2] = v[2].replace('Abschnitt ', '')
            v[1] = v[0]+len(v[2])
            indexes[key] = v
        elif 'LB ' in v[2]:
            v[0] = v[0]+len('LB ')
            v[2] = v[2].replace('LB ', '')
            v[1] = v[0]+len(v[2])
            indexes[key] = v
        elif 'Gewerk ' in v[2]:
            v[0] = v[0]+len('Gewerk ')
            v[2] = v[2].replace('Gewerk ', '')
            v[1] = v[0]+len(v[2])
            indexes[key] = v
    for k, val in indexes.items():
        values.append(val[2].strip())
        indices.append(k)
    values = natsorted(enumerate(values), key=lambda i: i[1])
    # print(values)
    sep = ''
    if space:
        sep = ' '
    else:
        sep = '.'
    for ind, i in values:
        head.addChild(i, sep, indices[ind])
# sort the tree
    head.sortTree()
    # refresh complete tree data
    print(head)
    head.refreshNodeLists()
    head.countNodes()
    treeLevel = 0
    head.findDebth()
    if treeLevel > 1:
        head = DFS.driveDFS(head, df)
    # select all the parent which follows pattern found
    head.verifySequence()
    print("after verification",head)
    head.refreshNodeLists()
    head.countNodes()
    treeLevel = 0
    head.findDebth()
    # find pattern if it follows . or not
    head.properSort()
    # find the max frequency of differences in head data and select according to i
    head.sortHead()
    print('after sort',head)
    head.refreshNodeLists()
    if treeLevel > 1:
        bullets = deleteBullet(head, indexes)
    else:
        bullets = head
    print(head)
    # convert tree to list in the way first is parent then its child and then next parent node
    bullets = bullets.makeList()
    bullets = [json.loads(x) for x in bullets]
    bullets = {k: v for id in bullets for k, v in id.items()}
    bulletpoints = list(bullets.keys())
    indexKeys = list(bullets.values())
    return indexKeys, bulletpoints
