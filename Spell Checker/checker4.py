import time
encodes = {"অ" :"o",  "আ": "a", "া": "a",  "ই": "i", "ঈ": "i", "ি":"i", "ী" : "i", "উ" : "u", "ঊ": "u", "ু": "u", "ূ": "u", "এ": "e", "ে": "e", "ঐ": "oi", "ৈ": "oi", "ও": "o", "ঔ": "ou","ৌ": "ou", "ক": "k", "খ": "k", "গ": "g", "ঘ": "g", "ঙ": "ng", "ং": "ng", "চ": "c", "ছ": "c", "য": "j", "জ": "j", "ঝ": "j", "ঞ": "n", "ট": "T", "ঠ": "T", "ড": "D", "ঢ": "D", "ঋ": "ri", "র": "r", "ড়": "r", "ঢ়": "r", "ন": "n", "ণ": "n", "ত": "t", "থ": "t", "দ": "d", "ধ": "d", "প": "p", "ফ": "p", "ব": "b", "ভ": "b", "ম": "m", "য়": "y", "ল": "l", "শ": "s", "স": "s", "ষ": "s", "হ": "h", "ঃ" : "h", "ৎ": "t"}
max_edit_distance = 2

def get_edit_distance(word1, word2):
    m, n = len(word1), len(word2)
    # if abs(m-n)>max_edit_distance: return max_edit_distance+1
    dp = [[0 for v in range(m+1) ] for __ in range(n+1) ]
    for i in range(m+1):
        dp[0][i] = i
    for i in range(n+1):
        dp[i][0] = i
    for j in range(1, m+1):
        for i in range(1, n+1):
            dp[i][j] = min(dp[i-1][j-1] + (word1[j-1]!=word2[i-1]) , dp[i-1][j]+1, dp[i][j-1]+1)
            
    return dp[n][m]

def get_encoded_word(word):
    encoded_word = ""
    for w in word:
        if w in encodes:
            encoded_word += encodes[w]
    return encoded_word

def create_delete_list(word, delete_words, edit_distance = 1):
	l = len(word)
	if edit_distance > max_edit_distance or l <3 : return
	
	for c in range(l):
		new_word = word[:c] + word[c+1:]
		if new_word not in delete_words:
			delete_words.append(new_word)
			if len(new_word) > 2:
				create_delete_list(new_word, delete_words, edit_distance + 1)

def weighted_distance(phonetic_edit_dist, edit_dist):
	return phonetic_edit_dist*0.6 + edit_dist*0.4

def generate_dictionary():
	file = open('dict.txt', 'r')
	lines = file.readlines()
	file.close()
	dictionary, encode_to_word_map = {}, {}
	for line in lines:
		encoded_word, real_word,  count = line.strip().split()
		if encoded_word in encode_to_word_map:
			encode_to_word_map[encoded_word].append((real_word, int(count)))
		else: 
			encode_to_word_map[encoded_word] = [(real_word, int(count))]

		if encoded_word not in dictionary:
			dictionary[encoded_word] = []
		
		delete_words = []
		create_delete_list(encoded_word, delete_words)

		for item in delete_words:
			if item in dictionary:
				dictionary[item].append(encoded_word)
			else: dictionary[item] = [encoded_word]
	return dictionary, encode_to_word_map

def get_suggestion(dictionary, encode_to_word_map, input_word):
	suggestion_dic = {}
	encoded_input_word = get_encoded_word(input_word)
	encoded_input_word_len = len(encoded_input_word)
	listed_encoded_words = []
	if encoded_input_word in dictionary:
		if encoded_input_word in encode_to_word_map:
			listed_encoded_words.append(encoded_input_word)
			for word_tuple in encode_to_word_map[encoded_input_word]:
				suggestion_dic[word_tuple[0]] = (word_tuple[1], weighted_distance(0, get_edit_distance(input_word, word_tuple[0])))

		for encoded_word in dictionary[encoded_input_word]:
			if encoded_word not in listed_encoded_words:
				listed_encoded_words.append(encoded_word)
				phonetic_edit_dist = len(encoded_word) - encoded_input_word_len
				for word_tuple in encode_to_word_map[encoded_word]:
					suggestion_dic[word_tuple[0]] = (word_tuple[1], weighted_distance(phonetic_edit_dist, get_edit_distance(input_word, word_tuple[0])))
	
	encoded_delete_words = []
	create_delete_list(encoded_input_word, encoded_delete_words)
	for encoded_delete_word in encoded_delete_words:
		if encoded_delete_word in dictionary:
			if encoded_delete_word in encode_to_word_map:
				if encoded_delete_word not in listed_encoded_words:
					listed_encoded_words.append(encoded_delete_word)
					phonetic_edit_dist = encoded_input_word_len - len(encoded_delete_word)
					for word_tuple in encode_to_word_map[encoded_delete_word]:
						suggestion_dic[word_tuple[0]] = (word_tuple[1], weighted_distance(phonetic_edit_dist, get_edit_distance(input_word, word_tuple[0])))

			else:
				for encoded_word in dictionary[encoded_delete_word]:
					if encoded_word not in listed_encoded_words:
						listed_encoded_words.append(encoded_word)
						phonetic_edit_dist = get_edit_distance(encoded_word, encoded_input_word)
						for word_tuple in encode_to_word_map[encoded_word]:
							suggestion_dic[word_tuple[0]] = (word_tuple[1], weighted_distance(phonetic_edit_dist, get_edit_distance(input_word, word_tuple[0])))

	return suggestion_dic

def main():
	
	dictionary, encode_to_word_map = generate_dictionary()
	# suggestion_dic = get_suggestion(dictionary, encode_to_word_map, "অংকন")
	# print(suggestion_dic)
	# suggestions = sorted(suggestion_dic, key = lambda x: (suggestion_dic[x][1], -suggestion_dic[x][0]))
	# print(suggestions)
	file = open('test.txt', 'r')
	lines = file.readlines()
	file.close()
	count=0
	first_count = 0
	third_count = 0
	c=0
	start_time = time.time()
	for line in lines:
		wrong, correct = line.split('-')
		correct = correct.strip()
		suggestion_dic = get_suggestion(dictionary, encode_to_word_map, wrong.strip())
		
		suggestions = sorted(suggestion_dic, key = lambda x: (suggestion_dic[x][1], -suggestion_dic[x][0]))
		if correct in suggestions[:10]:
			count+=1
			if correct in suggestions[:3]:
				third_count  += 1
				if correct == suggestions[0]:
					first_count  += 1

	print(count, third_count,  first_count)
	print(time.time()-start_time)
	
if __name__ == '__main__':
	main()




# accuracy using wiki data

# max_phonetic edit distance = 1
# 1st position: 77%
# upto 3rd postion: 93%
# upto 5th postion: 94%
# upto 10th position: 95%
# average time per word: 0.5 ms

# max_phonetic edit distance = 2
# 1st position: 77%
# upto 3rd postion: 93%
# upto 5th postion: 95%
# upto 10th position: 97%
# average time per word: 8 ms