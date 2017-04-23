from MusicComposer import RW_obj as rw
from functools import reduce
pitch_dict = rw.load_obj("pitch_dict")

class Pitch():
	def __init__(self,pitch):
		self.pitch = int(pitch)  

	def __str__(self):
		string_repr = pitch_dict.get(self.pitch)
		return string_repr

	def __repr__(self):
		return str(self.pitch)

	def __sub__(self,other):
		diff = self.pitch - other.pitch
		return diff

	def __add__(self,other):
		pc = PitchChain()
		pc.pitchChain.append(self)
		pc.pitchChain.append(other)
		return pc


class PitchChain():
	def __init__(self):
		self.pitchChain = []
	def __str__(self):
		s_list = [str(p) for p in self.pitchChain]
		return "-".join(s_list)

	def __add__(self,other):
		if type(self) == type(other):
			self.pitchChain = self.pitchChain + other.pitchChain
		elif isinstance(other,Pitch):
			self.pitchChain.append(other)
		return self




if __name__ == '__main__':
	"""
	p1 = Pitch(70)
	p2 = Pitch(63)
	p3 = Pitch(69)
	l = [p1,p2,p3,p2,p3,p2,p1]
	f = lambda a,b : a+b
	t =reduce (f,l)

	temp = dict()
	temp[t] = 1
	for k,v in temp.items():
		print(k,v)
	"""
	for k,v in pitch_dict.items():
		print(k,v)


