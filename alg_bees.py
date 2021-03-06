from alg_base import * 

class beesAlgorithm(algorithm):
    def __init__(self, **args):
        algorithm.__init__(self)
        self.opFlight = None
        self.opPlaceProbs = None
        self.plNum = None
        self.probScout = None
        algorithm.initAttributes(self, args)

    def sortPlaces(self):
        if self.metrics.task.getDir() == "min":
            self.env['places'].sort(key=lambda x: x['f'])
        else:
            self.env['places'].sort(key=lambda x: -x['f'])

    def start(self):
        algorithm.start(self, "places probs plNum", "x f p")
        pl = {'x':None, 'f':None}
        self.env['places'] = [pl.copy() for i in range(self.plNum + 1)]
        foreach(self.env['places'], self.opInit, self.args(key='x'))
        evaluate(self.env['places'], self.args(keyx='x', keyf='f'))
        self.sortPlaces()
        self.env['probs'] = self.opPlaceProbs(self.plNum, self.probScout)

    def reduceOp(self, x, y):
        return [y[i] if x[i] == None or y[i] != None and self.metrics.task.isBetter(y[i]['f'], x[i]['f']) else x[i] for i in range(len(x))]

    def extractOp(self, ind):
        return [{'x':ind['x'].copy(), 'f':ind['f']} if i == ind['p'] else None for i in range(self.plNum + 1)]

    def __call__(self):
        self.start()
        while not self.metrics.stopIt():
            self.newGeneration()
            foreach(self.population, self.opFlight, self.args(key='x'))
            self.evaluateAll()
            self.env['places'] = reducePop(self.population, self.extractOp, self.reduceOp, lambda x: x, initVal = self.env['places'])
            self.sortPlaces()

class beeFlight: 
    def __init__(self, opLocal, opGlobal):
        self.loc = opLocal
        self.glob = opGlobal
    def __call__(self, ind, args):
        env = args['env']
        m = env['plNum']
        probs = env['probs']
        p = np.random.choice(range(m + 1), p=probs)
        ind['p'] = p
        if p < m:
            ind['x'] = env['places'][p]['x'].copy()
            self.loc(ind, args)
        else:
            self.glob(ind, args)

def uniformPlacesProbs(num, pscout):
    probs = np.full(num + 1, (1 - pscout) / num )
    probs[num] = pscout 
    return probs   

class linearPlacesProbs:
    def __init__(self, elitism):
        self.elitism = elitism
    def __call__(self, num, pscout):
        a = self.elitism * (1 - pscout) * 2 / (num ** 2 - num)
        b = (1 - pscout) / num + a * (num - 1) / 2
        probs = -a * np.array(range(num + 1)) + b
        probs[num] = pscout
        return probs
