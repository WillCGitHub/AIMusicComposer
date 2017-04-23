from MusicComposer import HMM

import pickle
import os


abs_path = os.path.dirname(os.path.abspath(__file__))
directory = "/obj/"
def save_obj(obj, name):
	if not os.path.exists(directory):
		os.makedirs(directory)
	with open(abs_path+directory+ name + '.pkl', 'wb') as f:
		pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
	with open(abs_path+directory + name + '.pkl', 'rb') as f:
		return pickle.load(f)




if __name__ =='__main__':
	load_obj("happy_dicts")