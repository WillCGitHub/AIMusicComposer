import RW_obj as rw

pitch_dict = rw.load_obj("pitch_dict")
class MusicNote:
	def __init__(self,pitch,duration,velocity):
		self.pitch = pitch
		self.duration = duration

		self.velocity = velocity

	def __str__(self):
		try:
			r = "-".join([pitch_dict.get(int(self.pitch)),str(self.duration),str(self.velocity)])
		except:
			r = "-".join([str(self.pitch),str(self.duration),str(self.velocity)])
		return r

	def __repr__(self):
		return (self.__str__())

	def beat2tick(self,ticks_per_beat = 480):
		d = float(self.duration) # in beat
		return round(d*ticks_per_beat)



