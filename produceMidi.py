import os
import random
import operator

from RW_obj import *
from mido import Message, MidiFile, MidiTrack, bpm2tempo, MetaMessage
import MusicNote as mn
import RW_obj as rw






class produceMidi():
	def __init__(self,bpm = 100):
		self.mid = MidiFile()
		self.tempo = bpm2tempo(bpm)

	"""
	initial_states: most frequent used chords
		default mode: get the most frequent used chord
		random mode: get a random chord from the list 
	"""
	def generate_melody(self,num_of_notes,num_of_states,markov_p, initial_p, mode = 'default'):

		if mode == 'default':
			init_p = initial_p


		# initialize the first note
		init_mn = mn.MusicNote(int(init_p),0.25,100)

		# initialize the melody list
		melody = []
		melody.append(init_mn)

		curr_p = init_p


		generated_list_p = [curr_p]


		for idx in range(0,num_of_notes-1):
			randInt = random.randint(1,100)


			nxt_p = self.get_next_by_multi_state(generated_list_p,markov_p,num_of_states)

			if nxt_p is None:
				nxt_p = generated_list_p[-1]


			generated_list_p.append(nxt_p)


			curr_mn = mn.MusicNote(int(curr_p),0.25,100)
			melody.append(curr_mn)


			curr_p = str(nxt_p)


		return melody



	"""
	initial_states: most frequent used chords
		default mode: get the most frequent used chord
		random mode: get a random chord from the list 
	"""
	def generate_chord_progression(self,num_of_notes,num_of_states,markov_CP, initial_states, mode = 'default'):

		if mode == 'default':
			init_chord = initial_states[-1]
		elif mode == 'random':
			init_chord = random.choice(initial_states)




		# initialize the first note
		init_mn = mn.MusicNote(init_chord,1,100)

		# initialize the CP list
		chord_progression = []
		chord_progression.append(init_mn)

		curr_c = init_chord


		generated_list_c = [curr_c]


		for idx in range(0,num_of_notes):
			randInt = random.randint(1,100)


			nxt_c = self.get_next_by_multi_state(generated_list_c,markov_CP,num_of_states)

			if nxt_c is None:
				nxt_c = generated_list_c[-1]


			generated_list_c.append(nxt_c)


			curr_mn = mn.MusicNote(curr_c,1,100)
			chord_progression.append(curr_mn)


			curr_c = nxt_c


		return chord_progression


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


	def produce_new_track(self,melody,mode="melody"):
		self.track = MidiTrack()
		self.mid.tracks.append(self.track)
		self.track.append(MetaMessage("set_tempo",tempo = self.tempo,time=0))
		self.track.append(Message('program_change', program=1, time=0))
		for mn in melody:
			self.append_note(mn,mode=mode)





	def append_note(self,music_note,mode):
		if mode == "melody":
			self.track.append(Message('note_on',note=int(music_note.pitch),velocity = music_note.velocity,time =0))
			self.track.append(Message('note_off',
								note=int(music_note.pitch),
								velocity = music_note.velocity,
								time = music_note.beat2tick(ticks_per_beat = 480)))
		elif mode == "cp":
			chordName = music_note.pitch
			nameChordDict = rw.load_obj('nameToChordDict')
			note_tuples = nameChordDict.get(str(chordName))
			if len(note_tuples) == 2 and note_tuples[0] == note_tuples[1]:

				temp_n = note_tuples[1]
				temp_n+=12
				new_tuple = (note_tuples[0],temp_n)
				note_tuples = new_tuple

			for note in note_tuples:

				note+=48 # move displacement
				self.track.append(Message('note_on',note=int(note),velocity = music_note.velocity,time =0))
			for idx,note in enumerate(note_tuples):	

				note+=48 # move displacement
				if idx == 0:
					self.track.append(Message('note_off',
										note=int(note),
										velocity = music_note.velocity,
										time =music_note.beat2tick(480)))
				else:
					self.track.append(Message('note_off',
										note=int(note),
										velocity = music_note.velocity,
										time = 0))



		

	def export_midi(self,f):
		file_name = "".join([f,'.mid'])
		folder = "SampleMIDI"
		save_path = os.path.join(folder,file_name)
		self.mid.save(save_path)



if __name__=='__main__':
	pm = produceMidi()



