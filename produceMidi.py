import os
import random
import operator

from RW_obj import *
from mido import Message, MidiFile, MidiTrack, bpm2tempo, MetaMessage
import MusicNote as mn


"""
basic_rhythm = ["0.25-->0.25-->0.25-->0.25",
				"0.125-->0.125-->0.125-->0.125-->0.25-->0.25",
				"1.0",
				"0.5-->0.5",
				"1.5-->0.5",
				"0.25-->0.25-->0.5",
				"0.25-->0.25-->0.25-->0.25-->1.0",
				"0.334-->0.333-->0.332"]
"""
basic_rhythm = ["0.25-->0.25-->0.25-->0.25",
				"1.0",
				"0.5-->0.5",
				"1.5-->0.5",
				"0.25-->0.25-->0.5",
				"0.25-->0.25-->0.25-->0.25-->1.0"]

basic_rhythm_ending = ["0.25-->0.25-->0.25-->0.25",
					"1.0",
					"0.5-->0.5",
					"0.25-->0.25-->0.5"]





class produceMidi():
	def __init__(self,bpm = 60):
		self.mid = MidiFile()
		self.tempo = bpm2tempo(bpm)


	"""
	num_of_notes --> how mnay notes of the current gneration
	markov_d --> duration markov chain
	num_of_states --> the number of states that the model will use to generate the melody
	markov_p --> pitch markov chain 
	markov_v --> velocity markov chain
	p_init__diff_state --> initial pitch difference. Default == 2
	v_init_state --> initial velocity. Default == 100
	v_init_diff_state --> initial velocity difference. Default == 3
	"""
	def generate_melody(self,num_of_notes,num_of_states,markov_p,init = 'default'):

		lower_init_pitch_bound = 60
		upper_init_pitch_bound = 84
		if init == 'default':
			p_init_state = 60

		elif init == 'random':
			p_init_state = random.randint(lower_init_pitch_bound,upper_init_pitch_bound)

		elif init == 'bounded':
			p_init_state = random.choice([60,62,64,65,67,69])

		else:
			p_init_state = 60



		# initialize the first note
		init_mn = mn.MusicNote(p_init_state,1,100)

		# initialize the melody list
		melody = []
		melody.append(init_mn)

		curr_p = str(p_init_state)


		generated_list_p = [curr_p]


		for idx in range(0,num_of_notes):
			randInt = random.randint(1,100)


			nxt_p = self.get_next_by_multi_state(generated_list_p,markov_p,num_of_states)

			if nxt_p is None:
				nxt_p = generated_list_p[-1]


			generated_list_p.append(nxt_p)


			curr_mn = mn.MusicNote(curr_p,1,100)
			melody.append(curr_mn)


			curr_p = str(nxt_p)



		return melody


	def get_next_by_multi_state(self,generated_list,markov_chain,num_of_states):
		


		if num_of_states <= 0:
			print("get_next_by_multi_state() --> num_of_states = 0\nGenerated list:{}".format(generated_list))
			return None
		if len(generated_list) < num_of_states:
			num_of_states = len(generated_list)



		key_chain = [str(x) for x in generated_list]
		#print("key chain: {}  num of state: {}, idx:{}".format(key_chain,num_of_states,idx))

		if num_of_states == 0:
			key = key_chain[-1]
		else:
			key = "-".join(key_chain[-num_of_states:])
		if key == "":
			print("key chain: {}  num of state: {}".format(key_chain,num_of_states))
		#print("key: ({})".format(key))

		nxt = markov_chain.get_next_state(key)
		if nxt is None:
			return self.get_next_by_multi_state(generated_list,markov_chain,num_of_states-1)
		else:
			return nxt


	def addDurations(self,melody,duration):
		if len(melody) != len(duration):
			print("duration list length does not match melody list length")
			sys.exit()

		for m,d in zip(melody,duration):
			m.duration = float(d)

		return melody
	"""
	Not used
	def generate_duration(self,time_signiture = 4,num_of_bars = 12):
		rhythm_list = []
		total_length = num_of_bars*time_signiture
		while(total_length > 0):
			if total_length == 1:
				randInt = random.randint(0,len(basic_rhythm_ending)-1)
				rhythm = basic_rhythm_ending[randInt]
			else:
				randInt = random.randint(0,len(basic_rhythm)-1)
				rhythm = basic_rhythm[randInt]
			
			temp_total = 0
			for t in rhythm.split("-->"):
				rhythm_list.append(t)
				temp_total+=float(t)


			total_length -= temp_total

		return rhythm_list
	"""

	def produce_new_track(self,melody):
		self.track = MidiTrack()
		self.mid.tracks.append(self.track)
		self.track.append(MetaMessage("set_tempo",tempo = self.tempo,time=0))
		self.track.append(Message('program_change', program=1, time=0))
		curr_time = 0
		for mn in melody:
			self.append_note(mn)


	def append_note(self,music_note):
		self.track.append(Message('note_on',note=int(music_note.pitch),velocity = music_note.velocity,time =0))

		self.track.append(Message('note_off',note=int(music_note.pitch),velocity = music_note.velocity,time = music_note.beat2tick(ticks_per_beat = 480)))


		#self.track.append(Message('note_off',note=int(music_note.pitch),velocity = int(music_note.velocity),time = 96))

	def export_midi(self,f):
		file_name = "".join([f,'.mid'])
		folder = "SampleMIDI"
		save_path = os.path.join(folder,file_name)
		self.mid.save(save_path)



if __name__=='__main__':
	pm = produceMidi()
	l = [5]
	print(l[-1:])
	#pm.export_midi("test")


