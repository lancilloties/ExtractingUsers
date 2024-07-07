#!/usr/bin/env python3
####################################### GLOBAL CONSTANTS
global USERNAME_LOG

# Logging config
USERNAME_LOG = "users.log"
####################################### CONSTANTS END

####################################### GLOBAL VARIABLES
global memory_users
memory_users = []
####################################### VARIABLES END

# Calculate Entropy
def Entropy(s):
	p, lns = Counter(s), float(len(s))
	return -sum( count/lns * math.log(count/lns, 2) for count in p.values())

# Calculate the Levenshtein distance to find closely related strings.
def LevenshteinDistance(str1, str2, m, n):
	#m = len(str1)
	#n = len(str2)
	d = [[i] for i in range(1, m + 1)]   # d matrix rows
	d.insert(0, list(range(0, n + 1)))   # d matrix columns
	for j in range(1, n + 1):
		for i in range(1, m + 1):
			if str1[i - 1] == str2[j - 1]:   # Python (string) is 0-based
				substitutionCost = 0
			else:
				substitutionCost = 1
			d[i].insert(j, min(d[i - 1][j] + 1,
							   d[i][j - 1] + 1,
							   d[i - 1][j - 1] + substitutionCost))
	return d[-1][-1]

# Checks for character alteration, which are commonly the same user.
def CheckAlteration(first, second):
	lenFirst = len(first)
	lenSecond = len(second)
	
	# TODO: This is extremely slow, so maybe use it as a second pass on the data, that way there's less data to process.
	#levenshteinDst = float(LevenshteinDistance(first, second, lenFirst, lenSecond) / max([lenFirst, lenSecond]))
	#if levenshteinDst >= 50.0:
		#return levenshteinDst
	
	# TODO: Can be optimized!
	# Check if a complete copy of one is in the other.
	if first in second:
		return float((lenFirst*100)/lenSecond)
	elif second in first:
		return float((lenSecond*100)/lenFirst)
	
	index = 0 # Default: Check for partial prefix.
	base = lenSecond
	rotations = lenFirst
	
	if (lenFirst > lenSecond): # Check for partial suffix. ~0.005% of things are suffix vs ~30% prefix.
		index = (lenFirst-lenSecond)-1
		base = lenFirst
		rotations = lenSecond
	
	counter = 0
	for i in range(rotations):
		if first[index+i] == second[i]:
			counter = counter + 1
	
	return float(((counter*100)/base))

# Check if username is part of other usernames
def PartialNick(nick):
	global memory_users
	
	tmpNickList = [] # List of nicks that the current nick is part of and the percentage of similarity.
	
	lowerNick = nick.lower()
	
	for entry in memory_users:
		lowerEntry = entry.lower()
		if entry != nick:
			similarity = CheckAlteration(lowerNick, lowerEntry) # Lower ensures cases don't influence the results, since it should not.
			if similarity > 40.0:
				tmpNickList.append((entry, similarity))
	
	if len(tmpNickList) == 0: # If not part of other usernames
		return None
	else: # If part of other usernames
		return tmpNickList

# Clean usernames before hand
def CleanNick(nick):
	global memory_users
	
	tmp = nick.strip('\n').strip('^').strip('_').strip('-').strip('`').strip('|') # Remove trash characters.
	
	if tmp.find('[') != -1: # Remove "[m]"
		tmp = tmp[0:tmp.find('[')] + tmp[tmp.find(']')+1:len(tmp)]
	
	if tmp.find("Telegram") != -1: # Remove "Telegram"
		tmp = tmp.replace("Telegram","")
	
	# Removes high Entropy names, other trash & duplicates.
	if len(tmp) <= 3 or Entropy(tmp) > 3 or tmp in memory_users:
		return None
	else:
		return tmp

# Load known users from logs
def LoadUsers():
	global memory_users
	global USERNAME_LOG
	
	if path.exists(USERNAME_LOG) is True:
		with open(USERNAME_LOG) as f:
			for line in f:
				tmp = CleanNick(line)
				if tmp != None:
					memory_users.append(tmp)
		return True
	else:
		print("Log not found!")
		return False


def main(args):
	global memory_users
	
	# LoadUsers will clean nicks independently.
	if LoadUsers():
		
		# Here we need to clean the nicks in relation to eachother.
		for user in memory_users:
			user_list = PartialNick(user)
			#if user == "zyga":
				#print(user)
				#print(user_list)
			if user_list is not None:
				if len(user_list) > len(user):
					for entry in user_list:
						if entry[1] > 90.0 or (entry[1] > 40.0 and entry[0].replace(user, '').isalpha() == False):
							memory_users.remove(entry[0])
				else:
					for entry in user_list:
						if entry[1] > 85.0 or (entry[1] > 60.0 and entry[0].replace(user, '').isalpha() is False):
							memory_users.remove(entry[0])
						
		
		# Once all cleaned, we print.
		for user in memory_users:
			print(user)
	else:
		return 1 # Error in loading
	
	return 0

if __name__ == '__main__':
	import math
	from collections import Counter
	import sys
	from os import path
	sys.exit(main(sys.argv))
