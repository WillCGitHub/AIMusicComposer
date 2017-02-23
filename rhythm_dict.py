from RW_obj import *
import midiparser as midiP
import extract_feature as ef


import operator
import sys
import random

basic_rhythm = ["0.25-->0.25-->0.25-->0.25",
				"0.125-->0.125-->0.125-->0.125-->0.25-->0.25",
				"1.0",
				"0.5-->0.5",
				"1.5-->0.5",
				"0.25-->0.25-->0.5",
				"0.25-->0.25-->0.25-->0.25-->1.0",
				"0.334-->0.333-->0.332"]
