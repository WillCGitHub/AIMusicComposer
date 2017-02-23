import midiparser as midiP
import MarkovChain as mc
import RW_obj as rw
import MusicNote as mn
import produceMidi 
import extract_feature as ef

import os
import random
import sys


STATES_NUM = 5

MIDI_path = "MIDI/liszt"

name_var = "liszt"

num_of_states = STATES_NUM

markov_p = ef.extract(MIDI_path,num_of_states,name_var)




#markov_p = load_tables("all",num_of_states)


pm = produceMidi.produceMidi()
rhythm_list = pm.generate_duration()




for track_idx in range(0,3):
	melody = pm.generate_melody(rhythm_list,num_of_states,markov_p,p_init = 'bounded')	




	pm.produce_new_track(melody)




pm.export_midi("{}_state_{}_1".format(name_var,num_of_states))



