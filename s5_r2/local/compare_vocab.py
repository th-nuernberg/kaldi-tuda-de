#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

filter_stopwords=True

stopwords = []
if filter_stopwords:
    with open('data/stop_words_german.txt') as f:
        for l in f.readlines():
            stopwords.append(l.rstrip().lower())

text1 = []
print(f"Text1: {sys.argv[1]}")
with open(sys.argv[1], 'r', encoding='UTF-8') as f:
    for l in f.readlines():
        words = [i.strip().lower() for i in l.split()]
        # first elem is utt_id
        words.pop(0)
        text1 += words

text2 = []
print(f"Text2: {sys.argv[2]}")
with open(sys.argv[2], 'r', encoding='UTF-8') as f:
    for l in f.readlines():
        words = [i.strip().lower() for i in l.split()]
        # first elem is utt_id
        words.pop(0)
        text2 += words

text1 = list(set(text1))
text2 = list(set(text2))

if filter_stopwords:
    text1 = [i for i in text1 if i not in stopwords]
    text2 = [i for i in text2 if i not in stopwords]

intersect = list(set(text1).intersection(text2))

print(f"Text 1 has {len(text1)} unique words, text 2 has {len(text2)} unique words")
print(f"Number of common words: {len(intersect)}")
print(f"Overlap of text 1: {len(intersect)/len(text1)*100:.1f}%")
print(f"Overlap of text 2: {len(intersect)/len(text2)*100:.1f}%")

# data/voxpopuli_train/text
# data/mls_train/text
# data/test_hires/text
# data/tuda_train/text
# data/m_ailabs_train/text
# data/tuda_ailabs_swc_train_text


# No stopwords filter
# Text1: data/tuda_ailabs_swc_train_text
# Text2: data/test_hires/text
# Text 1 has 223380 unique words, text 2 has 5745 unique words
# Number of common words: 4894
# Overlap of text 2: 85.2%

# Text1: data/voxpopuli_train/text
# Text2: data/test_hires/text
# Text 1 has 73078 unique words, text 2 has 5745 unique words
# Number of common words: 4424
# Overlap of text 2: 77.0%

# Text1: data/mls_train/text
# Text2: data/test_hires/text
# Text 1 has 304688 unique words, text 2 has 5745 unique words
# Number of common words: 4329
# Overlap of text 1: 1.4%
# Overlap of text 2: 75.4%

###############################################################

# With stopwords filter
# Text1: data/tuda_ailabs_swc_train_text
# Text2: data/test_hires/text
# Text 1 has 222771 unique words, text 2 has 5329 unique words
# Number of common words: 4478
# Overlap of text 1: 2.0%
# Overlap of text 2: 84.0%

# Text1: data/voxpopuli_train/text
# Text2: data/test_hires/text
# Text 1 has 72513 unique words, text 2 has 5329 unique words
# Number of common words: 4011
# Overlap of text 1: 5.5%
# Overlap of text 2: 75.3%

# Text1: data/mls_train/text
# Text2: data/test_hires/text
# Text 1 has 304080 unique words, text 2 has 5329 unique words
# Number of common words: 3913
# Overlap of text 1: 1.3%
# Overlap of text 2: 73.4%