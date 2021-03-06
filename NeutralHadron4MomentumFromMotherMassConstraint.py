import ROOT
from ROOT import TLorentzVector, TVector3
from ROOT import Belle2
from basf2 import Module


class NeutralHadron4MomentumFromMotherMassConstraint(Module):

    def __init__(self, particleList, path=None):
        super().__init__()
        self.particleList = particleList
        self.path = path
        self.path.add_module(self)

        self.neutralDirection = TVector3()
        self.neutral3Momentum = TVector3()
        self.neutral4Momentum = TLorentzVector()
        self.motherMass = 5.27962
        self.neutralMass = 0.939565413

    def event(self):
        particleList = Belle2.PyStoreObj(self.particleList).obj()
        toRemove = ROOT.std.vector('unsigned int')()
        for particle in particleList:
            #self.motherMass = particle.getMass()  # XXX: Should move this to ``initialize`` later
            charged = particle.getDaughter(0)
            neutral = particle.getDaughter(1)
            #self.neutralMass = neutral.getMass()  # XXX: Should move this to ``initialize`` later
            self.neutralDirection = (neutral.getECLCluster().getClusterPosition() - charged.getVertex()).Unit()
            a = charged.getMomentum() * self.neutralDirection
            b = (self.motherMass**2 - self.neutralMass**2 - charged.get4Vector().Mag2()) / 2.
            c = charged.getEnergy()
            d = self.neutralMass**2
            D = (a**2 - c**2) * d + b**2
            if D >= 0:
                neutralP = (-1. * a * b - c * D**(0.5)) / (a**2-c**2)
                self.neutral3Momentum.SetMagThetaPhi(neutralP, self.neutralDirection.Theta(), self.neutralDirection.Phi())
                self.neutral4Momentum.SetVectM(self.neutral3Momentum, self.neutralMass)
                neutral.set4Vector(self.neutral4Momentum)
                particle.set4Vector(neutral.get4Vector() + charged.get4Vector())
            else:  # Remove this Particle from its ParticleList
                toRemove.push_back(particle.getArrayIndex())
        particleList.removeParticles(toRemove)

