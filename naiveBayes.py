import sys
import os
import math

def buildLex(k):
    lex = {}
    #set up dict with items as tuples (h,s) h = occurrence in ham, s = occurrence in spam
    kobserved = {}
    Htotal = 0 #total number of words in Ham
    Stotal = 0 #total number of words in spam
    
    root = os.getcwd()    
    hamtrain = "/emails/hamtraining/"
    spamtrain = "/emails/spamtraining/"
        
    for subdir, dirs, files in os.walk(root + hamtrain):
        for file in files:
            f = open(root + hamtrain + file)
            for word in f.read().split():
                if word in kobserved.keys():
                    (h,s) = kobserved[word]
                    h += 1
                    kobserved[word] = (h,s)
                else:
                    kobserved[word] = (1,0)
    
    for subdir, dirs, files in os.walk(root + spamtrain):
        for file in files:
            f = open(root + spamtrain + file)
            for word in f.read().split():
                if word in kobserved.keys():
                    (h,s) = kobserved[word]
                    s += 1
                    kobserved[word] = (h,s)
                else:
                    kobserved[word] = (0,1)
    
    for word in kobserved.keys():
        (h,s) = kobserved[word]
        if(h + s >= k):
            lex[word] = (h,s)
            Htotal += h
            Stotal += s
    return lex, Htotal, Stotal

class MAP:
    def __init__(self, lexicon, Htotal, Stotal):
        self.lex = lexicon
        self.Htotal = Htotal
        self.Stotal = Stotal
        self.V = len(lexicon)
        self.wGivenHam = {} # P(word|Ham)
        self.wGivenSpam = {} # P(word|Spam)
        self.hamProb = 0.0 # P(ham) prior
        self.spamProb = 0.0 # P(spam) prior
        
    def estimate(self, m):
        #compute Ham probabilities
        for word in self.lex.keys():
            if word not in self.wGivenHam.keys():
                prob = (self.lex[word][0] + m)/(self.Htotal + m*self.V)
                self.wGivenHam[word] = prob
        #compute Spam probabilities
        for word in self.lex.keys():
            if word not in self.wGivenSpam.keys():
                prob = (self.lex[word][1] + m)/(self.Stotal + m*self.V)
                self.wGivenSpam[word] = prob
        #compute prior for Ham and Spam
        root = os.getcwd()
        hamtrain = "/emails/hamtraining/"
        spamtrain = "/emails/spamtraining/"
        hamFiles = 0
        spamFiles = 0
        
        for subdir, dirs, files in os.walk(root + hamtrain):
            hamFiles = float(len(files))
        for subdir, dirs, files in os.walk(root + spamtrain):
            spamFiles = float(len(files))
        
        self.hamProb = hamFiles/(hamFiles + spamFiles)
        self.spamProb = spamFiles/(hamFiles + spamFiles)
        
def test(train):
    hamRight = 0.0 #track number of correctly classified ham emails
    spamRight = 0.0 #track number of correctly classified spam emails
    hamFiles = 0
    spamFiles = 0
    
    root = os.getcwd()    
    hamtrain = "/emails/hamtesting/"
    spamtrain = "/emails/spamtesting/"
        
    for subdir, dirs, files in os.walk(root + hamtrain):
        hamFiles = float(len(files))
        for file in files:
            f = open(root + hamtrain + file)
            hamProb = math.log(train.hamProb)
            spamProb = math.log(train.spamProb)
            for word in f.read().split():
                if word in train.wGivenHam.keys():
                    hamProb += math.log(train.wGivenHam[word])
                if word in train.wGivenSpam.keys():
                    spamProb += math.log(train.wGivenSpam[word])
            if(hamProb > spamProb):
                hamRight += 1.0
    
    for subdir, dirs, files in os.walk(root + spamtrain):
        spamFiles = float(len(files))
        for file in files:
            f = open(root + spamtrain + file)
            hamProb = math.log(train.hamProb)
            spamProb = math.log(train.spamProb)
            for word in f.read().split():
                if word in train.wGivenHam.keys():
                    hamProb += math.log(train.wGivenHam[word])
                if word in train.wGivenSpam.keys():
                    spamProb += math.log(train.wGivenSpam[word])
            if (spamProb > hamProb):
                spamRight += 1.0
    
    print "Overall accuracy:", ((hamRight + spamRight)/(hamFiles + spamFiles))*100, "%"
    print "Spam accuracy:", (spamRight/spamFiles)*100, "%"
    print "Ham accuracy:", (hamRight/hamFiles)*100, "%" 

if __name__ == '__main__':
    #got best accuracy with 2, 1
    script, k, m = sys.argv
    k = int(k)
    m = float(m)
    
    lexicon, Htotal, Stotal = buildLex(k)
    training = MAP(lexicon, Htotal, Stotal)
    training.estimate(m)
    test(training)