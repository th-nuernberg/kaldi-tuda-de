#!/usr/bin/env bash

# This script fixes the data/local/dict dir. 
# Most importantly, the <UNK> symbol will no longer be mapped onto silence. 
# To be run from one directory above this script.

# ls data/local/dict
# extra_questions.txt  lexiconp.txt lexicon.txt x nonsilence_phones.txt  optional_silence.txt  x silence_phones.txt x

echo "$0 $@"  # Print the command line for logging.

if [ -f path.sh ]; then . ./path.sh; fi
. parse_options.sh || exit 1;

if [ $# -ne 3 ]; then
    echo "Usage: $0 <dict-dir> <out-dir>"
    echo "e.g.: $0 data/local/dict data/local/dict_fixed2"
    exit 1;
fi

srcdir=$1
dir=$2

cp -r $srcdir $dir || exit 1;

# Overwrite nonsilence phones
( echo sil; echo spn; echo nsn; echo lau ) > $dir/silence_phones.txt

# Overwrite optional silence
echo sil > $dir/optional_silence.txt

# Remove unk symbol from existing lexicon
sed '/<UNK>*/d' $dir/lexicon.txt > $dir/lexicon0.txt || exit 1;

# Add silences, noises etc. to the lexicon 
( echo '!sil sil'; echo '[vocalized-noise] spn'; echo '[noise] nsn'; \
  echo '[laughter] lau'; echo '<UNK> spn' ) | cat - $dir/lexicon0.txt | sort -u > $dir/lexicon1.txt || exit 1;

# Remove unk symbol from existing lexiconp.txt
sed '/<UNK>*/d' $dir/lexiconp.txt > $dir/lexiconp0.txt || exit 1;

# Add silences, noises etc. to the lexicon with multiple pronunciations
( echo '!sil 1.0    sil'; echo '[vocalized-noise] 1.0   spn'; echo '[noise] 1.0 nsn'; \
 echo '[laughter] 1.0  lau'; echo '<UNK> 1.0   spn' )  | cat - $dir/lexiconp0.txt | sort -u > $dir/lexiconp1.txt || exit 1;

mv -f $dir/lexicon1.txt $dir/lexicon.txt
# mv -f $dir/lexiconp1.txt $dir/lexiconp.txt
