#!/usr/bin/env python

from ROOT import TMVA, TFile, TTree, TCut
from subprocess import call
from os.path import isfile
import sys
import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

import numpy as np
import keras
import h5py

from keras.models import Sequential
from keras.layers import Dense, Activation, Conv2D, MaxPooling2D, Flatten, Dropout
from keras.regularizers import l2
from keras.optimizers import SGD, Adam
from keras.callbacks import ModelCheckpoint

##### FUNCTIONS

def getKerasModel(inputDim, modelName, layerSize = 200, nLayers = 2, dropValue = 0.2, optLabel = 'adam'):
    model = Sequential()
    model.add(Dense(layerSize, activation='relu', kernel_initializer='normal', input_dim=inputDim))
    model.add(Dropout(dropValue))

    for i in range(1, nLayers):
        model.add(Dense(layerSize, activation='relu', kernel_initializer='normal'))
        model.add(Dropout(dropValue))

    model.add(Dense(2, activation='softmax'))

    opt = Adam(lr=0.001)
    if optLabel == 'sgd':
        opt = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)

    model.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['accuracy'])
    model.save(modelName)
    model.summary()
    return

##### MAIN

# Development Flags
DNNFLAG = True
BDTFLAG = False
TESTMODE = False

# Setup TMVA
TMVA.Tools.Instance()
TMVA.PyMethodBase.PyInitialize()

# Parameters
#region = sys.argv[1]
#var1 = sys.argv[2]
#var2 = sys.argv[3]

region = 'Full'
var1 = 'woIP'
var2 = 'wIso'

if TESTMODE:
    dropValue = sys.argv[4]
    layerSize = sys.argv[5]
    nLayers = sys.argv[6]
    optLabel = sys.argv[7]
    dropValue = float(dropValue)
    layerSize = int(layerSize)
    nLayers = int(nLayers)

if region != 'Barrel' and region != 'Endcap' and region != 'Full':
    print 'Invalid argument region'
    sys.exit()

if var1 != 'wIP' and var1 != 'woIP':
    print 'Invalid argument var1'
    sys.exit()

if var2 != 'wIso' and var2 != 'woIso':
    print 'Invalid argument var2'
    sys.exit()

if TESTMODE:
    region += 'Test'

outputName = 'TMVAMuonID' + region + '2017' + var1 + var2 + '.root'
output = TFile.Open(outputName, 'RECREATE')

# Factory
factory = TMVA.Factory('TMVAClassification', output,
                       '!V:!Silent:Color:DrawProgressBar:AnalysisType=Classification')

# Load data
if TESTMODE:
    data = TFile.Open('bankBsJpsiPhi17.root')
    tree = data.Get('PDsecondTree')
else:
    dataBs = TFile.Open('bankBsJpsiPhi17.root')
    dataBsD0 = TFile.Open('bankBsJpsiPhiDGamma017.root')
    dataBu = TFile.Open('bankBuJpsiK17.root')
    dataBd = TFile.Open('bankBdJpsiKx17.root')
    dataBdNR = TFile.Open('bankBdKxMuMu17.root')

    treeBs = dataBs.Get('PDsecondTree')
    treeBsD0 = dataBsD0.Get('PDsecondTree')
    treeBu = dataBu.Get('PDsecondTree')
    treeBd = dataBd.Get('PDsecondTree')

dataloader = TMVA.DataLoader('dataset')

# add variables
varList = [
    ('muoPt', 'F')
    ,('abs(muoEta)', 'F')
    ,('muoSegmComp', 'F')
    ,('muoChi2LM', 'F')
    ,('muoChi2LP', 'F')
    ,('muoGlbTrackTailProb', 'F')
    ,('muoIValFrac', 'F')
    ,('muoLWH', 'I')
    ,('muoTrkKink', 'F')
    ,('muoGlbKinkFinderLOG', 'F')
    ,('muoTimeAtIpInOutErr', 'F')
    ,('muoOuterChi2', 'F')
    ,('muoInnerChi2', 'F')
    ,('muoTrkRelChi2', 'F')
    ,('muoVMuonHitComb', 'I')
    ,('muoGlbDeltaEtaPhi', 'F')
    ,('muoStaRelChi2', 'F')
    ,('muoTimeAtIpInOut', 'F')
    ,('muoValPixHits', 'I')
    ,('muoNTrkVHits', 'I')
    ,('muoGNchi2', 'F')
    ,('muoVMuHits', 'I')
    ,('muoNumMatches', 'F')
    ,('muoQprod', 'I')
    ]


if var1 == 'wIP':
    varList.append(('trkDxy/trkExy', 'F'))
    varList.append(('trkDz/trkEz', 'F'))
if var2 == 'wIso':
    varList.append(('muoPFiso', 'F'))

nVars = 0
for var in varList:
    dataloader.AddVariable( var[0], var[1] )
    nVars += 1

dataloader.AddSpectator( 'muoEvt', 'I' )

# prepare dataloader

mycutgen = 'muoPt>=2'
#mycutgen += '&&(muoEvt%10)<8'

if region == 'Barrel':
    mycutgen += '&&abs(muoEta)<1.2'
elif region == 'Endcap':
    mycutgen += '&&abs(muoEta)>=1.2'

mycuts = mycutgen + '&&abs(muoLund)==13&&muoAncestor>=0'
mycutb = mycutgen + '&&abs(muoLund)!=13'

if TESTMODE:
    dataloader.AddSignalTree(tree, 1.0)
    dataloader.AddBackgroundTree(tree, 1.0)
else:
    dataloader.AddSignalTree(treeBs, 1.0)
    dataloader.AddSignalTree(treeBsD0, 1.0)
    dataloader.AddSignalTree(treeBu, 1.0)
    dataloader.AddSignalTree(treeBd, 1.0)

    dataloader.AddBackgroundTree(treeBs, 1.0)
    dataloader.AddBackgroundTree(treeBsD0, 1.0)
    dataloader.AddBackgroundTree(treeBu, 1.0)
    dataloader.AddBackgroundTree(treeBd, 1.0)

if region == 'Barrel':
    nBkg = '49800'
    nSgn = '500000'
    nBkgTest = '49800'
    nSgnTest = '500000'
elif region == 'Endcap':
    nBkg = '111750'
    nSgn = '1120000'
    nBkgTest = '111750'
    nSgnTest = '1120000'
elif region == 'Full':
    nBkg = '345000'
    nSgn = '690000'
    nBkgTest = '115000'
    nSgnTest = '230000'

nBkg = '350000'
nSgn = '3000000'
nBkgTest = '0'
nSgnTest = '0'

if TESTMODE:
    nBkg = '50000'
    nSgn = '100000'
    nBkgTest = '50000'
    nSgnTest = '100000'

dataloaderOpt = 'nTrain_Signal=' + nSgn + ':nTrain_Background=' + nBkg + ':nTest_Signal=' + nSgnTest + ':nTest_Background=' + nBkgTest
dataloaderOpt += ':SplitMode=Random:NormMode=EqualNumEvents:!V'

dataloader.PrepareTrainingAndTestTree(TCut(mycuts), TCut(mycutb), dataloaderOpt)

if DNNFLAG:
    # Define model
    modelName = 'model' + region + '17' + var1 + var2 + '.h5'

    if not TESTMODE:
        dropValue = 0.2
        layerSize = 200
        nLayers = 2
        optLabel = 'adam'

    getKerasModel(nVars, modelName, layerSize, nLayers, dropValue, optLabel)

    # Book methods
    dnnOptions = '!H:!V:FilenameModel=' + modelName + ':NumEpochs=200:TriesEarlyStopping=20:BatchSize=512:ValidationSize=30%:Tensorboard=./logs'

    iVar = 0
    preprocessingOptions = ':VarTransform=N'
    preprocessingOptions += ',G('
    for var in varList:
        if var[0] == 'muoQprod':
            iVar += 1
            continue
        preprocessingOptions += '_V' + str(iVar) + '_' + ','
        iVar += 1
    preprocessingOptions = preprocessingOptions[:-1]
    preprocessingOptions +=  '),N'
    
    dnnName = 'DNNMuonID' + region + '2017' + var1 + var2

    factory.BookMethod(dataloader, TMVA.Types.kPyKeras, dnnName, dnnOptions + preprocessingOptions)
    
if BDTFLAG:
    bdtOptions = '!H:!V:UseBaggedBoost:BaggedSampleFraction=0.6:NTrees=600:MaxDepth=8:nCuts=100:MinNodeSize=1.0%:BoostType=RealAdaBoost:AdaBoostBeta=0.3:SigToBkgFraction=2:DoBoostMonitor=True'
    bdtName = 'BDTMuonID' + region + '2017' + var1 + var2
    factory.BookMethod(dataloader, TMVA.Types.kBDT, bdtName, bdtOptions)

# Run training, test and evaluation
factory.TrainAllMethods()
factory.TestAllMethods()
factory.EvaluateAllMethods()

#TMVA.TMVAGui("TMVA_keras.root")
