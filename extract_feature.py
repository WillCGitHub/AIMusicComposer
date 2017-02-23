import midiparser as midiP
import MarkovChain as mc
import RW_obj as rw
import MusicNote as mn
import produceMidi 

import os
import random
import sys





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
	
		
	markov_p = mc.MarkovChain()
	markov_d = mc.MarkovChain()

	for midi_file in midi_path_list:
		
		try:
			df = midiP.analyze_file(midi_file)

			labeledDF = midiP.labelingParts(df)


			dfUpper = df[df['Label'] == 0]
			dfLower = df[df['Label'] == 1]


			melodyDF, chordDF = midiP.splitMelodyAndChord(dfUpper)
				

			for num_of_state in range(1,num_of_states+1):


				ptemp = melodyDF.loc[:,'Pitch']
				dtemp = melodyDF.loc[:,'Duration']
				markov_p.addData_multi_dim(ptemp,num_of_state)



		except:
			pass
		outer_idx+=1
		
		print("{0:.1f}% \r".format(float(outer_idx/(list_len))*100),end='')

		sys.stdout.flush()




	print("training done")

	save_tables(table_name,num_of_states,markov_p)

	return markov_p



if __name__ == '__main__':
	STATES_NUM = 5

	MIDI_path = "MIDI/chopin"
	#MIDI_path = "MIDI/bach"


	num_of_states = STATES_NUM

	markov_p = extract(MIDI_path,num_of_states,"chopin")




	print(markov_p)

	"""


	#markov_p = load_tables("all",num_of_states)


	pm = produceMidi.produceMidi()
	#rhythm_list = pm.generate_duration()



	num_of_notes = 60

	for track_idx in range(0,3):

		melody = pm.generate_melody(num_of_notes,num_of_states,markov_p,markov_d,init = 'bounded')	

		pm.produce_new_track(melody)


	pm.export_midi("mozartCtest{}".format(num_of_states))


	"""