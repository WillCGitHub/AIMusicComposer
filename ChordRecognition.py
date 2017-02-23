import math

import numpy as np
import RW_obj as rw

chordConstructionDict = {(1,5,8):'Major',(1,4,8):'Minor',(1,5,8,11):'7th',
							(1,5,8,12):'Major 7th',(1,4,8,11):'Minor 7th',
							(1,5,8,10):'6th',(1,4,8,10):'Minor 6th',(1,4,7):'Diminished',
							(1,4,7,10):'Diminished 7th',(1,4,7,11):'Hal diminished 7th',
							(1,5,9):'Augmented',(1,5,9,11):'7th #5',(1,5,8,11,15):'9th',
							(1,5,8,11,16):'7th #9',(1,5,8,12,15):'Major 9th',(1,5,8,15):'Added 9th',
							(1,4,8,11,15):'Minor 9th',(1,4,8,15):'Minor add 9th',(1,5,8,11,15,18):'11th',
							(1,4,8,11,15,18):'Minor 11th',(1,5,8,11,15,19):'Major 7th #11',(1,5,8,12,15,22):'13th',
							(1,4,8,12,15,18,22):'Minor 13th',(1,6,8):'sus4',(1,3,8):'sus2',(1,8):'5th',
							(1,2):'m2',(1,3):'M2',(1,4):'m3',(1,5):'M3',(1,6):'P4',(1,7):'TT',
							(1,9):'m6',(1,10):'M6',(1,11):'m7',(1,12):'M7',(1,13):'P8',(1,1):'U'}

class ChordRecognition:
	def __init__(self):
		self.listOfNotes = []

	def findBase(self,notes):
		return min(notes)

	def calculateIntervals(self,notes):
		diff = np.diff(notes)
		for idx, d in enumerate(diff):
			diff[idx] = abs(d)

		return diff

	def constructChord(self,diff):
		c = [1]
		for idx, d in enumerate(diff):
			c.append(d+c[idx])
		return c

	def isChord(self,notes):
		diff = self.calculateIntervals(notes)
		if len(diff) == 1:
			if diff[0] > 12:
				floor = math.floor(diff[0]/12)
				diff[0] -= 12*floor

		base = self.findBase(notes)
		constructedChord = self.constructChord(diff)
		temp = chordConstructionDict.get(tuple(constructedChord))
		if temp is None:
			return False
		if temp is not None:
			#print(temp)
			return True


	def checkChords(self,notes):
		notes = sorted(notes)


		if len(notes) >= 2: 

			if self.isChord(notes):
				return [notes]


			currLen = len(notes)
			chordEnumeration = []
			
			while (currLen >= 2):
				for idx in range(0,len(notes) - currLen+1):
					subNotes = notes[idx:idx+currLen]
					chordEnumeration.append(subNotes)
				currLen -= 1

			chordEnumeration = list(reversed(sorted(chordEnumeration,key = lambda s: len(s))))

			#print("notes:{} chordEnumeration: {}".format(notes,chordEnumeration))

			result = []
			for idx, c in enumerate(chordEnumeration):
				if len(c) > 1:
					if self.isChord(c):
						result.append(c)
						for inner_idx in range(idx,len(chordEnumeration)):
							chordEnumeration[inner_idx] = list(set(chordEnumeration[inner_idx]) - set(c))

			if len(result) >= 1:	
				return result
			return None
		else:
			return None
			
		
		








if __name__ == "__main__":

	cr = ChordRecognition()
	notes = [60,66,69]
	print(cr.findBase(notes))
	diff = cr.calculateIntervals(notes)
	print(cr.constructChord(diff))
	n = ['C','C#,Db','D','D#,Eb','E','F','F#,Gb','G','G#,Ab','A',"A#,Bb","B"]
	#for idx,note in enumerate(n):
		#print((idx+1,note))
	
	pitchDict = rw.load_obj('pitch_dict')
	print(pitchDict.get(45))
	print(pitchDict.get(65))
	print(cr.isChord([45,65]))







		