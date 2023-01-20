#!/bin/bash

# (c) 2014 Korbinian Riedhammer

# This script is based on s5/utils/prepare_lang.sh.  Based on a data/lang
# directory, generate a new L transducer with the new lexicon.
# Make sure to use the same phone options as used to generate data/lang.

if [ -f path.sh ]; then
      . path.sh; else
      echo "missing path.sh"; exit 1;
fi

sil_prob=0.5
# thn silphone from phones.txt
silphone=sil
thn_dir=data/lang_std_big_v6_test
unihh_dir=data/lang_std_big_v6_unihh_test
lexdir=/nfs/scratch/staff/wagnerdo/unihh_kaldi_model_files/de_900k_nnet3chain_tdnn1f_2048_sp_bi/phones
# lexdir=data/local/dict_std_big_v6
outdir=lfst_rebuild


mkdir -p $outdir

ndisambig=`utils/add_lex_disambig.pl $lexdir/lexicon.txt $outdir/lexicon_disambig.txt`
echo "Number of disambiguation symbols: $ndisambig"
# and produce $tmpdir/lexicon_disambig.txt
# --pron-probs $tmpdir/lexiconp.txt
#ndisambig=`utils/add_lex_disambig.pl $tmpdir/lexiconp_disambig.txt`
#ndisambig=$[$ndisambig+1]; # add one disambig symbol for silence in lexicon FST.
#echo $ndisambig > $tmpdir/lex_ndisambig

# Format of lexiconp_disambig.txt:
# !SIL	1.0   SIL_S
# <SPOKEN_NOISE>	1.0   SPN_S #1
# <UNK>	1.0  SPN_S #2
# <NOISE>	1.0  NSN_S
# !EXCLAMATION-POINT	1.0  EH2_B K_I S_I K_I L_I AH0_I M_I EY1_I SH_I AH0_I N_I P_I OY2_I N_I T_E


# Create the lexicon FST with disambiguation symbols, and put it in lang_test.
# There is an extra step where we create a loop to "pass through" the
# disambiguation symbols from G.fst.
phone_disambig_symbol=`grep \#0 $thn_dir/phones.txt | awk '{print $2}'`
word_disambig_symbol=`grep \#0 $unihh_dir/words.txt | awk '{print $2}'`

echo "Found phone_disambig_symbol=$phone_disambig_symbol and word_disambig_symbol=$word_disambig_symbol"

# Create the basic L.fst without disambiguation symbols, for use
# in training.
# make_lexicon_fst.pl [--pron-probs] lexicon.txt [silprob silphone [sil_disambig_sym]] >lexiconfst.txt
# --pron-probs $tmpdir/lexiconp.txt
utils/make_lexicon_fst.pl $lexdir/lexicon.txt $sil_prob $silphone | \
	fstcompile --isymbols=$thn_dir/phones.txt --osymbols=$unihh_dir/words.txt \
	--keep_isymbols=false --keep_osymbols=false | \
		fstarcsort --sort_type=olabel > $outdir/L.fst || exit 1;

# Create the lexicon FST with disambiguation symbols, and put it in lang_test.
# There is an extra step where we create a loop to "pass through" the
# disambiguation symbols from G.fst.
phone_disambig_symbol=`grep \#0 $thn_dir/phones.txt | awk '{print $2}'`
word_disambig_symbol=`grep \#0 $unihh_dir/words.txt | awk '{print $2}'`
# --pron-probs $tmpdir/lexiconp_disambig.txt
utils/make_lexicon_fst.pl $outdir/lexicon_disambig.txt $sil_prob $silphone '#'$ndisambig | \
   fstcompile --isymbols=$thn_dir/phones.txt --osymbols=$unihh_dir/words.txt \
   --keep_isymbols=false --keep_osymbols=false |   \
   fstaddselfloops  "echo $phone_disambig_symbol |" "echo $word_disambig_symbol |" | \
   fstarcsort --sort_type=olabel > $outdir/L_disambig.fst || exit 1;

echo "Finished"
exit 0
