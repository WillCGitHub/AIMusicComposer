import math

import numpy as np
import RW_obj as rw
"""
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
"""
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
							(1,9):'m6',(1,10):'M6',(1,11):'m7',(1,12):'M7',(1,13):'P8'}
class ChordRecognition:
	def __init__(self):
		self.listOfNotes = []
		try:
			self.chordDict = rw.load_obj("chordDict")
		except:
			# construct if not exist
			self.constructChordDict()
			self.constructNameToChordDict()

	def calculateIntervals(self,notes):
		diff = np.diff(notes)
		for idx, d in enumerate(diff):
			diff[idx] = abs(d)

		return diff

	def constructChord(self,notes):
		notes = sorted(notes)

		if len(notes) == 1:
			notes.append(notes[0])

		if len(notes) == 2:
			diff = self.calculateIntervals(notes)

			quotient = diff[0]/12
			if quotient > 1:
				notes[-1]-= int(12*(int(quotient)))

		min_val = min(notes)

		num_of_octave = int(min_val /12)

		displacement = num_of_octave*12

		constructedChord = []
		for n in notes:
			constructedChord.append(int(n-displacement+1))
		return constructedChord



	def inversion(self,combination,idx = 0):
		"""
		combination -- a list of numbers represent notes
		idx 0 -- first inversion
		idx 1 -- second inversion
		"""
		new_combo = combination[idx+1:]
		for i in range(0,idx+1):
			new_combo.append(combination[i]+12)


		return new_combo

	def constructChordDict(self):
		chordConstructionDict_new = dict()
		pitchList = ['C','C#','D','D#','E','F','F#','G','G#','A',"A#","B"]
		for combination,chordName in chordConstructionDict.items():
			for pitchIdx,pitch in enumerate(pitchList):
				l = [c+pitchIdx for c in list(combination)]
				inversion1 = self.inversion(l)
				if len(l) >=3:
					inversion2 = self.inversion(l,idx=1)
					chordConstructionDict_new[tuple(l)] = pitch+"-"+chordName
					chordConstructionDict_new[tuple(inversion1)] = pitch+"-"+chordName+"-Inversion1"
					chordConstructionDict_new[tuple(inversion2)] = pitch+"-"+chordName+"-Inversion2"
					print(pitch+"-"+chordName,l,pitch+"-"+chordName+"-Inversion1",inversion1,pitch+"-"+chordName+"-Inversion2",inversion2)
				else:
					chordConstructionDict_new[tuple(l)] = pitch+"-"+chordName
					chordConstructionDict_new[tuple(inversion1)] = pitch+"-"+chordName+"-Inversion1"
					print(pitch+"-"+chordName,l,pitch+"-"+chordName+"-Inversion1",inversion1)
		rw.save_obj(chordConstructionDict_new,"chordDict")

	def constructNameToChordDict(self):
		chordDict = rw.load_obj("chordDict")
		nameToChordDict = dict()
		for k,v in chordDict.items():
			nameToChordDict[v] = k

		rw.save_obj(nameToChordDict,"nameToChordDict")

	def isChord(self,notes):

		constructedChord = self.constructChord(notes)
		
		temp = self.chordDict.get(tuple(constructedChord))
		if temp is None:
			return False,[]
		if temp is not None:
			return True, [temp]


	def checkChords(self,notes):
		notes = sorted(notes)


		if len(notes) >= 2: 

			#if self.isChord(notes):
				#return [notes]


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
					status,chordList = self.isChord(c)
					if status:
						result.append(chordList[0])
						for inner_idx in range(idx,len(chordEnumeration)):
							chordEnumeration[inner_idx] = list(set(chordEnumeration[inner_idx]) - set(c))

			if len(result) >= 1:	
				return result
			return None
		else:
			return None
			
		
		








if __name__ == "__main__":

	cr = ChordRecognition()
	"""
	notes = [60,66,69]
	print(cr.findBase(notes))
	diff = cr.calculateIntervals(notes)
	print(cr.constructChord(diff))
	n = ['C','C#,Db','D','D#,Eb','E','F','F#,Gb','G','G#,Ab','A',"A#,Bb","B"]
	#for idx,note in enumerate(n):
		#print((idx+1,note))
	"""	
	#pitchDict = rw.load_obj('pitch_dict')
	#pitchList = ['C','C#','D','D#','E','F','F#','G','G#','A',"A#","B"]
	#print(pitchDict.get(45))
	#print(pitchDict.get(65))
	#print(cr.isChord([45,65]))

	














		