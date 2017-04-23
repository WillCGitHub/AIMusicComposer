from MusicComposer import MarkovChain
from MusicComposer import RW_obj as rw
from MusicComposer import MusicNote as mn
from MusicComposer import produceMidi
from MusicComposer import HMM
from MusicComposer.HMM import Model




import os
import random
import sys
from collections import Counter
import operator
import pickle

valid_emotion = ['happy','sad']
class MusicComposer(object):
	def __init__(self,emotion,fileName = None, num_of_states = 3,num_of_notes = 31):
		self.emotion = emotion.lower().strip()
		
		if self.emotion not in valid_emotion:
			#print("Invalid emotion: {}".format(emotion))
			#print("Vlid emotions are: {}".format(valid_emotion))
			self.emotion = "happy"

		if not fileName:
			self.file_name = "{}_output.mid".format(self.emotion)
		else:
			self.file_name = fileName
		self.num_of_notes = num_of_notes
		self.num_of_states = num_of_states

		dict_set = self.load_tables(self.emotion)
		self.matchDict = dict_set.get('matchDict')
		self.markov_p = dict_set.get('markov_p')
		self.markov_CP = dict_set.get('markov_CP')
		self.duration_M = dict_set.get('duration_M')
		self.duration_C = dict_set.get('duration_C')
		self.chordSeq = dict_set.get('chordSeq')
		self.velocity_model = dict_set.get('velocity_model')

	def __repr__(self):
		return "<{} Music Composer Object>".format(self.emotion)

	def load_tables(self,table_name):
		dict_set = rw.load_obj("{}_dicts".format(table_name))
		return dict_set

	def getFreqDict(self):
		"""
		Calculate emission probability
		"""
		freqDict = dict()
		for k,mList in self.matchDict.items():
			freq = Counter(mList)
			total_num = len(mList)

			temp = dict()
			for note, times in freq.items():
				temp[note] = times/total_num
			freqDict[k] = temp

		return freqDict

	def getNoteFromEmissionDict(self,emiss_dict):

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

	def produce(self,directory = "output/"):
		initial_states = self.markov_CP.get_most_freq_used_chords()
		freqDict = self.getFreqDict()
		if self.emotion =='sad':
			pm = produceMidi.produceMidi(bpm=80)
		else:
			pm = produceMidi.produceMidi()
		CP = pm.generate_chord_progression(self.num_of_notes,
				self.num_of_states,
				self.markov_CP, 
				initial_states, 
				mode = 'default')

		melody_raw = []
		melody = []
		generated_chord_sequence = []

		for c in CP:
			chord = str(c.pitch)

			emiss_dict = freqDict.get(chord)
			if emiss_dict is None:
				note = -1
			else:
				note = self.getNoteFromEmissionDict(emiss_dict)
			melody_raw.append(note)

		for c in CP:
			c.duration = 4

	
		pitch_velocity_list = []
		for idx,m in enumerate(melody_raw):
			num_of_notes_to_generate = 15
			if note != -1:
				generated_m = pm.generate_melody(num_of_notes_to_generate,
									self.num_of_states,
									self.markov_p, 
									str(m))
				melody_list = [str(int(mn.pitch)) for mn in generated_m]
				pitch_velocity_list = self.velocity_model.decode(melody_list)
			else:
				generated_m = [-1 for idx in range(num_of_notes_to_generate)]
				melody_list = [str(m)]+[str(int(mn)) for mn in generated_m]


			note_duration=1



			if len(pitch_velocity_list) != 0:
				for m,v in zip(melody_list,pitch_velocity_list):
					melody.append(mn.MusicNote(m,note_duration,int(v)))
			else:
				for m in melody_list:
					melody.append(mn.MusicNote(m,note_duration,0))

		pm.produce_new_track(CP,mode="cp")

		pm.produce_new_track(melody)
		abs_path = os.path.dirname(os.path.abspath(__file__))
		
		
		save_path = os.path.join(directory,self.file_name)
		pm.export_midi(save_path)




if __name__=="__main__":

	composer = MusicComposer('sad')
	composer.produce()





