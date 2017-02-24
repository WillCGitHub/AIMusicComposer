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
	abs_path = "MIDI/Mozart"
	MIDI_list = ef.listdir_nohidden(abs_path)
	total_result = []
	totalP = []
	totalD = []
	for a in MIDI_list:
		try:
			df = midiP.analyze_file(a)


			labeledDF = midiP.labelingParts(df)



			dfUpper = df[df['Label'] == 0]
			dfLower = df[df['Label'] == 1]


			pitch = list(dfUpper['Pitch'])
			tempP = [str(int(p)) for p in pitch]
			totalP+=tempP

			duration = list(dfUpper['Duration'])
			tempD = [str(d) for d in duration]
			totalD+=tempD
		except:
			pass






	hh = hh.HMMHelper(totalP,totalD)

	pitchUniqueState = hh.findUniqueStates(pitch)
	durationUniqueState = hh.findUniqueStates(duration,t="origin")
	trans_prob = hh.calculateTransitionMatrix()
	emit_prob = hh.calculateEmissionMatrix()
	hh.calculateInitialDistribution()
	start_prob = hh.initialDistributionDict
	model = HMM.Model(durationUniqueState, pitchUniqueState, start_prob, trans_prob, emit_prob)


	STATES_NUM = 5

	MIDI_path = "MIDI/Mozart"



	num_of_states = STATES_NUM

	markov_p = ef.extract(MIDI_path,num_of_states,"Mozart")
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





