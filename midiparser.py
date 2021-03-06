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



def analyze_file(midi_path,mode="default",count= 1):

	mid = mido.MidiFile(midi_path)

	data = []
	pitchDict = rw.load_obj("pitch_dict")
	for i, track in enumerate(mid.tracks):
		current_time = 0
		current_beats = 0
		note_dict = dict()
		prev_note = None
		temp_time = 0
		
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

					


					

					if mode =="default":
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
					elif mode =="no_off":
						if prev_note is None :
							prev_note = temp
							continue
						if message_time != 0:
							temp_time = message_time

						prev_note.note_on_time = current_time-temp_time
						prev_note.note_off_time = current_time
						prev_note.calc_duration()
						data.append(prev_note.get_data())
						prev_note = temp
							



	
		

		df = pd.DataFrame(data = data, columns = ["Pitch","Duration","Velocity","Time"])


		if len(df) == 0 and count == 1:
			count-=1
			return analyze_file(midi_path,mode="no_off",count = count)



	return df


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

	abs_path = "MIDI/pop"
	MIDI_list = ef.listdir_nohidden(abs_path)
	total_result = []
	matchDict = None
	for a in MIDI_list:
		print(a)

		df = analyze_file(a)
		print(df)




	



	













		


	







