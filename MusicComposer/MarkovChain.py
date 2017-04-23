from functools import reduce
from collections import Counter
import random


import operator

class MarkovState:
	def __init__(self,data):
		self.data = data    
		self.rate_table = dict()
		

	def __key(self):
		return str(self.data)

	def __len__(self):
		return len(self.rate_table)

	def __hash__(self):
		return hash(self.__key())

	def __str__(self):
		return str(self.data)

	def __repr__(self):
		return str(self.data)

	def __eq__(self,other):
		if self.data == other.data:
			return True
		else:
			return False

	def __add__(self,other):
		if self != other:
			raise "Error: Different Markov State cannot be added together."
		new_MS = MarkovState(self.data)
		new_rate_table = self.update_dict(self.rate_table,other.rate_table)
		new_MS.rate_table = new_rate_table
		return new_MS

	def update_dict(self,dict1, dict2):
		"""
		Merge two dictionaries
		"""
		dict3 = dict()
		for k,v in dict1.items():
			if dict2.get(k) is None:
				dict3[k] = round(v/2,3)
			else:
				dict3[k] = round((dict2.get(k)+v)/2,3)
		for k,v in dict2.items():
			if dict3.get(k) is None:
				dict3[k] = round(v/2,3)

		return dict3









class MarkovChain:
	def __init__(self):
		self.chain = []
		self.htable = dict()
		self.state_chain = dict()

	def __str__(self):
		r = []
		for str_ms, ms in self.state_chain.items():
			r.append(str_ms)
			r.append(":\n")
			for k,v in ms.rate_table.items():
				r.append("\t{} {}%\n".format(k,v))
			r.append("\n")

		return "".join(r)

	def __iter__(self):
		self.idx = 0
		self.iter_list = sorted(self.state_chain.items())
		return self

	def __next__(self):
		self.idx+=1
		if self.idx >= len(self.iter_list):
			raise StopIteration
		return (self.iter_list[self.idx][0],list(self.iter_list[self.idx][1].rate_table.items()))


	def __add__(self,other):
		if not isinstance(other,MarkovChain):
			return "Markov Chain class cannot add to {}".format(type(other))

		new_MC = MarkovChain()

		for str_ms, ms in other.state_chain.items():
			if self.state_chain.get(str_ms) is None:
				new_MC.state_chain[str_ms] = ms
			else:
				curr_ms = self.state_chain.get(str_ms)
				curr_ms += ms
				new_MC.state_chain[str(curr_ms)] = curr_ms

		for str_ms, ms in self.state_chain.items():
			if new_MC.state_chain.get(str_ms) is None:
				new_MC.state_chain[str_ms] = ms

		return new_MC


	def __eq__(self,other):
		if set(self.state_chain) == set(other.state_chain):
			return True
		else:
			return False

		

	def addData_multi_dim(self,new_l,num_of_layer):
		if num_of_layer >= len(new_l):
			raise "number of layer > length of data length"
		self.chain = []
		self.htable = dict()
		key_chain = []
		for idx in range(0,len(new_l)):
			key_chain.append(str(new_l[idx]))


		for ele_idx in range(0,len(key_chain)-num_of_layer):

			key_name = "-".join(key_chain[ele_idx:ele_idx+num_of_layer])
			key = MarkovState(key_name)
			nxt = MarkovState(key_chain[ele_idx+num_of_layer])
			self.addToTable(key,nxt)

		self.calc_rate()

	def addToTable(self,key,nxt):
		if self.htable.get(key) is None:
			self.htable[key] = [nxt]
		else:
			self.htable[key].append(nxt)






	def calc_rate(self):
		for k,v in self.htable.items():

			cnt = Counter(v)

			cnt_values = cnt.values()

			total = reduce(lambda a,b:a+b, cnt_values)

			for key,freq in cnt.items():
				k.rate_table[key] = round(freq/total,3)*100 

			if self.state_chain.get(str(k)) is None:
				self.state_chain[str(k)] = k
			else:
				self.state_chain[str(k)] += k

	def get_next_state(self,curr):


		ms = self.state_chain.get(curr)  # get the MarkovState object

		if ms is None:

			return None

		randInt = random.randint(1,100)

		curr_num = 0
		prev_num = curr_num

		next_table_list = list(sorted(ms.rate_table.items(),key=operator.itemgetter(1)))

		for (k,v) in next_table_list:
			curr_num += v
			if randInt >= prev_num and randInt <= curr_num:
				#print("k: {} , type:{}".format(k,type(k)))
				return k
			prev_num = curr_num

		return k

	def get_state_chain_table(self):
		return self.state_chain


	def get_most_freq_used_chords(self,num_of_chords = 5):
		"""
		num_of_chords: the number of most freqeunt chords need to be returned 
		default chords number is 5
		"""
		max_len = 0
		result = []
		for k,v in self.state_chain.items():
			if len(v) > max_len:
				max_len = len(v)
				#result.append((k,len(v)))
				result.append(k)
				if len(result) > num_of_chords:
					result.pop(0)
		return result


	




if __name__ == "__main__":

	pass


















