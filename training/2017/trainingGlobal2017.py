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


# Setup TMVA
TMVA.Tools.Instance()
TMVA.PyMethodBase.PyInitialize()

region = sys.argv[1]
var1 = sys.argv[2]
var2 = sys.argv[3]

kerasFlag = True
bdtFlag = True

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
dataBdNS = TFile.Open('bankBdKxMuMu17.root')

treeBs = dataBs.Get('PDsecondTree')
treeBsD0 = dataBsD0.Get('PDsecondTree')
treeBu = dataBu.Get('PDsecondTree')
treeBd = dataBd.Get('PDsecondTree')
treeBdNS = dataBdNS.Get('PDsecondTree')

dataloader = TMVA.DataLoader('dataset')

# add variables
dataloader.AddVariable( 'muoPt', 'F' )
dataloader.AddVariable( 'abs(muoEta)', 'F' )
dataloader.AddVariable( 'muoSegmComp', 'F' )
dataloader.AddVariable( 'muoChi2LM', 'F' )
dataloader.AddVariable( 'muoChi2LP', 'F' )
dataloader.AddVariable( 'muoGlbTrackTailProb', 'F' )
dataloader.AddVariable( 'muoIValFrac', 'F' )
dataloader.AddVariable( 'muoLWH', 'I' )
dataloader.AddVariable( 'muoTrkKink', 'F' )
dataloader.AddVariable( 'muoGlbKinkFinderLOG', 'F' )
dataloader.AddVariable( 'muoTimeAtIpInOutErr', 'F' )
dataloader.AddVariable( 'muoOuterChi2', 'F' )
dataloader.AddVariable( 'muoInnerChi2', 'F' )  
dataloader.AddVariable( 'muoTrkRelChi2', 'F' )
dataloader.AddVariable( 'muoVMuonHitComb', 'I' )
dataloader.AddVariable( 'muoGlbDeltaEtaPhi', 'F' )
dataloader.AddVariable( 'muoStaRelChi2', 'F' )
dataloader.AddVariable( 'muoTimeAtIpInOut', 'F' )
dataloader.AddVariable( 'muoValPixHits', 'I' )
dataloader.AddVariable( 'muoNTrkVHits', 'I' )
dataloader.AddVariable( 'muoGNchi2', 'F' )
dataloader.AddVariable( 'muoVMuHits', 'I' )
dataloader.AddVariable( 'muoNumMatches', 'F' )
dataloader.AddVariable( 'muoQprod', 'I' )
if var1 == 'wIP':
	dataloader.AddVariable( 'trkDxy/trkExy', 'F' )
	dataloader.AddVariable( 'trkDz/trkEz', 'F' )
if var2 == 'wIso':
	dataloader.AddVariable( 'muoPFiso', 'F' )


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
dataloader.AddSignalTree(treeBdNS, 1.0)

dataloader.AddBackgroundTree(treeBs, 1.0)
dataloader.AddBackgroundTree(treeBsD0, 1.0)
dataloader.AddBackgroundTree(treeBu, 1.0)
dataloader.AddBackgroundTree(treeBd, 1.0)
dataloader.AddBackgroundTree(treeBdNS, 1.0)

if region == 'Barrel':
	nBkg = '20000'
	nSgn = '40000'
elif region == 'Endcap':
	nBkg = '55000'
	nSgn = '55000'

dataloaderOpt = 'nTrain_Signal=' + nSgn + ':nTrain_Background=' + nBkg + ':nTest_Signal=' + nSgn + ':nTest_Background=' + nBkg
dataloaderOpt += ':SplitMode=Random:NormMode=NumEvents:!V'

dataloader.PrepareTrainingAndTestTree(TCut(mycuts), TCut(mycutb), dataloaderOpt)

if kerasFlag:
	# Define model
	dropValue = 0.5
	layerSize = 200
	inputDim = 24
	if var1 == 'wIP':
		inputDim += 2
	if var2 == 'wIso':
		inputDim += 1

	model = Sequential()

	model.add(Dense(layerSize, activation='relu', kernel_initializer='normal', input_dim=inputDim))
	model.add(Dropout(dropValue))

	model.add(Dense(layerSize, activation='relu', kernel_initializer='normal'))
	model.add(Dropout(dropValue))

	model.add(Dense(layerSize, activation='relu', kernel_initializer='normal'))
	model.add(Dropout(dropValue))

	model.add(Dense(layerSize, activation='relu', kernel_initializer='normal'))
	model.add(Dropout(dropValue))

	model.add(Dense(layerSize, activation='relu', kernel_initializer='normal'))
	model.add(Dropout(dropValue))

	model.add(Dense(2, activation='softmax'))

	# Set loss and optimizer
	sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
	model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

	# Store model to file
	modelName = 'model' + region + '17' + var1 + var2 + '.h5'
	model.save(modelName)
	model.summary()

	# Book methods
	dnnOptions = '!H:!V:FilenameModel=' + modelName + ':NumEpochs=1000:TriesEarlyStopping=50:BatchSize=128'

	dnnOptions += ':VarTransform=N'
	dnnOptions += ',G(_V0_,_V1_,_V2_,_V3_,_V4_,_V5_,_V6_,_V8_,_V9_,_V10_,_V11_,_V12_,_V13_,_V15_,_V16_,_V17_,_V20_,_V22_'
	if var1 == 'wIP' and var2 == 'wIso':
		dnnOptions += ',_V24_,_V25_,_V26_'
	elif var1 == 'wIP' and var2 == 'woIso':
		dnnOptions += ',_V24_,_V25_'
	elif var1 == 'woIP' and var2 == 'wIso':
		dnnOptions += ',_V24_'
	dnnOptions += '),N'

	dnnName = 'DNNGlobal' + region + '2017' + var1 + var2

	factory.BookMethod(dataloader, TMVA.Types.kPyKeras, dnnName, dnnOptions)

	modelName_PT = 'preTrainedModels/TrainedModel_DNNGlobal' + region + '2016' + var1 + var2 + '.h5'
	dnnOptions_PT = '!H:!V:FilenameModel=' + modelName_PT + ':NumEpochs=1000:TriesEarlyStopping=50:BatchSize=64'
	
	dnnOptions_PT += ':VarTransform=N'
	dnnOptions_PT += ',G(_V0_,_V1_,_V2_,_V3_,_V4_,_V5_,_V6_,_V8_,_V9_,_V10_,_V11_,_V12_,_V13_,_V15_,_V16_,_V17_,_V20_,_V22_'
	if var1 == 'wIP' and var2 == 'wIso':
		dnnOptions_PT += ',_V24_,_V25_,_V26_'
	elif var1 == 'wIP' and var2 == 'woIso':
		dnnOptions_PT += ',_V24_,_V25_'
	elif var1 == 'woIP' and var2 == 'wIso':
		dnnOptions_PT += ',_V24_'
	dnnOptions_PT += '),N'

	dnnName_PT = 'DNNPTGlobal' + region + '2017' + var1 + var2

	factory.BookMethod(dataloader, TMVA.Types.kPyKeras, dnnName_PT, dnnOptions_PT)

if bdtFlag:
	bdtOptions = '!H:!V:UseBaggedBoost:BaggedSampleFraction=0.6:NTrees=600:MaxDepth=8:nCuts=100:MinNodeSize=1.0%:BoostType=RealAdaBoost:AdaBoostBeta=0.3:SigToBkgFraction=2:DoBoostMonitor=True'
	bdtName = 'BDTGlobal' + region + '2017' + var1 + var2
	factory.BookMethod(dataloader, TMVA.Types.kBDT, bdtName, bdtOptions)

# Run training, test and evaluation
factory.TrainAllMethods()
factory.TestAllMethods()
factory.EvaluateAllMethods()

#TMVA.TMVAGui("TMVA_keras.root")
