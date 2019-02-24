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

def getKerasModel(inputDim, modelName, layerSize = 100, nLayers = 5, dropValue = 0.5, optLabel = 'adam'):
    model = Sequential()
    model.add(Dense(layerSize, activation='relu', kernel_initializer='normal', input_dim=inputDim))
    model.add(Dropout(dropValue))

    for i in range(1, nLayers):
        model.add(Dense(layerSize, activation='relu', kernel_initializer='normal'))
        model.add(Dropout(dropValue))

    model.add(Dense(2, activation='softmax'))

    if optLabel == 'adam':
        opt = Adam(lr=0.001)
    elif optLabel == 'sgd':
        opt = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)

    model.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['accuracy'])
    model.save(modelName)
    model.summary()
    return

##### MAIN

# Setup TMVA
TMVA.Tools.Instance()
TMVA.PyMethodBase.PyInitialize()

name = 'Full2017Scan'

outputName = 'TMVAMuonID' + name + '.root'
output = TFile.Open(outputName, 'RECREATE')

# Factory
factory = TMVA.Factory('TMVAClassification', output, '!V:!Silent:Color:DrawProgressBar:AnalysisType=Classification')

# Load data
data = TFile.Open('../bankBsJpsiPhi17.root')
tree = data.Get('PDsecondTree')

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
    ,('muoPFiso', 'F')
    ]

nVars = 0
for var in varList:
    dataloader.AddVariable( var[0], var[1] )
    nVars += 1

dataloader.AddSpectator( 'muoEvt', 'I' )

# prepare dataloader

mycutgen = 'muoPt>=2'
mycuts = mycutgen + '&&abs(muoLund)==13&&muoAncestor>=0'
mycutb = mycutgen + '&&abs(muoLund)!=13'

dataloader.AddSignalTree(tree, 1.0)
dataloader.AddBackgroundTree(tree, 1.0)

nBkg = '180000'
nSgn = '360000'

dataloaderOpt = 'nTrain_Signal=' + nSgn + ':nTrain_Background=' + nBkg + ':nTest_Signal=' + nSgn + ':nTest_Background=' + nBkg
dataloaderOpt += ':SplitMode=Random:NormMode=NumEvents:!V'

dataloader.PrepareTrainingAndTestTree(TCut(mycuts), TCut(mycutb), dataloaderOpt)

# Define model
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

ntu_nLayers = (1, 2, 3)
ntu_layerSize = (150, 200, 250)
ntu_dropValue = (0.0, 0.1, 0.2)
optLabel = 'adam'

for nLayers in ntu_nLayers:
    for layerSize in ntu_layerSize:
        for dropValue in ntu_dropValue:
            suffix = '_' + str(nLayers) + '_' + str(layerSize) + '_' + str(int(dropValue*10))
            modelName = 'model' + name + suffix +'.h5'
            getKerasModel(nVars, modelName, layerSize, nLayers, dropValue, optLabel)
            dnnOptions = '!H:!V:FilenameModel=' + modelName + ':NumEpochs=100:TriesEarlyStopping=20:BatchSize=512'
            logPath = ':Tensorboard=./logs/' + suffix + '/'
            dnnOptions += logPath
            dnnName = 'DNNMuonID' + name + suffix
            factory.BookMethod(dataloader, TMVA.Types.kPyKeras, dnnName, dnnOptions + preprocessingOptions)

# Run training, test and evaluation
factory.TrainAllMethods()
factory.TestAllMethods()
factory.EvaluateAllMethods()

#TMVA.TMVAGui("TMVA_keras.root")
