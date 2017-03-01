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
		self.duration = round((self.note_off_time - self.note_on_time)/self.ticks_per_beat,3) # Unit(duration) in beat

		# inaccurate MIDI file causes duration 0 notes
		if self.duration == 0:
			self.duration = 0.125

	def get_data(self):
		return np.array([self.pitch,self.duration,self.velocity,self.note_on_time])




def listdir_nohidden(path):
	for f in os.listdir(path):
		if not f.startswith('.'):
			yield f

def abs_diff(a,b):
	return abs(a-b)

def regulateTime(time,ticks_per_beat):
	#print("Time is: {}".format(time))
	timeList = [6,4,3,2,1.5,1,0.75,0.5,0.375,0.333,0.25,0.1875,0.125]
	time_in_beat = time / ticks_per_beat
	#print("time in beat: {}".format(time_in_beat))
	accurateBeat = 0

	if time_in_beat in timeList:
		#print("in list")
		return time


	for idx in range(0,len(timeList)):
		
		curr_time = timeList[idx]

		if idx < len(timeList)-1:
			nxt_time = timeList[idx+1]
		else:
			nxt_time = 0

		if (idx == 0) and (time_in_beat > curr_time):
			accurateBeat = curr_time 
			#print("time {} greater than first item")
			break
		if (time_in_beat < curr_time) and (time_in_beat > nxt_time):
			#print("time {} in the interval {} {}".format(time_in_beat,curr_time,nxt_time))
			diff_to_curr = abs_diff(time_in_beat,curr_time)
			diff_to_nxt = abs_diff(time_in_beat,nxt_time)
			if diff_to_curr >= diff_to_nxt:
				accurateBeat = nxt_time
			else:
				accurateBeat = curr_time
			break



	#print("accurate beat {}".format(accurateBeat))
	result = accurateBeat * ticks_per_beat
	return result



def analyze_file(midi_path):

	mid = mido.MidiFile(midi_path)

	data = []
	pitchDict = rw.load_obj("pitch_dict")
	for i, track in enumerate(mid.tracks):
		current_time = 0
		current_beats = 0
		note_dict = dict()
		
		
		for message in track:
			if isinstance(message,mido.MetaMessage):
				if message.type == "set_tempo":
					tempo = message.tempo
				if message.type == "time_signature":
					beats_per_bar = message.denominator


			if isinstance(message,mido.Message):
				if message.type == "program_change":
					if message.program != 0:
						break
					

				if message.type == "note_on" or message.type == "note_off":

					# get pitch and duration
					midi_bytes = message.bytes()
					temp = Note(midi_bytes[1],midi_bytes[2],float(mid.ticks_per_beat))


					# calculate time
					message_time = message.time
					message_time = regulateTime(message_time,mid.ticks_per_beat)
					current_time += message_time
					


					


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
							print("ERORR HERE")
						curr_note.status = False
						curr_note.note_off_time = current_time
						curr_note.calc_duration()
						note_data = curr_note.get_data()

						data.append(note_data)


	
		

		df = pd.DataFrame(data = data, columns = ["Pitch","Duration","Velocity","Time"])

	return df

def list2DF(sortedList,mode = 'melody'):
	data = []	

	for s in sortedList:
		if mode == 'melody':
			row = [s[1][0],s[1][1],s[1][2],s[0]]
			data.append(row)
		elif mode == 'chord':
			for chords in s[1]:
				row = [chords[0],chords[1],chords[2],s[0]]
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



	chordDict = dict()
	melodyDict = dict()
	pitchDict = rw.load_obj("pitch_dict")
	for k,v in sorted(timeLineDict.items(),key=operator.itemgetter(0)):
		#print(k)
		if len(v) == 1:
			melodyDict[k] = v[0]
			#print("{} ".format(pitchDict.get(v[0][0])))
		elif len(v) >= 2:

			pitchSet = [val[0] for val in v]
			"""
			print("=======")
			for p in pitchSet:
				print("{} ".format(pitchDict.get(p)),end='')
			print("\n=======\n")
			"""
			durationSet = [val[1] for val in v]
			velocitySet = [val[2] for val in v]
			chordDict[k] = v
			melodyDict[k] = [min(pitchSet),min(durationSet),max(velocitySet)]


	sortedMelody = list(sorted(melodyDict.items(),key =operator.itemgetter(0)))
	sortedChord = list(sorted(chordDict.items(),key = operator.itemgetter(0)))


	melodyDF = list2DF(sortedMelody,mode = 'melody')
	chordDF = list2DF(sortedChord,mode = 'chord')


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
		print(a)
		df = analyze_file(a)
		break

	labeledDF = labelingParts(df)

	#plot(labeledDF)

	dfUpper = df[df['Label'] == 0]
	dfLower = df[df['Label'] == 1]

	#print(dfUpper)
	melodyDFU,chordDFU = splitMelodyAndChord(dfUpper)
	melodyDF, chordDF = splitMelodyAndChord(dfLower)

	chordList = []
	time = chordDF.iloc[0,3]


	temp = []
	for idx, row in enumerate(chordDF.iterrows()):
		curr_pitch = row[1][0]
		curr_time = row[1][3]
		if time == curr_time:
			temp.append(curr_pitch)
		elif time!= curr_time:
			chordList.append(temp)
			time = curr_time
			temp = [curr_pitch]

	pitchDict = rw.load_obj("pitch_dict")
	cr = CR.ChordRecognition()
	for c in chordList:
		if cr.isChord(c) is False:
			if cr.checkChords(c) is None:
				for note in c:
					print(note, pitchDict.get(note),end =' ')
			print("\n")


	"""
	upperX = []
	upperY = []
	lowerX = []
	lowerY = []

	for row in melodyDF.iterrows():
		upperY.append(row[1][0])
		upperX.append(row[1][3])

	for row in chordDF.iterrows():
		lowerY.append(row[1][0])
		lowerX.append(row[1][3])



	upperUX = []
	upperUY = []
	lowerUX = []
	lowerUY = []

	for row in melodyDFU.iterrows():
		upperUY.append(row[1][0])
		upperUX.append(row[1][3])

	for row in chordDFU.iterrows():
		lowerUY.append(row[1][0])
		lowerUX.append(row[1][3])

	fig, ax = plt.subplots()

	ax.scatter(upperX, upperY, color='r', marker='^', alpha=.4)
	ax.scatter(lowerX, lowerY, color='b', marker='^', alpha=.4)
	ax.scatter(upperUX, upperUY, color='r', marker='^', alpha=.4)
	ax.scatter(lowerUX, lowerUY, color='b', marker='^', alpha=.4)

	plt.show()
	"""









		


	







