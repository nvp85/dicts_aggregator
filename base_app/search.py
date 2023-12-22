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
                if req.status_code == 200 and req.json().get('def', False):
                    data = req.json()
                    cache.add('yandex:'+word, data, timeout=None)
                    result = self.yandex_json_parser(data, word)
                else:
                    err_msgs = {
                        200: "No entry found.",
                        401: "Invalid API key.",
                        402: "This API key has been blocked.",
                        403: "Exceeded the daily limit on the number of requests.",
                        413: "The text size exceeds the maximum."
                    }
                    result = {}
                    result['dictionary'] = 'The Yandex Dictionary'
                    result['word'] = word
                    result['error'] = err_msgs.get(req.status_code, 'Sorry! The Yandex API is currently unavailable.')
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
                data = req.json()
                #result['oxford_code'] = req.status_code
                if req.status_code == 200:
                    cache.add('oxford:'+word, data, timeout=None)
                    result = self.oxford_json_parser(data)
                else:
                    result = {}
                    result['dictionary'] = 'The Oxford Dictionary'
                    result['word'] = word
                    result['error'] = data.get('error', "Sorry! The Oxford API is currently unavailable.")
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
                        e.synonyms = [syn['text'] for syn in sense.get('synonyms',[])]
                        if e.content is not None:
                            group.entries.append(e)
                    for pronunciation in entry.get('pronunciations', []):
                        dialects = ', '.join(pronunciation.get('dialects'))
                        transcription = pronunciation.get('phoneticSpelling')
                        p = Pronunciation(transcription, dialects)
                        group.pronunciations.append(p)
                result.groups.append(group)
        return result

class FreeDictionary:

    def search(self, word=None):
        result = None
        if word:
            word = word.lower()
            url_free_dict = '{base_url}{endpoint}/{language_code}/{word}'
            endpoint = 'entries'
            language_code = 'en'

            url_free_dict = url_free_dict.format(
                base_url=settings.FREEDICT_API_URL,
                endpoint=endpoint,
                language_code=language_code,
                word=word
            )
            cached = cache.get('free_dict:'+word)
            if cached is None:
                req = requests.get(url_free_dict)
                data = req.json()
                
                if req.status_code == 200:
                    cache.add('free_dict:'+word, data, timeout=None)
                    result = self.free_dict_json_parser(data, word)
                else:
                    result = {}
                    result['dictionary'] = 'The Free Dictionary'
                    result['word'] = word
                    result['error'] = data.get('title', "Sorry! The API is currently unavailable.")
            else:
                result = self.free_dict_json_parser(cached, word)
        return result
    
    @staticmethod
    def free_dict_json_parser(free_dict_json, word):
        # Takes a free dictionary json as a dict and return an Article object.
        result = Article()
        result.word = word
        result.dictionary = 'Free Dictionary'
        for item in free_dict_json:
            group_word = item.get('word')
            group_pronunciations = []
            for pronunciation in item.get('phonetics',[]):
                transcription = pronunciation.get('text')
                if transcription is not None:
                    p = Pronunciation(transcription=transcription)
                    group_pronunciations.append(p)
            for entry_group in item.get('meanings', []):
                group = EntriesGroup()
                group.word = group_word
                group.pronunciations = group_pronunciations
                group.part_of_speech = entry_group.get('partOfSpeech','')
                for definition in entry_group.get('definitions', []):
                    e = Entry()
                    e.content = [definition.get('definition')]
                    if definition.get('example'):
                        e.examples.append(definition.get('example'))
                    e.synonyms = definition.get('synonyms',[])
                    if e.content is not None:
                        group.entries.append(e)
                result.groups.append(group)
        return result
    
def search(word, dicts):
    result = {'success': False, 'result':[]}
    func = {
    'Yandex': YandexDictionary,
    'Oxford': OxfordDictionary,
    'free_dict': FreeDictionary,
    }
    for dict in dicts:
        dict_result = func[dict]().search(word)
        if isinstance(dict_result, Article):
            result['success'] = True
        result['result'].append(dict_result)
    return result