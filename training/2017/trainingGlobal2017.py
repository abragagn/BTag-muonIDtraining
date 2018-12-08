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
from keras.optimizers import SGD
from keras.callbacks import ModelCheckpoint

##### FUNCTIONS

def getKerasModel(inputDim, modelName, layerSize = 100, nLayers = 5, dropValue = 0.5):
	model = Sequential()
	model.add(Dense(layerSize, activation='relu', kernel_initializer='normal', input_dim=inputDim))
	model.add(Dropout(dropValue))

	for i in range(1, nLayers):
		model.add(Dense(layerSize, activation='relu', kernel_initializer='normal'))
		model.add(Dropout(dropValue))

	model.add(Dense(2, activation='softmax'))

	sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
	model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
	
	model.save(modelName)
	model.summary()
	return

##### MAIN

# Setup TMVA
TMVA.Tools.Instance()
TMVA.PyMethodBase.PyInitialize()

region = sys.argv[1]
var1 = sys.argv[2]
var2 = sys.argv[3]

DNNFLAG = True
BDTFLAG = True

if region != 'Barrel' and region != 'Endcap':
	print 'Invalid argument region'
	sys.exit()

if var1 != 'wIP' and var1 != 'woIP':
	print 'Invalid argument var1'
	sys.exit()

if var2 != 'wIso' and var2 != 'woIso':
	print 'Invalid argument var2'
	sys.exit()


outputName = 'TMVAGlobal' + region + '2017' + var1 + var2 + '.root'


output = TFile.Open(outputName, 'RECREATE')

factory = TMVA.Factory('TMVAClassification', output,
                       '!V:!Silent:Color:DrawProgressBar:AnalysisType=Classification')

# Load data
dataBs = TFile.Open('bankBsJpsiPhi17.root')
dataBsD0 = TFile.Open('bankBsJpsiPhiDGamma017.root')
dataBu = TFile.Open('bankBuJpsiK17.root')
dataBd = TFile.Open('bankBdJpsiKx17.root')
dataBdNR = TFile.Open('bankBdKxMuMu17.root')

treeBs = dataBs.Get('PDsecondTree')
treeBsD0 = dataBsD0.Get('PDsecondTree')
treeBu = dataBu.Get('PDsecondTree')
treeBd = dataBd.Get('PDsecondTree')
treeBdNR = dataBdNR.Get('PDsecondTree')

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

mycutgen = 'muoPt>=2&&(muoEvt%10)<8'

if region == 'Barrel':
	mycutgen += '&&abs(muoEta)<1.2'
elif region == 'Endcap':
	mycutgen += '&&abs(muoEta)>=1.2'

mycuts = mycutgen + '&&abs(muoLund)==13&&muoAncestor>=0'
mycutb = mycutgen + '&&abs(muoLund)!=13'

dataloader.AddSignalTree(treeBs, 1.0)
dataloader.AddSignalTree(treeBsD0, 1.0)
dataloader.AddSignalTree(treeBu, 1.0)
dataloader.AddSignalTree(treeBd, 1.0)
dataloader.AddSignalTree(treeBdNR, 1.0)

dataloader.AddBackgroundTree(treeBs, 1.0)
dataloader.AddBackgroundTree(treeBsD0, 1.0)
dataloader.AddBackgroundTree(treeBu, 1.0)
dataloader.AddBackgroundTree(treeBd, 1.0)
dataloader.AddBackgroundTree(treeBdNR, 1.0)

if region == 'Barrel':
	nBkg = '1000'
	nSgn = '1000'
elif region == 'Endcap':
	nBkg = '1000'
	nSgn = '1000'

dataloaderOpt = 'nTrain_Signal=' + nSgn + ':nTrain_Background=' + nBkg + ':nTest_Signal=' + nSgn + ':nTest_Background=' + nBkg
dataloaderOpt += ':SplitMode=Random:NormMode=NumEvents:!V'

dataloader.PrepareTrainingAndTestTree(TCut(mycuts), TCut(mycutb), dataloaderOpt)

if DNNFLAG:
	# Define model
	modelName = 'model' + region + '17' + var1 + var2 + '.h5'
	dropValue = 0.5
	layerSize = 200
	nLayers = 5

	getKerasModel(nVars, modelName, layerSize, nLayers, dropValue)

	# Book methods
	dnnOptions = '!H:!V:FilenameModel=' + modelName + ':NumEpochs=1000:TriesEarlyStopping=50:BatchSize=128'

	
	preprocessingOptions = ':VarTransform=N'
	preprocessingOptions += ',G('
	for var in varList:
		if var[0] == 'muoQprod':
			preprocessingOptions += var[0] + ','
	preprocessingOptions = preprocessingOptions[:-1]
	preprocessingOptions +=  '),N'

	dnnName = 'DNNGlobal' + region + '2017' + var1 + var2

	factory.BookMethod(dataloader, TMVA.Types.kPyKeras, dnnName, dnnOptions + preprocessingOptions)

if BDTFLAG:
	bdtOptions = '!H:!V:UseBaggedBoost:BaggedSampleFraction=0.6:NTrees=600:MaxDepth=8:nCuts=100:MinNodeSize=1.0%:BoostType=RealAdaBoost:AdaBoostBeta=0.3:SigToBkgFraction=2:DoBoostMonitor=True'
	bdtName = 'BDTGlobal' + region + '2017' + var1 + var2
	factory.BookMethod(dataloader, TMVA.Types.kBDT, bdtName, bdtOptions)

# Run training, test and evaluation
factory.TrainAllMethods()
factory.TestAllMethods()
factory.EvaluateAllMethods()

#TMVA.TMVAGui("TMVA_keras.root")
