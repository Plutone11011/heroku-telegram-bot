
#a dictionary with an additional variable to maintain last key value between states of ConversationHandler
class ListOfStuff():
    def __init__(self):
        self.mydict = {}
        self.chiave = ''

    def setKey(self,k):
        self.chiave = k
        if not self.chiave in self.mydict:
            self.mydict[self.chiave] = []

    def getKey(self):
        return self.chiave

    def getDict(self):
        return self.mydict

    def setValue(self,v):
        self.mydict[self.chiave].append(v)

    def getValue(self):
        return self.mydict[self.chiave] 