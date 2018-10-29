# This Python file uses the following encoding: utf-8
#import sys #This is not necessary anymore (but I'll keep it as a reminder that I might reintroduce it for batch-processing)
import re
import os

f_liaison_verbs_3rd = open('list_liaison_verbs_3rd_to_check.txt', 'w')
root='corpora'
dirlist = [ item for item in os.listdir(root) if os.path.isdir(os.path.join(root, item)) ]

# Apply schwa insertion?
do_schwa_insertion = False #Set to True or False

if not os.path.exists('output'):
	os.makedirs('output')

#### DICTIONARY ####
# Special symbols to be added to dictionary:
dico = {}
dico[","]=","
dico["?"]="?"
dico["!"]="!"
dico["."]="."
dico[";"]=";"
dico[":"]=":"

dico["\*"]="#"  
dico["l'"]="l'" 
dico["d'"]="d'" 
dico["m'"]="m'" 
dico["n'"]="n'" 
dico["c'"]="s'" 
dico["t'"]="t'" 
dico["s'"]="s'" 
dico["j'"]="Z'"

# Load the Lexique dictionary (simplified, only 2 columns, one for orthographic form, one with syllabified phonological form):
with open('auxiliary/french.dic') as dic:
	for line in dic:
		line = line.decode('cp1252').encode('utf-8')
		aux = line.split()
		if len(aux) == 2:
			dico[aux[0]] = aux[1]


#### PHONEMES ####
# Symbols used as in Lexique: http://www.lexique.org/outils/Manuel_Lexique.htm#_Toc108519023

## Vowels:
# vowels = ['a','i','e','E','o','O','u','y','§','1','5','2','9','@','°','3']
vowels = ['a','i','e','E','o','O','u','y','4','1','5','2','9','@','6','3']
semivowels = ['j', '8', 'w']
# Note: There is a problem with the encoding of the special characters § and °.
# For the moment (01/08/17) I have failed to fix it, I have tried different
# ways of encoding the text but my code still fails to find it in the list.
# The workaround I found is to replace these special characters with simple
# characters only for the parts of script that require comparing vowels.

## Consonants:
unvoiced_obstruents = ['p','t','k','f','s','S']
voiced_obstruents = ['b','d','g','v','z','Z']
obstruents = unvoiced_obstruents + voiced_obstruents
liquids    = ['l', 'R']
nasals     = ['m', 'n', 'N']
consonants = obstruents + liquids + nasals

## Other characters:
punctuation = [',', '?', '!', '.', ';', ':']

## Liaison consonants:
# Keys:   orthographic form
# Values: phonological form if liaison applies
liaison = {}
liaison['s'] = 'z'
liaison['z'] = 'z'
liaison['t'] = 't'
liaison['p'] = 'p'
liaison['n'] = 'n'
liaison['d'] = 't'
liaison['f'] = 'v'
liaison['x'] = 'z'
liaison['r'] = 'R'

## Expected pronunciation of relevant consonants:
# This serves to check if the consonants are silent or not
pronunciation = {}
pronunciation['s'] = ['s', 'z']
pronunciation['z'] = 'z'
pronunciation['t'] = 't'
pronunciation['p'] = 'p'
pronunciation['n'] = 'n'
pronunciation['d'] = 'd'
pronunciation['f'] = 'f'
pronunciation['x'] = ['s', 'z']
pronunciation['r'] = 'R'


#### WORD LISTS ####
# These lists contain all words in certain grammatical
# categories, necessary for checking certain liaison
# contexts. They were obtained from Lexique380.

# Load the adjectives:
V_adjectives = [] # All vowel-initial adjectives, for plural noun + adjective rule
adjectives   = [] # Only adjectives finishing in a liaison consonant, to add to mandatory list
with open('auxiliary/output_ADJ.txt') as ADJlist:
	for line in ADJlist:
		line = line.strip().decode('cp1252').encode('utf-8')
		if (line in dico):
			ortho_word = dico[line]
			first_phon = ortho_word.replace('§', '4').replace('°', '6')[0] # Replacing special characters (see note in PHONEMES section)
			if (first_phon in vowels+semivowels): 
				V_adjectives.append(line) 
			if (line[-1] in liaison) and (dico[line][-1] != liaison[line[-1]]): 
				adjectives.append(line)

# Load the plural nouns:
plural_nouns = [] # Nouns finishing in liaison consonant
V_nouns = [] # Vowel-initial nouns
C_nouns = [] # Consonant-initial nouns
with open('auxiliary/output_NOMp.txt') as NOMlist:
	for line in NOMlist:
		line = line.strip().decode('cp1252').encode('utf-8')
		if (line in dico):
			ortho_word = dico[line]
			first_phon = ortho_word.replace('§', '4').replace('°', '6')[0] # Replacing special characters (see note in PHONEMES section)
			if (first_phon in vowels+semivowels): 
				V_nouns.append(line) 
			if (first_phon in consonants):
				C_nouns.append(line)
			if (line[-1] in liaison) and (line != 'trucs'):
				plural_nouns.append(line)

			
# Load 3rd person verbs:
verbs_3s = []
with open('auxiliary/output_VER3s.txt') as VER3slist:
	for line in VER3slist:
		line = line.strip().decode('cp1252').encode('utf-8')
		if (line not in ['soit', 'dit']):	 #if (line[-1] in liaison) and (line not in ['soit', 'dit']):
			verbs_3s.append(line)

verbs_3p = []
with open('auxiliary/output_VER3p.txt') as VER3plist:
	for line in VER3plist:
		line = line.strip().decode('cp1252').encode('utf-8')
		verbs_3p.append(line)
			
#### LIAISON EXCEPTIONS LIST ####
# These are words that will never trigger liaison:

# (1) Words beginning with h-aspiré (list retrieved from wikipedia article: https://fr.wikipedia.org/wiki/H_aspiré)
h_aspire = []
with open('auxiliary/h_aspire.txt') as Hlist:
	for line in Hlist:
		line = line.strip()
		h_aspire.append(line)
		
# (2) Other words (interjections and others)
interjections = ['oh', 'eh', 'éh', 'ah', 'hum', 'euh', 'heuh', 'ouah', 'ouf']
loanwords_with_initial_semivowels = ['whisky', 'yack', 'yaourt', 'yéti']
names_of_letters = ['u', 'i', 'm'] # Note: these are just the ones we found in the text.
proper_names =  #names?
other_exceptions = ['et', 'ou', 'où', 'oui', 'ouais', 'apparemment', 'alors', 'attends', 'aussi', 'encore', 'avec', 'après']


exceptions_next = h_aspire + interjections + loanwords_with_initial_semivowels + other_exceptions


#### LIAISON CASES ####

# (1) Cases that apply always except if followed by specific exception words
# Keys: Words that are considered to undergo mandatory liaison
# Values: Exceptions of following words that would not trigger liaison
# Note: some exceptions were added specifically to certain target words because we happened to find them in the text.
always_except = {}
# Possessive pronouns:
always_except['mon'] = exceptions_next
always_except['ton'] = exceptions_next
always_except['son'] = exceptions_next
always_except['mes'] = exceptions_next
always_except['tes'] = exceptions_next
always_except['ses'] = exceptions_next
always_except['nos'] = exceptions_next
always_except['vos'] = exceptions_next
always_except['leurs'] = exceptions_next
# Personal pronouns:
always_except['on']    = exceptions_next
always_except['nous']  = exceptions_next + ['à', 'on'] + ['il', 'ils', 'elle', 'elles']
always_except['vous']  = exceptions_next + ['il', 'ils', 'elle', 'elles']
always_except['ils']   = exceptions_next
always_except['elles'] = exceptions_next
# Articles:
always_except['un']  = exceptions_next + ['à']
always_except['les'] = exceptions_next
always_except['des'] = exceptions_next
# Determiners:
always_except['ces']     = exceptions_next
always_except['quels']   = exceptions_next + ['il', 'ils', 'elle', 'elles']
always_except['quelles'] = exceptions_next + ['il', 'ils', 'elle', 'elles']
# Indefinite adjectives:
always_except["quelqu'un"] = exceptions_next + ['y', 'est', 'a']
always_except['quelques']  = exceptions_next + ['il', 'ils', 'elle', 'elles']
always_except['plusieurs'] = exceptions_next
always_except['certains']  = exceptions_next
always_except['certaines'] = exceptions_next
always_except['autres']    = exceptions_next + ['à', 'au']
always_except['aucun']     = exceptions_next
# Monosyllabic adverbs:
always_except['tout'] = exceptions_next + ['il', 'ils', 'elle', 'elles', 'on']
always_except['plus'] = exceptions_next
always_except['très'] = exceptions_next
# Prepositions:
always_except['aux']  = exceptions_next
always_except['en']   = exceptions_next + ['un', 'une']
always_except['sans'] = exceptions_next
always_except['sous'] = exceptions_next

# (2) Adjectives:
for adjective in adjectives:
	always_except[adjective] = exceptions_next + ['il', 'elle', 'on', 'un', 'une', 'en', 'alors', 'à', 'au', 'aux', 'écoutez', 'écoute', 'allez', 'adrien', 'elsa', 'avec']

# (3) Cases that apply only if followed by specific items:
# Keys: Words that are considered to undergo mandatory liaison in specific contexts
# Values: List of following words that trigger liaison for each Key.

only_before = {}
# 3rd person verbs in clitic groups:
for verb in verbs_3s:
	only_before[verb] = ['il', 'elle', 'on']
for verb in verbs_3p:
	only_before[verb] = ['ils', 'elles']

# Other cases:
only_before['vas']    = 'y'
only_before['allez']  = 'y'
only_before['allons'] = 'y'
only_before['prends'] = 'en'
only_before['prenez'] = 'en'
only_before['prenons'] = 'en'
only_before['comment'] = 'allez'
only_before['quand']   = ['il', 'elle','on', 'ils','elles']
only_before['quant']   = ['à', 'aux']
only_before['dans']    = ['un', 'une']
only_before['peut']    = only_before['peut'] + ['être']
only_before['bon']    = ['anniversaire', 'état', 'endroit', 'ordre', 'appui', 'escient', 'usage', 'appétit','achat', 'ami','investissement', 'exemple', 'enregistrement', 'emplacement'] # Note: we only apply liaison to "bon" in these specific cases in which it was used as a prenominal adjective, since "bon" is most often used as an interjection, in which case it doesn't undergo liaison.

#only_before['aller']   = ['à', 'au'] # Not mandatory 

# (4) Numbers 6, 9, 10:
vowel_ini_months = ['avril', 'août', 'octobre']
special_numbers = {}
special_numbers['six'] = exceptions_next + ['il', 'elle', 'on', 'un', 'une', 'en', 'alors', 'à', 'au', 'aux', 'écoutez', 'écoute', 'adrien', 'avec', 'y'] + vowel_ini_months
special_numbers['dix'] = exceptions_next + ['il', 'elle', 'on', 'un', 'une', 'en', 'alors', 'à', 'au', 'aux', 'écoutez', 'écoute', 'adrien', 'avec', 'y', 'après', 'onze'] + vowel_ini_months
special_numbers['n9f'] = exceptions_next + ['il', 'elle', 'on', 'un', 'une', 'en', 'alors', 'à', 'au', 'aux', 'écoutez', 'écoute', 'adrien', 'avec', 'y'] + vowel_ini_months


## Denasalization cases:
denasalization = {}
denasalization['bon']     = 'bOn'
denasalization['certain'] = 'sER-tEn'
denasalization['moyen']   = 'mwa-jEn'
denasalization['humain']  = 'y-mEn'
denasalization['prochain'] = 'pRo-SEN'
denasalization['sain']     = 'sEn'
denasalization['lointain'] = 'lw5-tEn'
denasalization['plein']    = 'plEn'
denasalization['ancien']   = '@-sjEn'
denasalization['vain']   = 'vEn'
denasalization['vilain'] = 'vi-lEn'
denasalization['divin']  = 'di-vin'
denasalization['fin']    = 'fin'

# Enchainement exceptions:
enchainement_exceptions = ['9m','5', 'Op']


#### FUNCTIONS ####
def silent_consonant(letter, phone):
	# Checks if a consonant is silent
	if (letter in liaison) and (phone not in pronunciation[letter]):
		return True
	else:
		return False

def check_vowel_onset(ortho_word):
	# Checks if a word begins with vowel or semi-vowel
	vowel_initial = ((ortho_word in dico) and (ortho_word not in punctuation) and
						(dico[ortho_word].replace('§', '4').replace('°', '6')[0] in vowels+semivowels)) # I replace special characters for matching vowels
	return vowel_initial
	
def check_liaison(line, all_words, k) :
	# This function checks if liaison applies, returns True or False
	# line: line ID (an integer)
	# all_words: full utterance (as a list)
	# k: index of the current word
	do_liaison = False
	current_word = all_words[k]
	next_word    = all_words[k+1]
	next_word_starts_with_vowel = check_vowel_onset(next_word)
	if (current_word not in punctuation) and (next_word_starts_with_vowel):
		next_word_2  = all_words[k+2]
		prev_word    = '#'
		if (k>0) :
			prev_word   = all_words[k-1]
			
		# Case 1: List of cases that apply only before specific items (see above)
		if (current_word in only_before) and (next_word in only_before[current_word]) :
			do_liaison = True
			
			# Corrections:
			# 'tu vas y ...':
			elif (current_word == 'vas') and (prev_word == 'tu') :
				do_liaison = False
			# 'ça peut être':
			elif (current_word == 'peut') and (prev_word == 'ça') and (next_word == 'être'):
				do_liaison = False
			# 'en fait', 'tout à fait', 'ça fait', etc:
			elif (current_word == 'fait') and (prev_word in ['en', 'à', 'au', 'ça']) :
				do_liaison = False
			# 'il faut...', 'il me faut...' cases:
			elif (current_word == 'faut') and ((prev_word in ['il', 'i(l)']) or (prev_word in ['me', 'te', 'lui', 'nous', 'vous', 'leur'] and next_word_2 not in punctuation + ['pour'])) :
				do_liaison = False
			# 'est il/elle/on' cases that are actually incorrect due to missing commas (e.g. ça y est il est parti)
			elif (current_word in ['est', 'était']) and (prev_word == 'y' or next_word_2 in ['est', 'a', 'était']) :
				do_liaison = False
			# general cases of 3rd person singular verb + il/elle/on that are incorrect due to missing commas
			elif (current_word in verbs_3s) and ((prev_word in ['a', 'il', 'i(l)', 'elle', 'on', "quelqu'un"]) or (next_word_2 in verbs_3s + ['y', 'ne', 'a', 'va', 'dit']) or (next_word == 'on' and next_word_2 == 'se')):
				do_liaison = False
			# general cases of 3rd person plural verb + ils/elles that are incorrect due to missing commas
			elif (current_word in verbs_3p) and ((prev_word in ['ont', 'ils', 'elles']) or (next_word_2 in verbs_3p)):
				do_liaison = False
				
			# # Print 3rd person verb cases for debugging:
			# if do_liaison == True and current_word in verbs_3s+verbs_3p:
				# print >> f_liaison_verbs_3rd, ('YES   ' + current_word + '  ' + next_word).ljust(20) + '  ' + ' '.join(all_words)
			# elif do_liaison == False and current_word in verbs_3s+verbs_3p:
				# print >> f_liaison_verbs_3rd, ('NO    ' + current_word + '  ' + next_word).ljust(20) + '  ' + ' '.join(all_words)
				
		# Case 2: List of cases that apply always except if followed by specific items
		elif (current_word in always_except) and (next_word not in always_except[current_word]):
			do_liaison = True
			if (current_word == 'aux') and (next_word == 'à'):
				do_liaison = False
				
		# Case 3: Plural noun + vowel-initial adjective # FOR THE MOMENT WE EXCLUDE IT (SEE TABLE 7 FROM BOULA DE MAREUIL ET AL 2003)
		#elif (current_word in plural_nouns) and (next_word in V_adjectives) :
		#	do_liaison = True
		
		# Case 4: Cases with special contexts:
		# Quand + est + ce:
		elif (current_word == 'quand') and (next_word == 'est') and (next_word_2 == 'ce'):
			do_liaison = True
		# Plus ou moins:
		elif (current_word == 'plus') and (next_word == 'ou') and (next_word_2 == 'moins'):
			do_liaison = True
		# Il était une fois:
		elif (current_word == 'était') and (prev_word == 'il') and (next_word == 'une') and (next_word_2 == 'fois'):
			do_liaison = True
		
		# If none of the above cases apply, print in rejected cases file:
		if do_liaison == False:
			rejected_case = (current_word+' '+next_word).ljust(30)
			print >> frejected, line+1, rejected_case, get_context(all_words, k)
		
		
	return do_liaison

def is_OL_cluster(current_word) :
	# Check word-final obstruent-liquid cluster
	return (len(current_word)>2) and (current_word[-2] in obstruents) and (current_word[-1] in liquids)
	
def check_liquid_deletion(all_words, k) :
	# This function checks if liquid deletion applies, returns True or False
	# all_words: full utterance (as a list)
	# k: index of the current word
	do_liquid_deletion = False
	current_word = all_words[k]
	next_word    = all_words[k+1]
	if is_OL_cluster(current_word) and (next_word[0] in consonants):
		do_liquid_deletion = True
	# Exception: contre jour
	if (current_word == 'k§tR') and (next_word == 'ZuR'):
		do_liquid_deletion = False
	return do_liquid_deletion
	
def check_C_cluster(word_phon,onset_or_coda):
	# This function checks if the 2 initial or final phonemes of a word form a consonant cluster, returns True or False
	# word_phon: phonological form of the word
	# onset_or_coda: initial or final consonants
	is_C_cluster = False
	if len(word_phon)>2 :
		if onset_or_coda == 'coda':
			phon1 = word_phon[-2]
			phon2 = word_phon[-1]
		elif onset_or_coda == 'onset':
			phon1 = word_phon[0]
			phon2 = word_phon[1]
		if (phon1 in consonants) and (phon2 in consonants):
			is_C_cluster = True
	return is_C_cluster
			
def check_schwa_insertion(all_words, k) :
	# This function checks if schwa insertion applies, returns True or False
	# all_words: full utterance (as a list)
	# k: index of the current word
	do_insert_schwa = False
	current_word = all_words[k]
	next_word    = all_words[k+1]
	if check_C_cluster(current_word,'coda') and check_C_cluster(next_word,'onset'):
		do_insert_schwa = True
	return do_insert_schwa

def check_enchainement(all_words, k) :
	# This function checks if enchainement applies, returns True or False
	# all_words: full utterance (as a list)
	# k: index of the current word
	do_enchainement = False
	current_word = all_words[k]
	next_word    = all_words[k+1].replace('§', '4').replace('°', '6') # Replace special characters before matching vowels
	if (current_word not in enchainement_exceptions) and (next_word not in enchainement_exceptions + punctuation):
		if (current_word[-1] in consonants) and (len(current_word)==1):
			do_enchainement = True
		elif (current_word[-1] in consonants) and (next_word[0] in vowels + semivowels):
			do_enchainement = True
		elif (current_word[-1] == "'"):
			do_enchainement = True
	return do_enchainement
	
def apply_enchainement(newwords, i) :
	currentword = newwords[i].replace("'","").replace('§', '4').replace('°', '6') # Remove apostrophes and replace special characters
	# Select which consonants to resyllabify:
	if not any(phoneme in vowels for phoneme in currentword):
		final_consonants = currentword # Whole word if it contains no vowels
		newwords[i] = ""
	elif is_OL_cluster(currentword):
		final_consonants = currentword[-2:] # OL clusters
		newwords[i] = currentword[:-2]
	else:
		final_consonants = currentword[-1] # Otherwise only final consonant
		newwords[i] = currentword[:-1]
		
	if (final_consonants[-1] == 'Z') and (newwords[i+1][0] in unvoiced_obstruents):
		final_consonants = final_consonants[:-1] + 'S'  # De-voicing of j(e) before unvoiced obstruents

	newwords[i+1] = (final_consonants + newwords[i+1]).replace('4','§').replace('6','°') # Append consonants to next word and re-introduce special characters if any
	newwords[i]   = newwords[i].replace('4','§').replace('6','°') # Remove from current word and re-introduce special characters if any
	return newwords

def get_context(line, k):
	# This function retrieves (if possible) 5 words from an utterance,
	# centered around a target word k (k=index of target word in utterance).
	if len(line)<6:
		context = line
	elif (len(line)>=6) and (k<=2):
		context = line[:6]
	elif (len(line)>=6) and (k>2) and (k<= len(line)-2):
		context = line[k-2:k+3]
	else:
		context = line[-6:]
	context = ' '.join(context)
	return context
	
def print_applied_liaison(line_index, all_words, k, transcribed_word, file_name):
	# This prints a list of all the liaison cases that were applied.
	current_word = all_words[k]
	next_word    = all_words[k+1]
	unedited = (current_word + ' ' + next_word).decode('utf-8').encode('cp1252').ljust(30) # Reencode in ANSI to left-justify
	unedited = unedited.decode('cp1252').encode('utf-8')                                   # Back to unicode for printing
	edited   = (transcribed_word + ' ' + dico[next_word]).decode('utf-8').encode('cp1252').ljust(30)
	edited   = edited.decode('cp1252').encode('utf-8')
	# Add a part of the sentence to clarify the context:
	context = get_context(all_words, k)
	print >> file_name, (str(line_index + 1).ljust(5) + unedited + edited + context)
	
def print_applied_cases(line_index, all_words_phon, k, all_words_ort, transcribed_word, file_name):
	# This prints a list of all the liquid deletion or schwa insertion cases that were applied.
	current_word_ort = all_words_ort[k]
	next_word_ort    = all_words_ort[k+1]
	next_word_phon   = all_words_phon[k+1]
	unedited = (current_word_ort + ' ' + next_word_ort).decode('utf-8').encode('cp1252').ljust(30)
	unedited = unedited.decode('cp1252').encode('utf-8')
	edited   = (transcribed_word + ' ' + next_word_phon).decode('utf-8').encode('cp1252').ljust(30)
	edited   = edited.decode('cp1252').encode('utf-8')
	# Add context:
	context = get_context(all_words_ort, k)
	print >> file_name, (str(line_index + 1).ljust(5) + unedited + edited + context)
	
def print_enchainement(line_index, k, all_words_ort, transcribed_word, transcribed_word_2, file_name):
	# This prints a list of all the enchainement cases that were applied.
	current_word_ort = all_words_ort[k]
	next_word_ort    = all_words_ort[k+1]
	#print line_index
	unedited = (current_word_ort + ' ' + next_word_ort).decode('utf-8').encode('cp1252').ljust(30)
	unedited = unedited.decode('cp1252').encode('utf-8')
	edited   = (transcribed_word + ' ' + transcribed_word_2).decode('utf-8').encode('cp1252').ljust(30)
	edited   = edited.decode('cp1252').encode('utf-8')
	if (edited[0] == ' '): # Correct empty spaces when the first word was absorbed fully by second word
		edited = edited[1:]
	# Add context:
	context = get_context(all_words_ort, k)
	print >> file_name, (str(line_index + 1).ljust(7) + unedited + edited + context)

	
	
#### MAIN BODY OF TRANSCRIPTION CODE ####
for corpusdir in dirlist:
	print 'Recoding transcription of:', corpusdir
	input_location  = 'corpora/' + corpusdir + '/clean'
	output_location = 'output/'  + corpusdir
	if not os.path.exists(output_location):
		os.makedirs(output_location)
		
	#### 1: FIRST TRANSCRIPTION + LIAISON ####
	# Open output files:
	f         = open(output_location + '/liaison_cases.txt', 'w')
	foutput   = open(output_location + '/recoded_with_liaison.txt','w')
	frejected = open(output_location + '/rejected_liaison_cases.txt', 'w')

	# Read line by line, transcribe from dictionary and apply liaison if appropriate
	with open(input_location + '/extract.txt') as input_file:
		for line_ID, line_text in enumerate(input_file):
			newwords  = []
			full_line = line_text.lower().split()
			info  = full_line[:4] # ID and age
			words = full_line[4:] # Start reading in 5th column, first 4 are ID and age
			
			for i, word in enumerate(words[:-1]): 
				if word in dico:
					# Transcribe the word:
					newwords.append(dico[word])
					
					# Check and apply liaison:
					lastletter = word[-1]
					lastphon   = newwords[i][-1]
					next_word  = words[i+1]
					# General case (silent consonant):
					if silent_consonant(lastletter, lastphon) and check_liaison(line_ID, words, i) :
						newwords[i] += liaison[lastletter] # Attach liaison consonant
						if word in denasalization:
							newwords[i] = denasalization[word]
						print_applied_liaison(line_ID, words, i, newwords[i], f)
					# Special case: numbers six, neuf, dix
					elif (word in special_numbers) and (next_word in V_nouns) and (next_word not in special_numbers[word]):
						newwords[i] = newwords[i][:-1] + liaison[lastphon]
						print_applied_liaison(line_ID, words, i, newwords[i], f)
					elif (word in special_numbers) and (lastphon == 's') and (words[i+1] in C_nouns):
						newwords[i] = newwords[i][:-1]
						
					# Correct alternative pronunciation of tous (with or without silent consonant):
					if (word == 'tous') and (next_word in ['les', 'des', 'ces', 'nos', 'vos', 'ses', 'tes', 'ceux']):
						newwords[i] = newwords[i][:-1]
				else:
					# Word not found in dictionary:
					newwords.append('#')
					
			newwords.append(full_line[-1])
			print >> foutput , ' '.join(info + newwords) # Concatenate with ID and age and print

	f.close()
	foutput.close()
	frejected.close()


	#### 2: LIQUID DELETION ####
	# Open output files:
	f2       = open(output_location + '/liquid_deletion_cases.txt', 'w')
	foutput2 = open(output_location + '/recoded_L_D.txt', 'w')

	# Load orthographic transcription:
	text_ort = []
	with open(input_location + '/extract.txt') as original_file:
		for line_ID, line_text in enumerate(original_file):
			text_ort.append(line_text.strip())
			
	with open(output_location + '/recoded_with_liaison.txt') as input_file:
		for line_ID, line_text in enumerate(input_file):
			newwords      = []
			full_line     = line_text.split()
			full_line_ort = text_ort[line_ID].split()
			info      = full_line[:4] # ID and age
			words     = full_line[4:] # Start reading in 5th column, first 4 are ID and age
			words_ort = full_line_ort[4:]
			
			for i, word in enumerate(words[:-1]): 
				newwords.append(word)
				if (word != '#') and check_liquid_deletion(words, i) :
					newwords[i] = word[:-1] # Delete liquid
					print_applied_cases(line_ID, words, i, words_ort, newwords[i], f2)
					
			newwords.append(full_line[-1])
			print >> foutput2 , ' '.join(info + newwords) # Concatenate with ID and age and print
			
	f2.close()
	foutput2.close()


	#### 3: SCHWA INSERTION ####
	if do_schwa_insertion:
		# Open output files:
		f3       = open(output_location + '/schwa_insertion_cases.txt', 'w')
		foutput3 = open(output_location + '/recoded_L_D_S.txt', 'w')

		with open(output_location + '/recoded_L_D.txt') as input_file:
			for line_ID, line_text in enumerate(input_file):
				newwords  = []
				full_line = line_text.split()
				full_line_ort = text_ort[line_ID].split()
				info  = full_line[:4] # ID and age
				words = full_line[4:] # Start reading in 5th column, first 4 are ID and age
				words_ort = full_line_ort[4:]
				
				for i, word in enumerate(words[:-1]): 
					newwords.append(word)
					if (word != '#') and check_schwa_insertion(words, i) :
						newwords[i] += '°' # Add schwa
						print_applied_cases(line_ID, words, i, words_ort, newwords[i], f3)
						
				newwords.append(full_line[-1])
				print >> foutput3 , ' '.join(info + newwords) # Concatenate with ID and age and print
			
		f3.close()
		foutput3.close()


	#### 4: ENCHAINEMENT ####
	# Open output files:
	f4       = open(output_location + '/enchainement_cases.txt', 'w')
	if do_schwa_insertion:
		foutput4 = open(output_location + '/recoded_L_D_S_E.txt', 'w')
		previous_recoded_file_name = '/recoded_L_D_S.txt'
	else:
		foutput4 = open(output_location + '/recoded_L_D_E.txt', 'w')
		previous_recoded_file_name = '/recoded_L_D.txt'

	with open(output_location + previous_recoded_file_name) as input_file:
		for line_ID, line_text in enumerate(input_file):
			newwords  = []
			full_line = line_text.split()
			full_line_ort = text_ort[line_ID].split()
			info     = full_line[:4] # ID and age
			newwords = full_line[4:] # Start reading in 5th column, first 4 are ID and age
			words_ort = full_line_ort[4:]
			
			for i, word in enumerate(newwords[:-1]): 
				if (word != '#') and check_enchainement(newwords, i) :
					newwords = apply_enchainement(newwords, i)
					print_enchainement(line_ID, i, words_ort, newwords[i], newwords[i+1], f4)
					
			newwords = filter(None, newwords)
			print >> foutput4 , ' '.join(info + newwords) # Concatenate with ID and age and print
		
	f4.close()
	foutput4.close()
f_liaison_verbs_3rd.close()