import copy
import numpy as np
import pandas as pd
import operator
from collections import Counter, OrderedDict


class HMMHelper():
	def __init__(self,observedSet,hiddenSet):
		self.observedSet = observedSet
		self.hiddenSet = hiddenSet
		self.transitionMatrix = None
		self.emmisionMatrix = None
		self.initialDistribution = [] 
		self.initialDistributionDict = dict()

	def calculateInitialDistribution(self):
		X1 = self.hiddenSet[0]
		total_number_of_states = len(self.hiddenSet)
		c = list(sorted(Counter(self.hiddenSet).items()))
		for item,freq in c:
			prob = freq/total_number_of_states
			self.initialDistribution.append(prob)
			self.initialDistributionDict[item] = prob


	def calculateTransitionMatrix(self):
		transitionDict = dict()
		emptyFreqDict = OrderedDict()



		# store all values
		for e in self.hiddenSet:
			if emptyFreqDict.get(str(e)) is None:
				emptyFreqDict[str(e)] = 0


		#initialize dictionary
		for state in self.hiddenSet:
			tempDict = copy.deepcopy(emptyFreqDict)
			transitionDict[str(state)] = tempDict


		for idx in range(0,len(self.hiddenSet)-1):
			element = str(self.hiddenSet[idx])
			nxtElement = str(self.hiddenSet[idx+1])
			transitionDict[element][nxtElement]+=1

		transitionMatrixDict = dict()

		for (state,valueDict) in sorted(transitionDict.items(),key=lambda i:(float(i[0]))):

			total_number_of_states = 0
			temp = dict()
			
			for k,v in valueDict.items():
					total_number_of_states+=v
			for (k,v) in sorted(valueDict.items(),key=lambda i:(float(i[0]))):
				if total_number_of_states != 0:
					prob = v/total_number_of_states
				else:
					prob = 0
				temp[k] = prob

			transitionMatrixDict[state] = temp


		return transitionMatrixDict


	def calculateEmissionMatrix(self):

		emissionDict = dict()

		emptyFreqDict = OrderedDict()

		# store all values
		for e in sorted(self.observedSet):
			if emptyFreqDict.get(str(e)) is None:
				emptyFreqDict[str(e)] = 0




		for observed, hidden in zip(self.observedSet,self.hiddenSet):
			observed = str(observed)
			hidden = str(hidden)

			if emissionDict.get(hidden) is None:
				tempDict = copy.deepcopy(emptyFreqDict)
				tempDict[observed] += 1
				emissionDict[hidden] = tempDict
			else:
				emissionDict[hidden][observed]+=1





		emissionMatrixDict = dict()
		for (state,valueDict) in sorted(emissionDict.items(),key=lambda i:(float(i[0]))):

			total_number_of_states = 0
			temp = dict()
			for k,v in valueDict.items():
					total_number_of_states+=v
			for k,v in sorted(valueDict.items(),key=lambda i:(float(i[0]))):
				if total_number_of_states != 0:
					prob = v/total_number_of_states
				else:
					prob = 0
				temp[k] = prob

			emissionMatrixDict[state] = temp


		return emissionMatrixDict

	def findUniqueStates(self,dataList,t= "int"):
		uniqueStates = []
		for element in tuple(set(dataList)):
			if t == "int":
				uniqueStates.append(str(int(element)))
			elif t == "origin":
				uniqueStates.append(str(element))
		return tuple(uniqueStates)






if __name__ == '__main__':

	hiddenSet = [1,2,3,4,5,6,7,8,9,10]
	observedSet = [0,0,3,5,8,10,20,8,3,2]
	HMM = HMM(observedSet,hiddenSet)
	transitionMatrixDict = HMM.calculateTransitionMatrix()
	emissionMatrixDict = HMM.calculateEmissionMatrix()
	HMM.calculateInitialDistribution()
	initialDistribution = HMM.initialDistribution








