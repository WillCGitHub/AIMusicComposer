from RW_obj import *

pitch = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
pitch_dict = dict()
for idx, note in enumerate(pitch):
	if pitch_dict.get(note) is None:
		l = []
		curr = idx
		while(curr < 128):
			l.append(curr)
			curr+=12 
		for num in l:
			pitch_dict[num] = note

save_obj(pitch_dict,"pitch_dict")