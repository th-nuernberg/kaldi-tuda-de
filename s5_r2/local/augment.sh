#!/bin/bash
# In this script, we augment the training data with reverberation,
# noise, music, and babble, and combine it with the clean data.

. ./path.sh

reverb_data_dir=data/train_reverb
musan_root=data
musan_output=data
sample_rate=16000

. utils/parse_options.sh

if [ $# != 2 ]; then
    echo "Usage: $0 <train_data_dir> <augment_data_dir>"
    exit 1;
fi

train_data_dir=$1
augment_data_dir=$2


frame_shift=0.01
awk -v frame_shift=$frame_shift '{print $1, $2*frame_shift;}' $train_data_dir/utt2num_frames > $train_data_dir/reco2dur

if [ ! -d "RIRS_NOISES" ]; then
  # Download the package that includes the real RIRs, simulated RIRs, isotropic noises and point-source noises
  wget --no-check-certificate http://www.openslr.org/resources/28/rirs_noises.zip -O /tmp/rirs_noises.zip
  unzip /tmp/rirs_noises.zip
fi

# Make a version with reverberated speech
rvb_opts=()
rvb_opts+=(--rir-set-parameters "0.5, RIRS_NOISES/simulated_rirs/smallroom/rir_list")
rvb_opts+=(--rir-set-parameters "0.5, RIRS_NOISES/simulated_rirs/mediumroom/rir_list")

# Make a reverberated version of the VoxCeleb2 list.  Note that we don't add any
# additive noise here.
local/reverberate_data_dir.py \
  "${rvb_opts[@]}" \
  --speech-rvb-probability 1 \
  --pointsource-noise-addition-probability 0 \
  --isotropic-noise-addition-probability 0 \
  --num-replications 1 \
  --source-sampling-rate $sample_rate \
  $train_data_dir $reverb_data_dir || exit 1

cp $train_data_dir/vad.scp $reverb_data_dir/
utils/copy_data_dir.sh --utt-suffix "-reverb" $reverb_data_dir ${reverb_data_dir}.new
rm -rf $reverb_data_dir
mv ${reverb_data_dir}.new $reverb_data_dir

# Prepare the MUSAN corpus, which consists of music, speech, and noise
# suitable for augmentation.
steps/data/make_musan.sh --sampling-rate $sample_rate $musan_root $musan_output

# Get the duration of the MUSAN recordings.  This will be used by the
# script augment_data_dir.py.
for name in speech noise music; do
  utils/data/get_utt2dur.sh $musan_output/musan_${name}
  mv $musan_output/musan_${name}/utt2dur $musan_output/musan_${name}/reco2dur
done

# Augment with musan_noise
local/augment_data_dir.py --utt-suffix "noise" --fg-interval 1 --fg-snrs "15:10:5:0" --num-bg-noises "1" --fg-noise-dir "${musan_output}/musan_noise" $train_data_dir $augment_data_dir/train_noise || exit 1
# Augment with musan_music
local/augment_data_dir.py --utt-suffix "music" --bg-snrs "15:10:8:5" --num-bg-noises "1" --bg-noise-dir "${musan_output}/musan_music" $train_data_dir $augment_data_dir/train_music || exit 1
# Augment with musan_speech
local/augment_data_dir.py --utt-suffix "babble" --bg-snrs "20:17:15:13" --num-bg-noises "3:4:5:6:7" --bg-noise-dir "${musan_output}/musan_speech" $train_data_dir $augment_data_dir/train_babble || exit 1

# Combine reverb, noise, music, and babble into one directory.
utils/combine_data.sh $augment_data_dir/train_aug $reverb_data_dir $augment_data_dir/train_noise $augment_data_dir/train_music $augment_data_dir/train_babble
echo "$0: Data augmentation finished. Results: " $augment_data_dir/train_aug

exit 0