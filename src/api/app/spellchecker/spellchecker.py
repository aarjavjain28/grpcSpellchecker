import os
from typing import Optional, Dict, List, Any
import json

#from spellchecker.types import Suggestion
from symspellpy import SymSpell, Verbosity
from dataclasses import dataclass
from pydantic import BaseModel
from typing import Dict, List, Optional


@dataclass
class Suggestion:
    term: str
    distance: int
    count: int
    correct_spelling: bool


class Prediction(BaseModel):
    total_words: int
    well_spelt_words: int
    ratio: float
    suggestions: Dict[str, List[str]]
    supported_language: bool


class Options(BaseModel):
    channel: Optional[str]
    language_code: Optional[str]


def get_banks(dc: str, root_path: str = '../../lib/spellchecker/resources') -> Dict[str, List[str]]:
    with open(f'{root_path}/{dc}_banks.json', 'r') as bank_file:
        banks = json.load(bank_file)
    return banks


class SpellChecker:
    _DEFAULT_FREQ: int = 100000
    __sym_spell_languages: Dict[str, SymSpell]
    __sym_spell_channels_by_lang: Dict[str, Dict[Any, SymSpell]]

    def __init__(self, dictionary_path: str, channel_path: Optional[str] = None, languages: List[str] = []):
        """
        Constructor to initialise the spellchecker dictionary
        :param dictionary_path: Filepath to frequency dictionary in txt form.
        :param channel_path: Filepath to pickled channel specific dictionaries
        If none specified will use default english dictionary
        """
        self.__sym_spell_languages = {}
        self.__sym_spell_channels_by_lang = {}
        if dictionary_path:
            for f in os.listdir(dictionary_path):
                lan = f.split('.')[0]
                if '.txt' in f and (not languages or lan in languages):
                    sc = SymSpell()
                    sc.load_dictionary(os.path.join(dictionary_path, f), 0, 1)
                    self.__sym_spell_languages[lan] = sc
        if channel_path:
            for ln in os.listdir(channel_path):
                channels = {}
                if len(ln) < 3 and (not languages or ln in languages):
                    for f in os.listdir(os.path.join(channel_path, ln)):
                        key = f.split('.')[0]
                        if '.pickle' in f:
                            sc = SymSpell()
                            sc.load_pickle(os.path.join(channel_path, ln, f), compressed=False)
                            channels[key] = sc
                    self.__sym_spell_channels_by_lang[ln] = channels

    def add_valid_word(self, word: str, language: str, freq: int = _DEFAULT_FREQ) -> None:
        """
        Add valid word to frequency dictionary to supply brand names or slang not currently covered by the given
        dictionary. Will pass if word is already present.

        :param word: Word to add to dictionary of all valid words
        :param freq: The frequency for that word if none specified _default freq will be used
        :return:
        """
        sc = self.__sym_spell_languages[language]
        sc.create_dictionary_entry(word, freq)

    def update_valid_word(self, word: str, language: str, freq: int = _DEFAULT_FREQ) -> None:
        """
        Change a valid words frequency to new value in the dictionary. Will pass if word is not already present.

        :param word: Word present in dictionary of all valid words
        :param freq: New frequency of word
        :return:
        """
        if language not in self.__sym_spell_languages:
            return None

        sc = self.__sym_spell_languages[language]
        if len(sc.lookup(word, Verbosity.TOP)) > 0 and \
                sc.lookup(word, verbosity=Verbosity.TOP)[0].distance == 0:
            sc.delete_dictionary_entry(word)
            sc.create_dictionary_entry(word, freq)

    def correct_word(self, word: str, language: str, channel: Optional[str] = None) -> Suggestion:
        """
        Returns top result for corrected spelling algorithm for a single word.

        :param word: word to correct
        :param channel: channel to check against
        :return: Suggest Item with 3 components term (string result), distance (Levensthien Distance),
        count (frequency in english)
        """
        if language in self.__sym_spell_languages:
            sc_l = self.__sym_spell_languages[language]
        else:
            return Suggestion(word, 3, 0, False)

        if self._word_contains_digits(word):
            return Suggestion(word, 0, 0, True)

        res_lang = sc_l.lookup(word, Verbosity.TOP, max_edit_distance=2, transfer_casing=True,
                               include_unknown=True)
        res_lang_blob = sc_l.lookup_compound(word, max_edit_distance=2)

        if res_lang_blob[0].distance < res_lang[0].distance and res_lang_blob[0].count > 0:
            res_lang = res_lang_blob

        if channel in self.__sym_spell_channels_by_lang[language]:
            res_chan = self.__sym_spell_channels_by_lang[language][channel].lookup(word, Verbosity.TOP,
                                                                                   max_edit_distance=2,
                                                                                   transfer_casing=True,
                                                                                   include_unknown=True)

            if res_chan[0].distance <= res_lang[0].distance:
                return Suggestion(res_chan[0].term, res_chan[0].distance, res_chan[0].count, res_chan[0].distance == 0)

        return Suggestion(res_lang[0].term, res_lang[0].distance, res_lang[0].count, res_lang[0].distance == 0)

    def candidates_word(self, word: str, language: str, channel: Optional[str] = None,
                        number_of_candidates: Optional[int] = None) -> \
            List[Suggestion]:
        """
        Returns top n results in the form of List[SuggestItem]
        if n is specified returns list of n closest results in frequency order
        if n is not specified returns a full list of closest results

        :param word: the single wordto correct (str)
        :param channel: channel to check against
        :param number_of_candidates: number of results to return
        :return: List of SuggestItem
        """
        if language in self.__sym_spell_languages:
            sc_l = self.__sym_spell_languages[language]
        else:
            return [Suggestion(word, 3, 0, False)]

        if self._word_contains_digits(word):
            return [Suggestion(word, 0, 0, True)]

        res_lang = sc_l.lookup(word, Verbosity.CLOSEST, max_edit_distance=2, transfer_casing=True,
                               include_unknown=True)
        res_lang_blob = sc_l.lookup_compound(word, max_edit_distance=2)
        if res_lang_blob[0].distance < res_lang[0].distance and res_lang_blob[0].count > 0:
            res_lang = res_lang_blob

        if language not in self.__sym_spell_channels_by_lang or \
                channel not in self.__sym_spell_channels_by_lang[language]:
            final_result = list(
                map(lambda r: Suggestion(r.term, r.distance, r.count, r.distance == 0), res_lang))
            final_result = list(filter(lambda r: r if r.count > 0 else None, final_result))
        else:
            res_chan = self.__sym_spell_channels_by_lang[language][channel].lookup(word, Verbosity.CLOSEST,
                                                                                   max_edit_distance=2,
                                                                                   include_unknown=True,
                                                                                   transfer_casing=True)

            all_results = list(sorted(res_chan + res_lang, key=lambda r: r.distance))
            clean_res = list(filter(lambda r: r if r.count > 0 else None, all_results))
            final_result = list(map(lambda r: Suggestion(r.term, r.distance, r.count, r.distance == 0), clean_res))

        if number_of_candidates:
            return final_result[:number_of_candidates]

        return final_result

    def correct_text_blob(self, text_blob: str, language: str, channel: Optional[str] = None) -> Suggestion:
        """
        Returns top result for corrected spelling algo for a compound of words.

        :param text_blob: sentence to correct
        :param channel: the channel of which products sentence is checked against
        :return:
        """
        if language in self.__sym_spell_languages:
            sc_l = self.__sym_spell_languages[language]
        else:
            return Suggestion(text_blob, 3, 0, False)

        res_lang = sc_l.lookup_compound(text_blob, max_edit_distance=2, transfer_casing=True)

        if res_lang[0].distance == 0 or channel not in self.__sym_spell_channels_by_lang[language]:
            return Suggestion(res_lang[0].term, res_lang[0].distance, res_lang[0].count, res_lang[0].distance == 0)

        channel_words = self.__sym_spell_channels_by_lang[language][channel].words

        for word in channel_words:
            sc_l.create_dictionary_entry(word, channel_words[word])

        res_chan = sc_l.lookup_compound(text_blob, max_edit_distance=2, transfer_casing=True)

        for word in channel_words:
            sc_l.delete_dictionary_entry(word)

        if res_chan[0].distance < res_lang[0].distance:
            return Suggestion(res_chan[0].term, res_chan[0].distance, res_chan[0].count, res_chan[0].distance == 0)
        else:
            return Suggestion(res_lang[0].term, res_lang[0].distance, res_lang[0].count, res_lang == 0)

    def merge_dictionary(self, dictionary: Dict[str, int], language: str, update: bool = False) -> None:
        """
        Merges frequency dictionary into existing dictionary.

        :param update: Should the merge update the frequency of a word if it encounters it
        :param dictionary: Frequency dictionary to be added into current dictionary
        :return:
        """
        if language not in self.__sym_spell_languages:
            return None

        sc_l = self.__sym_spell_languages[language]
        for word in dictionary:
            freq = dictionary[word]
            result = sc_l.lookup(word, Verbosity.TOP)
            if result and result[0].distance == 0:
                if update:
                    self.update_valid_word(word, language, freq)
            else:
                self.add_valid_word(word, language, freq)

    def remove_words(self, word_list: List[str], language: str) -> None:
        """
        Remove words from working dictionary.

        :param word_list: List of strings to remove from dict. Passes if string is not present
        :return:
        """
        if language not in self.__sym_spell_languages:
            return None
        sc_l = self.__sym_spell_languages[language]
        for word in word_list:
            if len(sc_l.lookup(word, Verbosity.TOP)) > 0:
                sc_l.delete_dictionary_entry(word)

    def _word_contains_digits(self, word: str) -> bool:
        return any(c.isdigit() for c in word)
