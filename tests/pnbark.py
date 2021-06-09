#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from basf2 import Path, process, B2INFO, statistics
from b2biiConversion import convertBelleMdstToBelleIIMdst
import modularAnalysis as ma
import vertex as vx

from neutralAnalysis.AddNeutralHadronHypothesis import AddNeutralHadronHypothesis
from neutralAnalysis.NeutralHadron4MomentumFromMotherMassConstraint import NeutralHadron4MomentumFromMotherMassConstraint
from utils.submit_parse import submit_info_parser, build_parser


isMC, url, basename = submit_info_parser(build_parser().parse_args())
mypath = Path()
convertBelleMdstToBelleIIMdst(url, enableLocalDB=False, path=mypath)

ma.fillParticleList('K-:sig', 'atcPIDBelle(3,2) > 0.6 and eIDBelle < 0.9 and muIDBelle < 0.9 and dr < 0.2 and abs(dz) < 2', path=mypath)
ma.fillParticleList('p+:sig', 'atcPIDBelle(4,3) > 0.6 and atcPIDBelle(4,2) > 0.6 and eIDBelle < 0.9 and muIDBelle < 0.9 and dr < 0.2 and abs(dz) < 2', path=mypath)
ma.reconstructDecay('@Xsd:kp -> K-:sig p+:sig', '', chargeConjugation=False, path=mypath)
vx.kFit('Xsd:kp', 0.0001, path=mypath)

AddNeutralHadronHypothesis(path=mypath)
ma.fillParticleList('anti-n0:sig', 'isFromECL > 0 and clusterBelleQuality == 0 and clusterTrackMatch == 0', path=mypath)
mypath.add_module('MVAExpert', listNames=['anti-n0:sig'], extraInfoName='nbarMVA', identifier='nbarMVA_20200717.xml')

ma.reconstructDecay('anti-B0:kpnbar -> Xsd:kp anti-n0:sig', '', chargeConjugation=False, path=mypath)
NeutralHadron4MomentumFromMotherMassConstraint('anti-B0:kpnbar', path=mypath)

ntupleVars = ['daughter(1,extraInfo(nbarMVA))', 'deltaE', 'M']
ma.variablesToNtuple('anti-B0:kpnbar', ntupleVars, treename='kpnbar', filename=basename, path=mypath)

process(mypath)
B2INFO(statistics)

