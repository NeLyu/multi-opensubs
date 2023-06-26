# multi-opensubs
Multilingual parallel corpus based on OPUS Opensubtitles and a corpus compiler
# GENERAL INFO
### MultiOpenSubs Corpus
The corpus is based on the data from OPUS OpenSubtitles (https://opus.nlpl.eu/OpenSubtitles-v2018.php), I used the data from OPUS with Jörg Tiedemann's consent.
It is created mainly for comparative linguistic research purposes.

**MultiOpenSubs** consists of two subcorpora: **Multisubs_euro** which contains texts only in European languages, and **Multisubs_misc** which also contains languages other than European.

1) **Multisubs_euro** contains texts in **14 languages**: Bulgarian, Czech, Dutch, English, French, German, Greek, Italian, Polish, Portuguese, Romanian, Russian, Serbian, Spanish.
It contains 109000 translation units and about 790000 tokens.

2) **Multisubs_misc** contains texts **also in 14 languages**: Arabic, English, French, Finnish, German, Greek, Hungarian, Italian, Polish, Portuguese, Russian, Serbian, Spanish, Turkish.
The fact that both corpora contain text 14 languages is a coincidence.
It contains 92000 translation units and about 680000 tokens. 

Sentence alignment was adopted from OPUS.

The main difference of this corpus from OPUS OpenSubtitles is that in both subcorpora each translational unit contains translations in all 14 languages. OPUS OpenSubtitles original collection contains 60 languages, but parallel texts do not always match with each other and the amoun of data per language varies greatly. Creating the corpus I had two main goals: 1) to avoid inconsistency in the data 2) to include as many languages as possible. By inconsistency I mean a situation when different language pairs in a parallel corpus have different amounts of data, e.g. English-German part has 100K pairs, English-French part has 70K pair, French-German part has 150K pairs and so on. One can use such data in comparative linguistic research but it needs to be unified and non-matching translational units should be filtered. The more languages the original collection contains the harder to do this.

The number of languages included in MultiSubs was determined by the amount of matching translations between translational pairs in the original collection. OPUS OpenSubtitles include numerous language pairs with gigabytes of data but the fact is that there are fewer of them matching together and this is quite common for many multilingual collections. Therefore we have to balance between the desired number of languages and the amount of data we end up with.

### MultiCompiler Script
The script MultiCompiler allows you to **create a corpus including languages you have chosen yourself (from 60 possible languages)**. When using the script you should take into account the following issue: the more languages you choose the less translational units your corpus contains, the less languages you choose the bigger is your corpus. This depends on the number of matching translations in the original collection.
English was used as a pivot language for corpus compiling. This means that the script takes as input language pairs with English and based on the matches in English compiles the corpus.


# REQUIREMENTS

In order to use MultiCompiler you need to have the following packages installed:
```
tqdm, pandas, wget, zipfile
```
You also need to have not less than 10Gb of RAM, because MultiCompiler processes large files.

# USAGE INSTRUCTIONS
As input uses the file `./Code/data/input_langs.txt`, it should contain language names in a format one name per line.

When you have a language list prepared you can run the script.

```
python3 collect_corpus.py
```

As the main output you get the multisubscorpus directory, it contains files with aligned texts, that's why all files have the same number of lines.
You will also get zipFiles and fileForCorpus folders, they contain data from OPUS that the script downloads.

# CONTACT
If you have any questions or suggestions don't hesitate to contact me.

Liubov Nesterenko - lyu.klimenchenko@gmail.com, Telegram @nestliu
