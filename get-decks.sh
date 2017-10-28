#!/bin/bash
# Used the following snippet to generate the dueck_urls.
# Manually went to each omnath-rage search page (1-10) on tapped out, rated by order and ran this snippet:
#str = ""
#$('.name.deck-wide-header').each(function(){
#    str += $(this).children().first().attr('href')+"\n";
#    });
#console.log(str)
thread_count=5
running_wget=`ps aux | grep wget | wc -l`
filename='deck_urls'
deck_contents=`cat deck_urls`
total_decks=$((`cat deck_urls | wc -l`-$thread_count))
IFS=$'\n' read -d '' -r -a lines < deck_urls
i=0

remainding_threads=$((`expr $total_decks % $thread_count`+1))

for (( i=0; i < total_decks; i+=thread_count )); do
	for (( j=0; j < thread_count; j++)); do
		wget -O "mtg-decks/deck-"$(($i+$j)) "http://tappedout.net/mtg-decks/"${lines[$(($i+$j))]} &
	done

	while true; do
		running_wget=`ps aux | grep wget | wc -l`
		sleep 1
		if [ $running_wget -eq "1" ]; then
			break
		fi
	done
done

#i variable still set
for (( j=0; j < remainding_threads; j++)); do
	wget -O "mtg-decks/deck-"$(($i+$j)) "http://tappedout.net/mtg-decks/"${lines[$(($i+$j))]} &
done

while true; do
	running_wget=`ps aux | grep wget | wc -l`
	sleep 1
	if [ $running_wget -eq "1" ]; then
		break
	fi
done