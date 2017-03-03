import midiparser as midiP
import MarkovChain as mc
import RW_obj as rw
import MusicNote as mn
import produceMidi 
import extract_feature as ef
import ChordRecognition as CR

import HMMHelper as hh
import HMM

import os
import random
import sys



if __name__=="__main__":
	abs_path = "MIDI/test"
	MIDI_list = ef.listdir_nohidden(abs_path)
	list_len = 0
	for mid in MIDI_list:
		list_len+=1
	MIDI_list = ef.listdir_nohidden(abs_path)
	total_result = []
	totalP = []
	totalD = []
	totalChordSeq =[]

	for idx, a in enumerate(MIDI_list):
		try:

			df = midiP.analyze_file(a)


			labeledDF = midiP.labelingParts(df)



			dfUpper = df[df['Label'] == 0]
			dfLower = df[df['Label'] == 1]

			chordSequence = ef.getChordSequence(dfLower)
			totalChordSeq+=chordSequence



			duration = list(dfUpper['Duration'])
			tempD = [str(d) for d in duration]
			totalD+=tempD

			break
		except:
			pass
		print("{0:.1f}% \r".format(float(idx/(list_len-1))*100),end='')

		sys.stdout.flush()






	hh_pitch = hh.HMMHelper(totalP,totalD)

	pitchUniqueState = hh_pitch.findUniqueStates(totalP)
	durationUniqueState = hh_pitch.findUniqueStates(totalD,t="origin")
	trans_prob = hh_pitch.calculateTransitionMatrix()
	emit_prob = hh_pitch.calculateEmissionMatrix()
	hh_pitch.calculateInitialDistribution()
	start_prob = hh_pitch.initialDistributionDict
	print("HMM Modeling...")
	model = HMM.Model(durationUniqueState, pitchUniqueState, start_prob, trans_prob, emit_prob)



	"""
	STATES_NUM = 5

	MIDI_path = "MIDI/test"



	num_of_states = STATES_NUM

	markov_p = ef.extract(MIDI_path,num_of_states,"test")
	pm = produceMidi.produceMidi()
	
	
	durationList = []

	iteration = 0
	while len(durationList) == 0:
		melody = pm.generate_melody(60,num_of_states,markov_p,init = 'bounded')
		sequence = []
		
		for m in melody:
			sequence.append(str(m.pitch))
		e = model.evaluate(sequence)
		durationList = model.decode(sequence)
		if iteration > 10000:
			print("iteration reaches 10000")
			sys.exit()
		iteration+=1
	print(sequence)
	print(durationList)

	melody = pm.addDurations(melody,durationList)
	pm.produce_new_track(melody)
	pm.export_midi("test")
	"""




