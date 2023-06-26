#!/usr/bin/env python3

from tqdm import tqdm
import pandas as pd
import sys, re
import os, shutil
from os import path
import wget
import zipfile


def get_lang_and_pairs_codes(path_code):
    '''
    Converting language names to language codes, 
    collecting a dict in a format "lang to pair"
    '''
    with open(os.path.join(path_code, 'data', 'input_langs.txt'),
              'r', encoding='utf-8') as f:
        langs_words = f.read().strip().split('\n')
        
    with open(os.path.join(path_code, 'data', 'codes_to_langs.txt'), 
              'r', encoding='utf-8') as f:
        langs_codes = f.read().strip().split('\n')
        codes = {}
        for el in langs_codes:
            codes[el.split('\t')[0]] = el.split('\t')[1] 
    
    langs = []
    for lang in langs_words:
        if lang in codes.keys():
            langs.append(codes[lang])
        else:
            print(lang, 'is incorrect language name')
            return False
        
    lang_2 = langs[0]
    
    with open(os.path.join(path_code, 'data', 'pairs_codes.tsv'), 
                           'r', encoding='utf-8') as f:
        pairs = f.read().strip().split()
    
    lang_pair = {}
    for lang in langs:
        for pair in pairs:
            parts = pair.split('-')
            if lang in parts:
                lang_pair[lang] = pair
    return lang_pair, lang_2

def download(pivot, pairs, path_code, path_corp):
    '''
    Downloading zipfiles from OPUS
    '''
    with open(os.path.join(path_code, 'data', 'langs_links.csv'),
                           'r', encoding='utf-8') as f:
        raw_links = f.readlines()
    
    pairs_links = []
    for pair in pairs:
        for el in raw_links:
            if el.startswith(pair):
                pairs_links.append((pair, el.split('\t')[1]))

    for i in range(len(pairs_links)):
        print('\n' + pairs_links[i][0])
        wget.download(pairs_links[i][1], out = os.path.join(path_corp, 'zipFiles', pairs_links[i][0] + '.zip'))
    return pairs_links
    
def unzip_save(pairs, path_code, path_corp):
    '''
    Unzipping and saving files from OPUS
    '''
    for pair in pairs:
        print(pair)
        with zipfile.ZipFile(os.path.join(path_corp, 'zipFiles', pair + '.zip')) as zip_ref:
            zip_ref.extractall(os.path.join(path_corp, 'filesForCorpus', pair))

def prepare_raw_files(fname, outname, langs):
    '''
    Converting friles from OPUS into csv format
    '''
    if len(langs) < 2:
        print('NO LANGS')
        return

    with open(fname, 'r', encoding='utf-8') as f:
        raw = f.readline()
        
    if len(raw.split('\t')) == 6 and 'film' in raw:
        print('\tFILE HAVE ALREADY BEEN PROCESSED')
    else:
        with open(fname, 'r', encoding='utf-8') as f:
            raw = f.read()
            
        for lang in langs:
            raw = raw.replace(lang + '/', lang+'\t')
        first_line = raw.split('\n')[0].split('\t')
        
        if first_line[0] == langs[0]:
            src = langs[0]
            tgt = langs[1]
        else:
            src = langs[1]
            tgt = langs[0]

        header = [src, 
                  src + 'film', 
                  tgt, 
                  tgt+'film',
                  src + 'sub',
                  tgt + 'sub']
        with open(fname, 'w', encoding='utf-8') as f:
            f.write('\t'.join(header) + '\n' + raw)

def merge_to_total(total, fname, pivot, lang):
    '''
    Merging alignments
    '''
    newlang = pd.read_csv(fname, delimiter='\t')
    newlang = newlang[[pivot + 'film', pivot + 'sub', lang + 'sub']]
    
    total = total.merge(newlang, how='inner', on=[pivot + 'film', 
                                               pivot + 'sub'])
    return total

def find_file_indexes(path, pivot, lang, path_code):
    '''
    Extracting alignment indexes for language
    '''
    total = pd.read_csv(os.path.join(path_code, 'data', 'total_merges.csv'), delimiter='\t')
    filenames = os.listdir(path)
    fname = ''
    for f in filenames:
        if f.endswith('.ids'):
            fname += f
    pdlang = pd.read_csv(path + fname, delimiter='\t')
    pdlang['ID'] = pd.DataFrame(list(range(len(pdlang))), dtype='int64')

    pdlang = pdlang[[pivot + 'film', lang+'sub','ID']]
    total = total[[pivot + 'film', lang+'sub']]

    indexes = pdlang.merge(total, how='inner', on=[pivot + 'film', lang + 'sub'])
    indexes['ID'].to_csv(os.path.join(path,'idexes_'+lang + '.txt'))
    return indexes

def make_corpus_part(indexes, path, lang, path_corp, mode=''):
    '''
    Compiling translations for language
    '''
    fnames = os.listdir(path)

    for name in fnames:
        if name.endswith(lang):
            langfname = '' + name
    
    f = open(os.path.join(path, langfname), 'r', encoding='utf-8')
    lines = f.readlines()
    
    fout = open(os.path.join(path_corp, 'multisubscorpus', lang + '.txt'), 'w', encoding='utf-8')
    
    text = ''
    for i in tqdm(indexes):
        text += lines[i]
    fout.write(text)
    f.close()
    fout.close()
    
if __name__ == '__main__':
    pivot = 'en'
    
    path_code = os.getcwd()
    path_corp = os.path.split(os.getcwd())[0]
    corpuspath = os.path.join(path_corp, 'multisubscorpus', '')
    
    if not path.exists(os.path.join(path_corp, 'filesForCorpus','')):
        os.mkdir(os.path.join(path_corp, 'filesForCorpus',''))
        
    dirname = os.path.join(path_corp, 'filesForCorpus','')
    
    print('Get languages codes...')
    if get_lang_and_pairs_codes(path_code) is False:
        sys.exit()
    
    lang_pair, lang_2 = get_lang_and_pairs_codes(path_code)
    
    print('\nChecking for source files...')
    if not path.exists(os.path.join(path_corp, 'zipFiles', '')):
        os.mkdir(os.path.join(path_corp, 'zipFiles', ''))
    
    not_downloaded = []
    for pair in lang_pair.values():
        if not path.exists(os.path.join(path_corp, 'zipFiles', pair + '.zip')):
            not_downloaded.append(pair)

    if not_downloaded != []: 
        print('\nSome zip-files have not been downloaded yet')
        print('Start downloading files...')
        pairs_links = download(pivot, not_downloaded, path_code, path_corp)
        print('\nUnzipping files...')
        unzip_save(not_downloaded, path_code, path_corp)
    else:
        print('\tNo need to download files')
    
    print('\nPreparing files with ids...')
    for lang in lang_pair:
        pair = lang_pair[lang]
        print('Processing ' + pair + ' pair...')
        prepare_raw_files(os.path.join(dirname, pair, 'OpenSubtitles.'+ pair + '.ids'), 
                          os.path.join(dirname, pair, 'OpenSubtitles.'+ pair + '.ids'), [lang, pivot])
    
    print('\nStart merging...')
    total = pd.read_csv(os.path.join(dirname, lang_pair[lang_2], 'OpenSubtitles.'+ lang_pair[lang_2] + '.ids'), delimiter='\t')
    
    total = total[[pivot + 'film', 
                   pivot + 'sub', 
                   lang_2 + 'sub']]

    collect = True
    for lang in lang_pair:
        print(lang)
        pair = lang_pair[lang]
        if lang != lang_2:
            filenames = os.listdir(os.path.join(dirname, pair))
            fname = os.path.join(dirname, pair, 'OpenSubtitles.'+ pair + '.ids')
            
            total = merge_to_total(total, fname, pivot, lang)
            
            if total.shape[0] == 0:
                print('Not enough language data to collect the corpus')
                collect = False
                break
            
    total.to_csv(os.path.join(path_code, 'data', 'total_merges.csv'), sep='\t')
    print('TOTAL')
    print(total.shape[0], 'translational units')
    
    if collect:
        print('\nStart collecting corpus...')
        if not path.exists(corpuspath):
            os.mkdir(corpuspath)
        elif path.exists(corpuspath): 
            shutil.rmtree(corpuspath)
            os.mkdir(corpuspath)
        

        indexes = find_file_indexes(os.path.join(dirname, lang_pair[lang_2], ''), pivot, pivot, path_code)
        indexes = list(indexes['ID'])
        make_corpus_part(indexes, os.path.join(dirname, lang_pair[lang_2], ''), pivot, path_corp)
        
        for lang in lang_pair:
            print(lang)
            pair = lang_pair[lang]
            
            indexes = find_file_indexes(os.path.join(dirname, pair, ''), pivot, lang, path_code)
            indexes = list(indexes['ID'])
            make_corpus_part(indexes, os.path.join(dirname, pair), lang, path_corp)
