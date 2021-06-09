from basf2 import Module
from ROOT import Belle2


class AddNeutralHadronHypothesis(Module):

    def __init__(self, path=None):
        super().__init__()
        self.path = path
        self.path.add_module(self)

        self.eclClusters = Belle2.PyStoreArray('ECLClusters')

    def event(self):
        for eclCluster in self.eclClusters:
            eclCluster.addHypothesis(Belle2.ECLCluster.EHypothesisBit.c_neutralHadron)

