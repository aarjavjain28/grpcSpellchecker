from collections import Counter
from typing import List, Dict, Optional
from polyglot.text import Text
import regex as re

from spellchecker import SpellChecker, get_banks, Prediction, Options
import logging
logger = logging.getLogger(__name__)


class SpellCheckerAPI(str, Prediction, Options):
    """Class to check the spelling for a list of strings, in multiple languages"""
    __config: Dict[str, Dict[str, str]]
    __freq_dictionaries: List[str]
    __spellcheck_lib: SpellChecker
    __bad_characters_regex: re.Pattern

    def __init__(self, config: Dict) -> None:
        super(SpellCheckerAPI, self).__init__()

        self.__freq_dictionaries = get_banks(config['bank_dc'])[config['bank']]
        self.__spellcheck_lib = SpellChecker(config['model']['frequency_dictionary_path'],
                                             config['model']['channel_freq_path'], self.__freq_dictionaries)
        self.__bad_characters_regex = re.compile(r'\p{Cc}|\p{Cs}')

    def predict(self, input_data: List[str], options: Optional[Options] = None) -> List[Prediction]:
        return [self.__fraction_well_spelt_words(self.__remove_bad_chars(sentence), options) for sentence in input_data]

    def __fraction_well_spelt_words(self, sentence: str, options: Optional[Options] = None) -> Prediction:
        if not sentence:
            return Prediction.construct(total_words=0, well_spelt_words=0, ratio=0.0, suggestions={},
                                        supported_languages=False)
        poly_text = Text(sentence)
        if not poly_text.words:
            return Prediction.construct(total_words=0, well_spelt_words=0, ratio=0.0, suggestions={},
                                        supported_languages=False)
        language = options.language_code if options and options.language_code else poly_text.language.code
        channel = options.channel if options and options.channel else None
        suggestions = {}
        word_counts: Dict[str, int] = Counter(poly_text.words)
        if language not in self.__freq_dictionaries:
            return Prediction.construct(total_words=sum(word_counts.values()), well_spelt_words=0, ratio=0.0,
                                        suggestions={}, supported_language=False)
        else:
            well_spelt_words = 0
            for word in word_counts:
                res = self.__spellcheck_lib.candidates_word(word, language=language, channel=channel,
                                                            number_of_candidates=5)
                if res and res[0].correct_spelling or word.isdigit():
                    well_spelt_words += word_counts[word]

                else:
                    suggestions[str(word)] = list(r.term for r in res)

        total_words = sum(word_counts.values())
        ratio = round((well_spelt_words / total_words), 3)
        return Prediction.construct(total_words=total_words, well_spelt_words=well_spelt_words, ratio=ratio,
                                    suggestions=suggestions, supported_language=True)

    @property
    def supported_languages(self) -> List[str]:
        return self.__freq_dictionaries

    def __remove_bad_chars(self, text: str) -> str:
        return re.sub(pattern=self.__bad_characters_regex, repl='', string=text)
