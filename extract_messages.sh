git grep translate \
	| grep -o '{{[^{]*| *translate' \
	| sed 's/ *| *translate//g;s/^{{ *//g' \
	| grep "^'" \
	| sed "s/'//g" \
	| sort | uniq
