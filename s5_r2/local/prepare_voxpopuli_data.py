# -*- coding: utf-8 -*-

# Copyright 2019 Language Technology, Universitaet Hamburg (author: Benjamin Milde)
# Copyright 2022 Informatik, Technische Hochschule Nuernberg (author: Thomas Ranzenberger)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import common_utils
import german_asr_lm_tools.normalize_sentences as normalize_sentences
import spacy
import os
from pathlib import Path


wav_scp_template = "sox $filepath -t wav -r 16k -b 16 -e signed - |"

def process(corpus_path, input_filename, language, output_datadir):
    common_utils.make_sure_path_exists(output_datadir)
    nlp = spacy.load('de_core_news_lg')

    # VoxPopuli might have repetitions so we normalize it again
    # we cache text normalizations since they can be slow
    normalize_cache = {}

    # we first load the entire corpus text into memory, sort by ID and then write it out into Kaldis data_dir format
    corpus = {}
    # speaker2gender
    #s2g = {}

    input_corpus_path = Path(corpus_path) / 'transcribed_data' / language / input_filename
    if not input_corpus_path.exists():
        raise FileNotFoundError(f'Corpus path {input_corpus_path} not found!')
    print('Loading', input_corpus_path)
    with open(input_corpus_path) as corpus_path_in:
        # Skip first line which contains the header of the tsv file
        itercorpus_path_in = iter(corpus_path_in)
        next(itercorpus_path_in)
        # Iterate over tsv file by line
        for line in itercorpus_path_in:
            split = line.split('\t')
            # print(split)
            utt_id = split[0]
            # normalized_text
            text = split[2]
            # speaker_id with prefix
            spk = 'vp' + split[3]
            # gender
            gndr = split[5].replace("male", "m").replace("female", "f").replace("fem", "f")
            # 2018
            subfolder = utt_id[0:4]
            # 2018/20180313-0900-PLENARY-16-de_20180313-20:08:11_1.ogg
            filename = subfolder + '/' + utt_id + '.ogg'
            if text not in normalize_cache:
                normalized_text = normalize_sentences.normalize(nlp, text)
                normalize_cache[text] = normalized_text
            else:
                normalized_text = normalize_cache[text]

            # print(utt_id, filename, normalized_text, spk, gndr)

            # Validate that the file really exists
            full_file_path = Path(corpus_path)  / 'transcribed_data' / language / filename
            if full_file_path.is_file():
                # Add file to output structure
                corpus[utt_id] = (filename, normalized_text, spk)
                #if s2g.get(spk) == None:
                #    s2g[spk] = gndr
                #else:
                #    if s2g[spk] != gndr:
                #        print('Error: Speaker ' + spk + ' has two genders in the dataset!')
                #        print(s2g[spk])
                #        print(gndr)
            else:
                print("File does not exist! Skipping " + full_file_path)
                print("Metadata: ", utt_id, filename, normalized_text, spk, gndr)

    print('done loading ' + input_filename + '!')
    print('Now writing out to', output_datadir,'in Kaldi format!')

    with open(output_datadir + 'wav.scp', 'w') as wav_scp, open(output_datadir + 'utt2spk', 'w') as utt2spk, open(output_datadir + 'text', 'w') as text_out:
        for utt_id in sorted(corpus.keys()):
            filename, normalized_text, spk = corpus[utt_id]
            
            # Note: Speaker IDs must be a prefix of the utterance. 
            # This is necessary for sorting utt2spk and spk2utt (see https://kaldi-asr.org/doc/data_prep.html)
            # add speaker id as prefix to utterance, so we get proper sorting
            fullid = spk + '-' + utt_id

            wav_scp.write(fullid + ' ' + wav_scp_template.replace("$filepath", corpus_path + 'transcribed_data/' + language + '/' + filename) + '\n')
            utt2spk.write(fullid + ' ' + spk + '\n')
            text_out.write(fullid + ' ' + normalized_text + '\n')

    #with open(output_datadir + 'spk2gender', 'w') as spk2gender:
    #    for spk in sorted(s2g.keys()):
    #        spk2gender.write(spk + ' ' + s2g[spk] + '\n')

    print('done!')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Prepares the files from the VoxPopuli corpus for KALDI')
    parser.add_argument('-c', '--corpus-path', dest='corpus_path', help='path to the corpus data', default='data/wav/vp/', type=str)
    parser.add_argument('-f', '--filename', dest='filename', help='filename for the corpus processing data', default='asr_train.tsv', type=str)
    parser.add_argument('-l', '--lang', dest='lang', help='language of the corpus processing data', default='de', type=str)
    parser.add_argument('-o', '--output-datadir', dest='output_datadir', help='lexicon out file', type=str, default='data/voxpopuli_train/')

    args = parser.parse_args()

    process(args.corpus_path, args.filename, args.lang, args.output_datadir)
