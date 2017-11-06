import pickle
import os, os.path
import json
from pprint import pprint
from collections import Counter

deck_lists = []
synergy_dict = {}

synergy_amount = 0.9
number_of_synergy_cards_deep = 28
number_of_deck_cards_deep = 150
min_count_for_synergy = 4

# Weird glitch makes this modifier necessary, peak synergy occurs at 75%, need to figure out why.
synergy_amount = synergy_amount*.75
original_amount = 1.0-synergy_amount
cards_to_go_over = number_of_deck_cards_deep


# Thanks to answer by Daniel Stutzbach at https://stackoverflow.com/questions/2632205/how-to-count-the-number-of-files-in-a-directory-using-python
DIR = './mtg-decks'
total_length = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])-1

with open('AllCards.json') as card_data:
	all_cards = json.load(card_data)

land_cards = []

for key in all_cards:
	if all_cards[key]['type'] == "Land":
		land_cards.append(key)

card_weights = {}
card_percentages = {}
card_count = 0

deck_list_collection = []

for i in range(total_length):
	filename='mtg-decks/deck-'+str(i)

	f = open(filename, 'r')
	line = f.readline()

	while line:
		is_deck_list = line.find('tcg_checkout')

		line = f.readline()

		if is_deck_list < 0:
			continue

		deck_entry = line.find('value=')+9
		entry_end = line.find('>', deck_entry)-1

		raw_deck = line[deck_entry:entry_end]

		split_deck = raw_deck.split("||1 ")

		for j in range(len(split_deck)):
			current_card = str(split_deck[j])
			current_card = str(current_card).replace("&","")
			current_card = str(current_card).replace(";","")
			current_card = str(current_card).replace("#","")
			# Replace that HTML character code with an actual apostrophe
			current_card = str(current_card).replace("39","'")
			split_deck[j] = current_card

		deck_list_collection.append(split_deck)
		deck_lists = deck_lists + split_deck

		# Create the synergy dictionary entries.
		for j in range(len(split_deck)):
			copy_deck = split_deck[:]
			current_card = split_deck[j]
			copy_deck.pop(j)

			if current_card in synergy_dict:
				synergy_dict[current_card] = synergy_dict[current_card]+copy_deck
			else:
				synergy_dict[current_card] = copy_deck
	f.close()

card_frequencies = Counter(deck_lists)

# Remove low frequency cards from the list.
keys_to_remove = []
for key in card_frequencies:
	if card_frequencies[key] < min_count_for_synergy:
		keys_to_remove.append(key)

for key in keys_to_remove:
	del card_frequencies[key]

# Get the weighted values of each card.
for key in card_frequencies:
	card_count = card_count + card_frequencies[key]
	card_weights[key] = float(card_frequencies[key])/total_length

# Generate the synergy list
card_synergies = {}

# Initialize the card synergies.
for key in card_frequencies:
	card_synergies[key] = Counter()
	for other_key in card_frequencies:
		# Skip repeats
		if (key == other_key):
			continue
		card_synergies[key][other_key] = 0

for deck in deck_list_collection:
	for card_x in deck:
		# Skip low frequency cards
		if card_x not in card_frequencies:
			continue

		for card_y in deck:
			# Skip repeats
			if (card_x == card_y):
				continue
			# Skip low frequency cards
			if card_y not in card_frequencies:
				continue

#			if card_x == 'Parallel Lives':
#				if card_y == 'Primal Vigor':
#					print "found primal vigor!"


			card_synergies[card_x][card_y] += 1

weighted_synergies = {}
# Initialize the weighted synergies.
for key in card_frequencies:
	weighted_synergies[key] = {}

for key in card_synergies:
	for other_key in card_synergies[key]:
		tmp_synergy_value = float(card_synergies[key][other_key])
		# Skip no-synergy onces
		if tmp_synergy_value < .001:
			continue
		tmp_frequency_value = float(card_frequencies[other_key])
		tmp_weighted_value = float(tmp_synergy_value / tmp_frequency_value)
		weighted_synergies[key][other_key] = tmp_weighted_value
#		if (tmp_weighted_value >= .95):
#			print "Card "+key+" synergizes "+str(tmp_weighted_value)+"% of the time with card "+other_key
#			print "number of synergies: "+str(tmp_synergy_value)+", number of occurences: "+str(tmp_frequency_value)

ordered_weighted_synergies = {}
cards_to_reorder = {}
reordered_sort = []

# Ordered weighted synergies.
for key in weighted_synergies:
	tmp_sorted_synergies = sorted(weighted_synergies[key].items(), key=lambda x: x[1], reverse=True)

	number_same = 0
	for i in range(len(tmp_sorted_synergies)-1):
		if number_same > 0:
			number_same -= 1
			continue
		number_same = 0
		for j in range(i,len(tmp_sorted_synergies)):
			if tmp_sorted_synergies[j][1] != tmp_sorted_synergies[i][1]:
				number_same = j - i
				break
			if j == len(tmp_sorted_synergies)-1:
				number_same = j - i
				break
		cards_to_reorder.clear()
		del reordered_sort[:]
		if number_same != 0:
			for j in range(i, i+number_same):
				card_to_reorder = tmp_sorted_synergies[j][0]
				cards_to_reorder[card_to_reorder] = card_frequencies[card_to_reorder]
			reordered_sort = sorted(cards_to_reorder.items(), key=lambda x: x[1], reverse=True)
			for j in range(i, i+number_same):
				tmp_sorted_synergies[j] = tuple([reordered_sort[j-i][0],tmp_sorted_synergies[i][1]])

	ordered_weighted_synergies[key] = tmp_sorted_synergies



cultivate_ordered_weights = ordered_weighted_synergies['Cultivate']
#for i in range(len(cultivate_ordered_weights)):
#	print cultivate_ordered_weights[i][0]+" "+str(cultivate_ordered_weights[i][1])+", "+str(card_frequencies[cultivate_ordered_weights[i][0]])

#print ordered_weighted_synergies['Cultivate']

print "Done figuring out weights."

#exit()

tmp_card_freq = {}
# card_frequencies
for key in card_frequencies:
	tmp_card_freq[key] = float(card_frequencies[key])

sorted_tmp_card_freq = sorted(card_frequencies.items(), key=lambda x: x[1], reverse=True)

current_deck = [None] * number_of_deck_cards_deep
average_deck = []

#previous_deck = []
previous_deck = sorted_tmp_card_freq[:number_of_deck_cards_deep]

# Seed the root card in the deck.
for i in range(number_of_deck_cards_deep):
	average_deck.append(([sorted_tmp_card_freq[i][0], sorted_tmp_card_freq[i][1]]))

for i in range(number_of_deck_cards_deep):
	current_card = sorted_tmp_card_freq[i][0]
	number_synergy_cards = len(ordered_weighted_synergies[current_card])
	number_to_loop = number_of_synergy_cards_deep;
	if number_synergy_cards < number_of_synergy_cards_deep:
		number_to_loop = number_synergy_cards
	for j in range(number_to_loop):
#	for j in range(number_synergy_cards):
		tmp_syn_card = ordered_weighted_synergies[current_card][j][0]
		tmp_syn_freq = float(ordered_weighted_synergies[current_card][j][1])
		default_value = float(original_amount * float(card_frequencies[tmp_syn_card]))
		tmp_syn_value = float(synergy_amount * tmp_syn_freq * default_value)

		new_value = float(default_value + tmp_syn_value)
		tmp_card_freq[tmp_syn_card] = new_value

	sorted_tmp_card_freq = sorted(tmp_card_freq.items(), key=lambda x: x[1], reverse=True)
	del current_deck[:]
	for j in range(i+1):
		current_deck.append(sorted_tmp_card_freq[j][0])

#	for 

current_deck_list = [None] * cards_to_go_over
previous_deck_list = [None] * cards_to_go_over

# 110 here so we can see the trailing values.
for i in range(cards_to_go_over):
#	current_deck_list[i] = current_deck[i]
	current_deck_list[i] = sorted_tmp_card_freq[i][0]
	previous_deck_list[i] = previous_deck[i][0]


cards_to_go_through = 100

current_full_deck = current_deck_list[:cards_to_go_through]
previous_full_deck = previous_deck_list[:cards_to_go_through]

#print "current_deck: "
#print current_deck_list
#print "previous_deck: "
#print previous_deck_list

total_different_cards = 0

for i in range(cards_to_go_through):
	if current_full_deck[i] not in previous_full_deck:
		total_different_cards += 1

non_shared_cards = [None] * total_different_cards
non_shared_cards_previous = [None] * total_different_cards

current_missing_idx = 0
previous_missing_idx = 0

for i in range(cards_to_go_through):
	if current_full_deck[i] not in previous_full_deck:
		non_shared_cards[current_missing_idx] = current_full_deck[i]
		current_missing_idx += 1
	if previous_full_deck[i] not in current_full_deck:
		non_shared_cards_previous[previous_missing_idx] = previous_full_deck[i]
		previous_missing_idx += 1


print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
print "different cards: "
print non_shared_cards
print "previous missing cards: "
print non_shared_cards_previous


print "total number of different cards: "+str(total_different_cards)

print "~ DECK ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"


build_offset = 0


total_basics = 19
total_non_basics = 17

only_get_some = 100 - total_basics

non_basics_available = 0
for i in range(100):
	tmp_key = current_deck_list[i]
	if tmp_key in land_cards:
		non_basics_available += 1

non_basics_diff =  non_basics_available - total_non_basics

if non_basics_diff < 0:
	print "Add "+str(non_basics_diff * -1)+" additional lands."
	only_get_some = non_basics_diff + only_get_some

for i in range(12):
	print "Forest"
for i in range(7):
	print "Mountain"


for i in range(only_get_some):
	tmp_key = current_deck_list[i+build_offset]

	if total_non_basics == 0:
		# Get the next non-land card.
		while tmp_key in land_cards:
			build_offset += 1
			tmp_key = current_deck_list[i+build_offset]
	else:
		if tmp_key in land_cards:
			total_non_basics -= 1;

	if tmp_key == "Omnath, Locus of Rage":
		print "Omnath, Locus of Rage *CMDR*"
	else:
		print "%s" % (tmp_key)



"""
print "Starting setting up new synergized counts"

card_limit=200
card_counter=0
total_synergy_counts = {}	
overall_synergy_count = 0

for key in synergy_dict:
	tmp_count = Counter(synergy_dict[key])
	synergy_count = 0
	for tmp_key in tmp_count:
		synergy_count = synergy_count + tmp_count[tmp_key]
	total_synergy_counts[key] = synergy_count
	overall_synergy_count = overall_synergy_count + synergy_count

weighted_total_synergy_counts = {}
for key in total_synergy_counts:
	current_count = total_synergy_counts[key]
	weighted_total_synergy_counts[key] = float(current_count)/float(overall_synergy_count)

print "All Setup. Doing hard lifting now."

synergized_counts = {}

for key in card_weights:
	current_weight = card_weights[key]*original_amount
	synergy_cards = synergy_dict[key]
	for card in synergy_cards:
		synergy_weight = weighted_total_synergy_counts[card]*synergy_amount
		weighted_value = synergy_weight * current_weight
		if card in synergized_counts:
			synergized_counts[card] = synergized_counts[card] + weighted_value
		else:
			synergized_counts[card] = weighted_value

for key in synergized_counts:
	synergized_counts[key] = synergized_counts[key]/card_frequencies[key]*3

final_deck = {}

for key in synergized_counts:
	original_value = card_weights[key]*original_amount
	synergy_value = synergized_counts[key]*synergy_amount
	combined_value = original_value+synergy_value
	final_deck[key] = combined_value

for i in range(12):
	print "Forest"
for i in range(7):
	print "Mountain"

total_basics = 19
total_non_basics = 17

only_get_some = 100 - total_basics


total_non_basics = total_non_basics - 3

for key, value in sorted(final_deck.iteritems(), key=lambda (k,v): (v,k), reverse=True):
	only_get_some = only_get_some - 1
	if key in land_cards:
		if total_non_basics < 0:
			only_get_some = only_get_some + 1
			continue

		total_non_basics = total_non_basics - 1

	if only_get_some < 0:
		break

	if key == "Omnath, Locus of Rage":
		print "Omnath, Locus of Rage *CMDR*"
	else:
		print "%s" % (key)
"""