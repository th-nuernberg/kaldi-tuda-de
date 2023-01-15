#!/bin/bash

exp=exp/chain_cleaned/tdnn1f_no_ivec_2048_specaug_sp_bi
output_dir=mod9


if [ -d "$output_dir" ]; then
  echo "Output directory ${output_dir} already exists. Please delete or move it."
  exit 1
fi

mkdir -p $output_dir
mkdir -p $output_dir/am
mkdir -p $output_dir/conf
mkdir -p $output_dir/graph
mkdir -p $output_dir/graph/phones

# Required files
cp $exp/final.mdl $output_dir/am || exit 1
cp $exp/graph/HCLG.fst $output_dir/graph || exit 1
gzip $output_dir/graph/HCLG.fst
cp $exp/graph/words.txt $output_dir/graph || exit 1
cp $exp/graph/phones/word_boundary.int $output_dir/graph/phones || exit 1
cp conf/mfcc_hires.conf $output_dir/conf/mfcc.conf || exit 1

# Optional files
cp $exp/tree $output_dir/am 
cp $exp/graph/phones.txt $output_dir/graph

cat <<EOF > $output_dir/conf/model.conf
# Original file was converted from const to vector FST type and then compressed.
--graph=graph/HCLG.fst.gz

# The options below are not Kaldi defaults, and explicitly specified to hide ASR Engine warnings.
--acoustic-scale=1.0
--frame-subsampling-factor=3

# These are default model file paths, explicitly specified for cleaner ASR Engine logging.
--metadata=metadata.json
--am=am/final.mdl
--word-boundary=graph/phones/word_boundary.int
--words=graph/words.txt
--feature-type=mfcc
--mfcc-config=conf/mfcc.conf
#--ivector-extraction-config=ivector/ivector.conf
--phones=graph/phones.txt
--tree=am/tree

# These options would otherwise be inferred from the "usb" silence phone in graph/phones.txt.
--endpoint.silence-phones=1:2:3:4:5
--sip-phones=1:2:3:4:5
--ivector-silence-weighting.silence-phones=1:2:3:4:5

EOF

md5_am=($(md5sum $output_dir/am/final.mdl))
md5_graph=($(md5sum $output_dir/graph/HCLG.fst.gz))

cat <<EOF > $output_dir/metadata.json
{
  "date": "220115",
  "description": "Robust German ASR model trained on SWC, M_AILABS, Tuda-De, CommonVoice V9 (2022-04-27). The vocabulary size is approximately 900k words. To increase noise robustness, SpecAugment layers were added to the AM architecture and the training data was augmented using MUSAN + RIRs noises. The model does not use iVectors. See https://github.com/uhh-lt/kaldi-tuda-de for further details.",
  "language": "de",
  "license": "Apache 2.0",
  "md5": {
    "am": "$md5_am",
    "graph": "$md5_graph"
  }
}

EOF

