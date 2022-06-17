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
from pathlib import Path
import common_utils
import german_asr_lm_tools.normalize_sentences as normalize_sentences
import spacy
import os


wav_scp_template = "sox $filepath -t wav -r 16k -b 16 -e signed - |"

def process(corpus_path, input_directory, output_datadir):
    common_utils.make_sure_path_exists(output_datadir)
    nlp = spacy.load('de_core_news_lg')

    corpus_path = Path(corpus_path)
    # Multilingual LibriSpeech (MLS) might have repetitions so we normalize it again
    # we cache text normalizations since they can be slow
    normalize_cache = {}

    # we first load the entire corpus text into memory, sort by ID and then write it out into Kaldis data_dir format
    corpus = {}
    # All speaker2gender
    s2g_all = {}

    print('Loading', str(corpus_path  / 'metainfo.txt'))
    with open(corpus_path / 'metainfo.txt') as metainfo_in:
        # Skip first line which contains the header of the metainfo file
        itermetainfo_in = iter(metainfo_in)
        next(itermetainfo_in)
        # Iterate over tsv file by line
        for line in itermetainfo_in:
            split = line.split('|')
            # speaker id
            spk = 'mls' + split[0].strip()
            # gender
            gndr = split[1].strip().lower()
            if s2g_all.get(spk) is None:
                s2g_all[spk] = gndr
            else:
                if s2g_all[spk] != gndr:
                    print(f'Error: Speaker {spk} has two genders in the dataset!')
                    print('Gender1:', s2g_all[spk])
                    print('Gender2:', gndr)
    print('done loading metainfo.txt!')
    print("Number of speakers in corpus: %d" % len(s2g_all))
    print('Loading', corpus_path / input_directory / 'transcripts.txt')
    with open(corpus_path / input_directory / 'transcripts.txt') as corpus_path_in:
        # Skip first line which contains the header of the tsv file
        itercorpus_path_in = iter(corpus_path_in)
        next(itercorpus_path_in)
        # Iterate over tsv file by line
        for line in itercorpus_path_in:
            split = line.split('\t')
            # print(split)

            # id: 10870_10823_000001
            utt_id = split[0]
            # text
            text = split[1]

            meta = utt_id.split('_')
            # speaker_id with prefix: mls-10870
            spk = 'mls' + meta[0]
            # audio/[speaker_id]/[book_id]/[id].flac
            # audio/10870/10823/10870_10823_000001.flac
            filename = "audio/" + meta[0] + '/' + meta[1] + '/' + utt_id + '.flac'
            if text not in normalize_cache:
                normalized_text = normalize_sentences.normalize(nlp, text)
                normalize_cache[text] = normalized_text
            else:
                normalized_text = normalize_cache[text]

            # print(utt_id, text, spk, filename)

            # Validate that the file really exists
            full_file_path = corpus_path / input_directory / filename
            if full_file_path.is_file():
                # Add file to output structure
                corpus[utt_id] = (filename, normalized_text, spk)
            else:
                print("File does not exist! Skipping " + full_file_path)
                print("Metadata: ", utt_id, filename, normalized_text, spk)

    print('done loading {}'.format(corpus_path / input_directory / 'transcripts.txt'))
    print('Now writing out to', output_datadir,'in Kaldi format!')
    # Speaker2Gender in subset, e.g. train, dev, test
    s2g = {}
    with open(output_datadir + 'wav.scp', 'w') as wav_scp, open(output_datadir + 'utt2spk', 'w') as utt2spk, open(output_datadir + 'text', 'w') as text_out:
        for utt_id in sorted(corpus.keys()):

            filename, normalized_text, spk = corpus[utt_id]
            # Note: Speaker IDs must be a prefix of the utterance. 
            # This is necessary for sorting utt2spk and spk2utt (see https://kaldi-asr.org/doc/data_prep.html)
            # add speaker id as prefix to utterance, so we get proper sorting
            fullid = spk + '-' + utt_id

            wav_scp.write(fullid + ' ' + wav_scp_template.replace("$filepath", str(corpus_path / input_directory / filename)) + '\n')
            utt2spk.write(fullid + ' ' + spk + '\n')
            text_out.write(fullid + ' ' + normalized_text + '\n')
            s2g[spk] = s2g_all[spk]
    print("Number of speakers in corpus subset " + input_directory + ": %d" % len (s2g))
    #with open(output_datadir + 'spk2gender', 'w') as spk2gender:
    #    for spk in sorted(s2g.keys()):
    #        spk2gender.write(spk + ' ' + s2g[spk] + '\n')

    print('done!')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Prepares the files from the Multilingual LibriSpeech (MLS) corpus for KALDI')
    parser.add_argument('-c', '--corpus-path', dest='corpus_path', help='path to the corpus data', default='data/wav/mls/', type=str)
    parser.add_argument('-d', '--dir', dest='directory', help='Directory for the corpus processing data', default='train', type=str)
    parser.add_argument('-o', '--output-datadir', dest='output_datadir', help='lexicon out file', type=str, default='data/mls_train/')

    args = parser.parse_args()

    process(args.corpus_path, args.directory, args.output_datadir)
