import time
import os
import random
import operator

from sklearn.cluster import KMeans
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import mido
import extract_feature as ef
import MarkovChain as mc
import RW_obj as rw
import ChordRecognition as CR

import HMMHelper as hh
import HMM

import produceMidi 



class Note():
	def __init__(self,pitch,velocity,ticks_per_beat):
		self.status = True # note on 
		self.note_on_time = 0
		self.note_off_time = 0
		self.duration = 0
		self.pitch = pitch
		self.velocity = velocity
		self.ticks_per_beat = ticks_per_beat

	def __str__(self):
		return str(self.pitch)

	def __repr__(self):
		return self.__str__()

	def __eq__(self,other):
		if isinstance(other,Note):
			if self.pitch == other.pitch:
				return True
			else:
				return False
		elif isinstance(other,Chord):
			if self in other.notes:
				return True
			else:
				return False

			

	def calc_duration(self):
		"""# beat = # ticks / (ticks per beat )  """
		self.duration = round((self.note_off_time - self.note_on_time)/self.ticks_per_beat,1) # Unit(duration) in beat

	def get_data(self):
		return np.array([self.pitch,self.duration,self.velocity,self.note_on_time])







def listdir_nohidden(path):
	for f in os.listdir(path):
		if not f.startswith('.'):
			yield f


def analyze_file(midi_path):

	mid = mido.MidiFile(midi_path)

	data = []

	for i, track in enumerate(mid.tracks):
		current_time = 0
		note_dict = dict()
		
		
		for message in track:
			if isinstance(message,mido.MetaMessage):
				if message.type == "set_tempo":
					tempo = message.tempo

			if isinstance(message,mido.Message):
				if message.type == "program_change":
					if message.program != 0:
						break
					

				if message.type == "note_on" or message.type == "note_off":

					current_time += message.time
					#print(message)
					midi_bytes = message.bytes()
					temp = Note(midi_bytes[1],midi_bytes[2],float(mid.ticks_per_beat))
					if message.type == "note_on":
						temp.note_on_time = current_time
						if note_dict.get(temp.pitch) is None:
							note_dict[temp.pitch] = [temp]
						else:
							note_dict.get(temp.pitch).append(temp)
					elif message.type == "note_off":
						curr_notes = note_dict.get(temp.pitch)
						#assert(curr_note.status == True )
						if curr_notes is None:
							print("off before on")
						curr_note = curr_notes.pop(0)
						if curr_note.status is not True:
							print("\n\n\n\n\n##############################")
							print("ASSERTION ERORR HERE")
							print("##############################\n\n\n\n\n")
						curr_note.status = False
						curr_note.note_off_time = current_time
						curr_note.calc_duration()
						note_data = curr_note.get_data()

						data.append(note_data)
	
		

		df = pd.DataFrame(data = data, columns = ["Pitch","Duration","Velocity","Time"])

	return df

def list2DF(sortedList):
	data = []

	for s in sortedList:
		row = [s[1][0],s[1][1],s[1][2],s[0]]
		data.append(row)

	df = pd.DataFrame(data = data, columns = ["Pitch","Duration","Velocity","Time"])
	return df

def splitMelodyAndChord(df):
	cr = CR.ChordRecognition()
	
	timeLineDict = dict()
	for row in df.iterrows():
		pitch = int(row[1][0])
		duration = row[1][1]
		velocity = int(row[1][2])
		time = int(row[1][3])
		dictValue = timeLineDict.get(time)
		if dictValue is None:
			timeLineDict[time] = [[pitch,duration,velocity]]
		else:
			timeLineDict[time].append([pitch,duration,velocity])



	for k in timeLineDict.keys():
		data = timeLineDict.get(k)
		df = pd.DataFrame(data = data, columns = ["Pitch","Duration","Velocity"])
		timeLineDict[k] = df

	chordDict = dict()
	for k,v in timeLineDict.items():
		if len(v['Pitch']) >= 2:
			chord = list(v['Pitch'])
			durations = min(list(v['Duration']))
			velocities = max(list(v['Velocity']))
			chordResult = cr.checkChords(chord)
			if chordResult is not None:
				chordDict[k] = [chordResult,durations,velocities]
				# print("time: {}, chords: {}, result:{}\n".format(k,chord,chordResult))

	melodyDict = dict()


	for k,v in timeLineDict.items():
		haschord = chordDict.get(k)
		remainingNote = list(v['Pitch'])
		value = None
		if haschord is not None:

			for c in haschord[0]:

				remainingNote = list(set(remainingNote)- set(c))
				#print("all:{}\nthe chord:{}\nresult:{}\n".format(list(v['Pitch']),list(c),remainingNote))

			if len(remainingNote) > 1:
				#print("all:{} the chord:{} result:{}".format(list(v['Pitch']),list(c),remainingNote))
				pass

			elif len(remainingNote) == 1:
				value = remainingNote[0]
		else:
			value = list(v['Pitch'])[0]
		if value is not None:
			durations = min(list(v['Duration']))
			velocities = max(list(v['Velocity']))
			melodyDict[k] = [value,durations,velocities]
			#print(value)

	sortedMelody = list(sorted(melodyDict.items(),key =operator.itemgetter(0)))
	sortedChord = list(sorted(chordDict.items(),key = operator.itemgetter(0)))

	melodyDF = list2DF(sortedMelody)
	chordDF = list2DF(sortedChord)


	return melodyDF,chordDF



def labelingParts(df):

	X = []

	for row in df.iterrows():
			X.append([row[1][0]])


	X_train = np.array(X)

	kmeans = KMeans(n_clusters=2, random_state=0).fit(X_train)

	X_label = kmeans.labels_

	df['Label'] = pd.Series(np.array(X_label))
	return df


def plot(df):
	"""
	Dataframe format
	row[1][0] = 'Pitch'
	row[1][1] = 'Duration'
	row[1][2] = 'Velocity'
	row[1][3] = 'Time'
	row[1][4] = 'Label'
	"""


	upperX = []
	upperY = []
	lowerX = []
	lowerY = []

	
	for row in df.iterrows():
		if row[1][4] == 0:
			upperX.append(row[1][3])
			upperY.append(row[1][0])
		elif row[1][4] == 1:
			lowerX.append(row[1][3])
			lowerY.append(row[1][0])

	fig, ax = plt.subplots()

	ax.scatter(upperX, upperY, color='r', marker='^', alpha=.4)
	ax.scatter(lowerX, lowerY, color='b', marker='^', alpha=.4)
	#plt.xlim([20000,50000])
	plt.show()


if __name__ == "__main__":

	abs_path = "MIDI/test"
	MIDI_list = ef.listdir_nohidden(abs_path)
	total_result = []
	for a in MIDI_list:

		df = analyze_file(a)
		break

	labeledDF = labelingParts(df)

	#plot(labeledDF)

	dfUpper = df[df['Label'] == 0]
	dfLower = df[df['Label'] == 1]

	#print(dfUpper)
	pitch = list(dfUpper['Pitch'])
	tempP = []

	for p in pitch:
		tempP.append(str(p))
	duration = list(dfUpper['Duration'])

	pitchUniqueState = []
	for p in tuple(set(pitch)):
		pitchUniqueState.append(str(p))

	pitchUniqueState = tuple(pitchUniqueState)
	durationUniqueState = [] 
	for d in tuple(set(duration)):
		durationUniqueState.append(d)

	durationUniqueState = tuple(durationUniqueState)



	hh = hh.HMMHelper(tempP,duration)
	transitionDF,trans_prob = hh.calculateTransitionMatrix()
	emissionDF,emit_prob = hh.calculateEmissionMatrix()
	hh.calculateInitialDistribution()
	start_prob = hh.initialDistributionDict
	print(start_prob)
	model = HMM.Model(durationUniqueState, pitchUniqueState, start_prob, trans_prob, emit_prob)


	STATES_NUM = 3

	MIDI_path = "MIDI/test"



	num_of_states = STATES_NUM

	markov_p = ef.extract(MIDI_path,num_of_states,"test")
	pm = produceMidi.produceMidi()
	melody = pm.generate_melody(60,num_of_states,markov_p,init = 'bounded')
	sequence = []
	for m in melody:
		sequence.append(str(m.pitch))
	print(sequence)
	print(model.evaluate(sequence))
	print(model.decode(sequence))



	#time = dfUpper['Time']
	#plt.scatter(time,duration)
	#plt.show()



	#melody, chord = splitMelodyAndChord(dfUpper)
	#print(chord)
	"""

	time = []
	pitches = []
	for row in chord.iterrows():
		for note in row[1][0]:
			for n in note:
				pitches.append(n)
				time.append(row[1][3])


	print(len(pitches))
	print(len(time))
	plt.scatter(time,pitches)
	plt.show()
	"""







		


	



























