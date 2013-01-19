#!/bin/bash

python pyheatmap/mapcoords.py \
	--area=46.304588,57.457436,180.304596,191.457428 \
	resources/positions.csv \
	| \
python pyheatmap/heataccum.py \
	--grid=100,100 \
	| \
python pyheatmap/heatmap.py \
	--palette=resources/palette.png \
	--bg=resources/usa.jpg \
	--dot=35 \
	--opacity=0.8