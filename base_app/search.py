import requests
from dataclasses import dataclass, field
from typing import List
from django.conf import settings
import json
from django.core.cache import cache


@dataclass
class Entry:
    content: List[str] = field(default_factory=list)
    synonyms: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)


@dataclass
class Pronunciation:
    transcription: str = ''
    dialects: str = ''


@dataclass
class EntriesGroup:
    # Group of Entries by part of speech.
    word: str = ''
    part_of_speech: str = ''
    pronunciations: List[Pronunciation] = field(default_factory=list)
    entries: List[Entry] = field(default_factory=list)


@dataclass
class Article:
    word: str = ''
    dictionary: str = ''
    groups: List[EntriesGroup] = field(default_factory=list)


class YandexDictionary:

    def search(self, word):
        result = None
        if word:
            word = word.lower()
            url_ya = settings.YANDEX_API_URL
            params_ya = {'key': settings.YANDEX_API_KEY, 'lang': 'en-ru', 'text': word}
            cached = cache.get('yandex:'+word)
            if cached is None:
                req = requests.get(url_ya, params=params_ya)
                # result['yandex_code'] = req.status_code
                if req.status_code == 200:
                    cache.add('yandex:'+word, req.json(), timeout=None)
                    result = self.yandex_json_parser(req.json(), word)
            else:
                result = self.yandex_json_parser(cached, word)
        return result

    @staticmethod
    def yandex_json_parser(yandex_json, word):
        # Takes a yandex json as a dict and return an Article object.
        result = Article()
        dict_entries = yandex_json.get('def', [])
        result.dictionary = 'Yandex dictionary'
        result.word = word
        for dict_entry in dict_entries:
            group = EntriesGroup()
            group.word = dict_entry.get('text')
            group.part_of_speech = dict_entry.get('pos')
            if dict_entry.get('ts'):
                group.pronunciations.append(Pronunciation(transcription=dict_entry.get('ts')))
            for translation in dict_entry.get('tr', []):
                e = Entry()
                e.content.append(translation.get('text'))
                e.synonyms = [x.get('text') for x in translation.get('mean', [])]
                e.examples = [x.get('text') for x in translation.get('ex', [])]
                group.entries.append(e)
            result.groups.append(group)
        return result


class OxfordDictionary:

    def search(self, word=None):
        result = None
        if word:
            word = word.lower()
            url_oxford = '{base_url}{endpoint}/{language_code}/{word}'
            oxford_endpoint = 'entries'
            language_code = 'en-us'

            url_oxford = url_oxford.format(
                base_url=settings.OXFORD_API_URL,
                endpoint=oxford_endpoint,
                language_code=language_code,
                word=word
            )
            cached = cache.get('oxford:'+word)
            if cached is None:
                req = requests.get(url_oxford, headers={'app_id': settings.OXFORD_APP_ID, 'app_key': settings.OXFORD_APP_KEY})
                #result['oxford_code'] = req.status_code
                if req.status_code == 200:
                    cache.add('oxford:'+word, req.json(), timeout=None)
                    result = self.oxford_json_parser(req.json())
            else:
                result = self.oxford_json_parser(cached)
        return result

    @staticmethod
    def oxford_json_parser(oxford_json):
        # Takes an oxford json as a dict and return an Article object.
        result = Article()
        result.word = oxford_json.get('id')
        result.dictionary = 'Oxford Dictionary'
        for item in oxford_json.get('results', []):
            for lex_entry in item.get('lexicalEntries', []):
                group = EntriesGroup()
                pronunciations = lex_entry.get('pronunciations', [])
                for pronunciation in pronunciations:
                    dialects = ', '.join(pronunciation.get('dialects', []))
                    transcription = pronunciation.get('phoneticSpelling')
                    p = Pronunciation(transcription, dialects)
                    group.pronunciations.append(p)
                group.word = lex_entry.get('text')
                if lex_entry.get('lexicalCategory'):
                    group.part_of_speech = lex_entry.get('lexicalCategory').get('text')
                for entry in lex_entry.get('entries', []):
                    for sense in entry.get('senses', []):
                        e = Entry()
                        e.content = sense.get('definitions')
                        for example in sense.get('examples', []):
                            e.examples.append(example.get('text'))
                        group.entries.append(e)
                    for pronunciation in entry.get('pronunciations', []):
                        dialects = ', '.join(pronunciation.get('dialects'))
                        transcription = pronunciation.get('phoneticSpelling')
                        p = Pronunciation(transcription, dialects)
                        group.pronunciations.append(p)
                result.groups.append(group)
        return result

