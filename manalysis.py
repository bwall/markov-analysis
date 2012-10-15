'''
Created on Oct 12, 2012

@author: bwall (Brian Wallace of Ballast Security)
'''
import os.path
import sys
import re
import operator

class MarkovDB:
    def createDB(self):
        fileOUT = open(self.name + ".db", "w")
        for first in range(0, 256):
            for second in range(0, 256):
                fileOUT.write("0\n")
        fileOUT.close()
    
    def __init__(self, name):
        self.name = name
        if os.path.isfile(name + ".db") == False:
            self.createDB()
        self.data = dict()
        for first in range(0, 256):
            self.data[first] = dict()
            for second in range(0, 256):
                self.data[first][second] = 0
        self.load()
        
    def load(self):
        fileIN = open(self.name + ".db", "r")
        for first in range(0, 256):
            for second in range(0, 256):
                self.data[first][second] = int(fileIN.readline())
        fileIN.close()
                
    def save(self):
        fileOUT = open(self.name + ".db", "w")      
        for first in range(0, 256):
            for second in range(0, 256):
                fileOUT.write(str(self.data[first][second]) + "\n")
        fileOUT.close()
        
    def insertPair(self, first, second):
        self.data[first][second] += 1
        
    def getPercentage(self, first, second):
        part = self.data[first][second]
        full = 0
        for s in range(0, 256):
            full += self.data[first][s]
        if full == 0:
            return (0, 0)
        return (part, full)
    
    def getMatch(self, line):
        total = 0
        full = 0
        last = ord(line[:1])
        line = line[1:]
        while line.__len__() != 0:
            current = ord(line[:1])
            line = line[1:]
            temp = self.getPercentage(last, current)
            full += temp[1]
            total += temp[0]
            last = current
        return (total, full)
        
    def addData(self, i):
        last = 0
        while i.__len__() != 0:
            current = ord(i[:1])
            i = i[1:]
            self.insertPair(last, current)
            last = current
        self.insertPair(last, 0)

databases = dict()

def GetBestMatches(line):
    matches = dict()
    for key in databases:
        result = databases[key].getMatch(line)
        if result[1] > 10000:
			if result[1] == 0:
				matches[key] = 0
			else:
				matches[key] = (float(result[0])/float(result[1]))
    sorted_matches = sorted(matches.iteritems(), key=operator.itemgetter(1))
    count = 0
    for i in range(0, sorted_matches.__len__()):
        print sorted_matches[-1 - i]
        count += 1
        if count == 10:
			break

def LoadAllKnown():
    files = filter(os.path.isfile, os.listdir('.'))
    for f in files:
        if f[-3:] == ".db":
            databases[f[:-3]] = MarkovDB(f[:-3])

def SaveAll():
    for key in databases:
        databases[key].save()

def ParseFile(log):
    pattern = re.compile('''\d\d:\d\d <.?([^>]+)\> (.*)''')
    fileIN = open(log, "r")
    line = fileIN.readline()
    while line:
        match = pattern.match(line)
        if match != None:
            print match.group(1) + " - " + match.group(2)
            if match.group(1) not in databases:
                databases[match.group(1)] = MarkovDB(match.group(1))
            databases[match.group(1)].addData(match.group(2))
        line = fileIN.readline()
    fileIN.close()

if __name__ == '__main__':
    print "Loading"
    LoadAllKnown()
    print "Done Loading"
    sys.stdout.write("Input Line: ")
    line = sys.stdin.readline()[:-1]
    while line != "":
        GetBestMatches(line)
        sys.stdout.write("Input Line: ")
        line = sys.stdin.readline()[:-1]
    
