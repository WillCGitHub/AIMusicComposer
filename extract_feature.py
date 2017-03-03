import midiparser as midiP
import MarkovChain as mc
import RW_obj as rw
import MusicNote as mn
import produceMidi 
import ChordRecognition as CR
import HMMHelper as hh
import HMM

import os
import random
import sys
from collections import Counter
import operator





def listdir_nohidden(path):
	for (dirpath, dirnames, filenames) in os.walk(path):
		for f in filenames:
			if f.endswith(".mid"):
				file_path = os.path.join(dirpath,f)
				yield file_path

def save_tables(talbe_name, num_of_states,p_table_list):
	rw.save_obj(p_table_list,"{}_pitch_table_list_{}".format(talbe_name,num_of_states))


def load_tables(table_name,num_of_states):
	p_table_list = rw.load_obj("{}_pitch_table_list_{}".format(table_name,num_of_states))

	return p_table_list


def getChordSequence(chordDF):
	chordList = []
	time = chordDF.iloc[0,3]
	temp = []
	for idx, row in enumerate(chordDF.iterrows()):
		curr_pitch = row[1][0]
		curr_time = row[1][3]
		curr_duration = row[1][1]
		if time == curr_time:
			temp.append(curr_pitch)
		elif time!= curr_time:
			chordList.append((temp,time,curr_duration))
			time = curr_time
			temp = [curr_pitch]

	pitchDict = rw.load_obj("pitch_dict")
	cr = CR.ChordRecognition()
	chord_sequence = []
	chordOnly_sequence = []


	for c in chordList:
		status,chord_name_list = cr.isChord(c[0])
		if status is False:
			chord_name_list = cr.checkChords(c[0])
			if chord_name_list is None:
				for note in c:
					pritn("==========")
					print(note, pitchDict.get(note),end =' ')
					pritn("==========")
		for chord in chord_name_list:
			chord_sequence.append((chord,c[1],c[2]*480+c[1])) # (chord,start time, end time)
			chordOnly_sequence.append(chord)

	return chord_sequence, chordOnly_sequence

def match(dfUpper,dfLower, matchDict = None):
	"""
	match melodies and chords
	"""
	melodyList = []
	for row in dfUpper.iterrows():
		melodyList.append(row[1])
	
	chordSequence,chordOnly_sequence = getChordSequence(dfLower)



	if matchDict is None:
		matchDict = dict()
	for idx in range(0,len(chordSequence)):
		for inner_idx in range(len(melodyList)):

			pitch = int(melodyList[inner_idx][0])
			time = melodyList[inner_idx][3]
			if time < chordSequence[idx][1]:
				pass
			elif time >= chordSequence[idx][1] and time < chordSequence[idx][2]:
				#within range
				if matchDict.get(chordSequence[idx][0]) is None:
					matchDict[chordSequence[idx][0]] = [pitch]
				else:
					matchDict[chordSequence[idx][0]].append(pitch)
			else:
				break
		#get rid off used melodies
		melodyList = melodyList[inner_idx:]

	return matchDict

def getFreqDict(matchDict):
	"""
	Calculate emission probability
	"""
	freqDict = dict()
	for k,mList in matchDict.items():

		freq = Counter(mList)
		total_num = len(mList)

		temp = dict()
		for note, times in freq.items():
			temp[note] = times/total_num
		freqDict[k] = temp

	return freqDict

def printFreqDict(freqDict):
	for k,v in freqDict.items():
		print(k,end=" | ")
		for note,freq in v.items():
			print(note,freq, end=", ")
		print("\n")

def getNoteFromEmissionDict(emiss_dict):

	randInt = random.randint(1,100)

	curr_num = 0
	prev_num = curr_num

	next_table_list = list(sorted(emiss_dict.items(),key=operator.itemgetter(1)))

	for (k,v) in next_table_list:
		v *= 100 
		curr_num += v
		if randInt >= prev_num and randInt <= curr_num:
			#print("k: {} , type:{}".format(k,type(k)))
			return k
		prev_num = curr_num

	return k

def extract(MIDI_path,num_of_states,table_name):

	MIDI_list = listdir_nohidden(MIDI_path)
	list_len = 0
	midi_path_list = []
	for mid in MIDI_list:
		midi_path_list.append(mid)
		list_len+=1


	print("Lenght of training list: {}".format(list_len))


	print("number of states = {}".format(num_of_states))
	print("training...")
	outer_idx = 0
	
		
	markov_CP = mc.MarkovChain() # chord progression
	markov_p = mc.MarkovChain() # pitch mc
	matchDict = None 
	totalD_M = [] # melody durations
	totalD_C = [] # chord durations
	complete_chord_sequence = []
	for midi_file in midi_path_list:
		
		try:
			df = midiP.analyze_file(midi_file)
			df = midiP.labelingParts(df)
			dfUpper = df[df['Label'] == 0]
			dfLower = df[df['Label'] == 1]
			matchDict = match(dfUpper,dfLower,matchDict)
			chordSequence,chordOnly_sequence = getChordSequence(dfLower)
			complete_chord_sequence += chordOnly_sequence

			duration_M = list(dfUpper['Duration'])
			duration_C = list(dfLower['Duration'])
			tempD_M = [str(d) for d in duration_M]
			tempD_C = [str(d) for d in duration_C]
			totalD_M+=tempD_M
			totalD_C+=tempD_C

			for num_of_state in range(1,num_of_states+1):
				ptemp = [int(p) for p in list(dfUpper.loc[:,'Pitch'])]
				markov_p.addData_multi_dim(ptemp,num_of_state)
				markov_CP.addData_multi_dim(chordOnly_sequence,num_of_state)


		except:
			pass
		



		outer_idx+=1
		
		print("{0:.1f}% \r".format(float(outer_idx/(list_len))*100),end='')

		sys.stdout.flush()




	print("training done")

	#save_tables(table_name,num_of_states,markov_p)

	return matchDict, markov_p,markov_CP,totalD_M,totalD_C,complete_chord_sequence



if __name__ == '__main__':
	STATES_NUM = 5

	MIDI_path = "MIDI/test"
	#MIDI_path = "MIDI/bach"


	num_of_states = STATES_NUM

	matchDict,markov_p, markov_CP, duration_M,duration_C, chordSeq = extract(MIDI_path,num_of_states,"test")

	initial_states = markov_CP.get_most_freq_used_chords()
	freqDict = getFreqDict(matchDict)

	#markov_p = load_tables("all",num_of_states)

	pm = produceMidi.produceMidi()
	num_of_notes = 100

	CP = pm.generate_chord_progression(num_of_notes,num_of_states,markov_CP, initial_states, mode = 'default')

	hh_chord = hh.HMMHelper(chordSeq,duration_C)

	chordUniqueState = hh_chord.findUniqueStates(chordSeq,t="origin")
	durationUniqueState = hh_chord.findUniqueStates(duration_C,t="origin")
	trans_prob = hh_chord.calculateTransitionMatrix()
	emit_prob = hh_chord.calculateEmissionMatrix()
	hh_chord.calculateInitialDistribution()
	start_prob = hh_chord.initialDistributionDict
	print("HMM Modeling...")
	model = HMM.Model(durationUniqueState, chordUniqueState, start_prob, trans_prob, emit_prob)











	melody_raw = []
	melody = []
	generated_chord_sequence = []
	for c in CP:
		chord = str(c.pitch)
		emiss_dict = freqDict.get(chord)
		if emiss_dict is None:
			note = 0
		else:
			note = getNoteFromEmissionDict(emiss_dict)
		melody_raw.append(note)
		generated_chord_sequence.append(chord)

	chord_duration_list = model.decode(generated_chord_sequence)

	for c, d in zip(CP,chord_duration_list):
		c.duration = float(d)

	for idx,m in enumerate(melody_raw):
		duration = CP[idx].duration
		num_of_notes = 1
		#generated_m = pm.generate_melody(num_of_notes,num_of_states,markov_p, str(m))
		note_duration = duration/num_of_notes

		#for new_m in generated_m:
			#new_m.duration = note_duration
		melody.append(mn.MusicNote(m,note_duration,100))
		#melody+=generated_m

	for m in melody:
		print(m.pitch,m.duration)

	pm.produce_new_track(CP,mode="cp")

	pm.produce_new_track(melody)

	pm.export_midi("test-{}".format(num_of_states))


