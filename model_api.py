"Rough interface for HF summarization model pipeline."

from typing import Callable
from deep_translator import GoogleTranslator as Translator
from deep_translator.exceptions import RequestError
from nltk.tokenize import sent_tokenize
from langdetect import detect
from transformers import pipeline


def recursive_split(translator: Translator,
                    sentences: list,
                    split_idx: int = None) -> str:
    """
    If translation ain't successeful due to sequence length,
    split it in half and try again.
    """
    split_idx = len(sentences)//2 if split_idx is None else split_idx//2
    try:
        translated_piece = translator.translate(' '.join(sentences))
        return translated_piece
    except RequestError:
        left_sentences = recursive_split(translator,
                                         sentences[:split_idx],
                                         split_idx)
        right_sentences = recursive_split(translator,
                                          sentences[split_idx:],
                                          split_idx)
        return left_sentences + right_sentences

def split_translation(translator: Translator,
                      text: str,
                      splitter_foo: Callable = recursive_split,
                      **splitter_kwargs: dict) -> str:
    """
    Preprocess input and call the optional splitter.
    """
    sentence_splited_text = sent_tokenize(text)
    translated_text = splitter_foo(translator,
                                   sentence_splited_text,
                                   **splitter_kwargs)
    return translated_text

class ModelAPI():
    """
    Rough interface for HF summarization model pipeline.
    """
    def __init__(self) -> None:
        self.set_model_name("Remeris/BART-CNN-Convosumm")
        self.model_language = 'en'
        self.context_translator = None
        self.summary_translator = None
        self.set_input_language('auto')
        self.set_output_language('auto')

        self.summarizer = None

    def set_model_name(self, model_name) -> None:
        """
        Set the desired model's name, before loading it's pipeline.
        Default - Remeris/BART-CNN-Convosumm
        """
        self.model_name = model_name

    def set_input_language(self, language) -> None:
        """
        Set the desired model's name, before loading it's pipeline.
        Default - autodetect.
        """
        self.input_language = language
        self.context_translator = Translator(source=self.input_language,
                                             target=self.model_language)

    def set_model_language(self, language) -> None:
        """
        Manually set language which model is trained on.
        Default - en.
        """
        self.model_language = language
        self.context_translator = Translator(source=self.input_language,
                                             target=self.model_language)
        self.summary_translator = Translator(source=self.model_language,
                                             target=self.output_language)

    def set_output_language(self, language) -> None:
        """
        Manually set language of output summary.
        Default - same as input.
        """
        self.output_language = language
        self.summary_translator = Translator(source=self.model_language,
                                             target=self.output_language)

    def prepare_model(self) -> None:
        """
        Load selected model's pipeline.
        """
        self.summarizer = pipeline(task='summarization', model=self.model_name)

    def _check_input_language(self, context: str) -> str:
        """
        Translate context, reinit output translator with detected language, if needed.
        """
        if self.input_language == self.output_language == 'auto':
            self.summary_translator = Translator(source=self.model_language,
                                                 target=detect(context))
        translated_context = split_translation(self.context_translator, context)
        return translated_context

    def _check_output_language(self, summary: str) -> str:
        """
        Translate output summary.
        """
        translated_summary = split_translation(self.summary_translator, summary)
        return translated_summary

    def _get_model_output(self, context: str) -> str:
        """
        Recieve and unpack model's output.
        """
        model_output = self.summarizer(context)[0]['summary_text']
        return model_output

    def summarize(self, context: str) -> str:
        """
        Load model if needed and launch summarization sequence.
        """
        if self.summarizer is None:
            self.prepare_model()
        context = self._check_input_language(context)
        summary = self._get_model_output(context)
        summary = self._check_output_language(summary)
        return summary
