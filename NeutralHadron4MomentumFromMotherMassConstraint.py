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
        self.neutralMomentum = TVector3()
        self.calculatedNeutralHadron4Momentum = TLorentzVector()
        self.motherMass = 5.27962
        self.neutralMass = 0.939565413

    def event(self):
        particles = Belle2.PyStoreObj(self.particleList).obj()
        for particle in particles:
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
                self.neutralMomentum.SetMagThetaPhi(neutralP, self.neutralDirection.Theta(), self.neutralDirection.Phi())
                self.calculatedNeutralHadron4Momentum.SetVectM(self.neutralMomentum, self.neutralMass)
                neutral.set4Vector(self.calculatedNeutralHadron4Momentum)
                particle.set4Vector(neutral.get4Vector() + charged.get4Vector())
            else:  # Remove this Particle from its ParticleList
                

