import pickle
import os, os.path
import json
from pprint import pprint
from collections import Counter
from itertools import dropwhile

deck_lists = []
synergy_dict = {}

average_cards = 76

synergy_amount = .95
original_amount = 1.0-synergy_amount

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
	if card_frequencies[key] < 4:
		keys_to_remove.append(key)

for key in keys_to_remove:
	del card_frequencies[key]

# Get the weighted values of each card.
for key in card_frequencies:
	card_count = card_count + card_frequencies[key]
	card_weights[key] = float(card_frequencies[key])/total_length

# Generate the synergy list
tmp_card_freq = card_frequencies

card_synergies = {}

print "Starting card frequencies top"
# Initialize the card synergies.
for key in card_frequencies:
	card_synergies[key] = Counter()
	for other_key in card_frequencies:
		# Skip repeats
		if (key == other_key):
			continue
		card_synergies[key][other_key] += 0

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

			card_synergies[card_x][card_y] += 1
print "Done cycling through decks."

weighted_synergies = {}
# Initialize the weighted synergies.
for key in card_frequencies:
	weighted_synergies[key] = {}

print "Done initializing weighted synergies"

for key in card_synergies:
	for other_key in card_synergies[key]:
		tmp_synergy_value = card_synergies[key][other_key]
		tmp_frequency_value = card_frequencies[other_key]
		weighted_synergies[key][other_key] = tmp_synergy_value / tmp_frequency_value

print "Done applying synergy weights"

print weighted_synergies


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