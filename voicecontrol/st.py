#!/usr/bin/python

import pyaudio
import typing
import typing_extensions
import abc
import os
from collections import Counter
from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *


p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    frames_per_buffer=1024,
)
stream.start_stream()


def vote_most_common_word(self: Decoder):
    c = Counter()
    for h, _ in zip(self.nbest(), range(10)):
        h = h.hypstr
        if h is None:
            c[None] += 1
            continue
        for w in h.split():
            c[w] += 1
    ab = c.most_common(2)
    if not ab:
        return None
    if len(ab) == 1:
        [(a, _)] = ab
        return a
    if len(ab) == 2:
        [(a, c1), (b, c2)] = ab
        if c1 >= 1.3 * c2:
            return a


def just_hyp(self: Decoder):
    hyp = self.hyp()
    if hyp:
        return hyp.hypstr


_K = typing.TypeVar("_K")
_V = typing.TypeVar("_V")


class Lookup(typing_extensions.Protocol[_K, _V]):
    def get(self, k: _K) -> typing.Optional[_V]:
        pass


class DSModelProto(typing_extensions.Protocol):
    # noinspection PyArgumentList
    path: str
    commands: Lookup[str, typing.Callable]
    accept_score: int = -3000
    decoder: Decoder
    decider: typing.Callable[[Decoder], typing.Optional[str]]


class CommandsFromMethods:
    @property
    def commands(self):
        return ClassLookup(self)


class DSModel(DSModelProto):
    accept_score = -3000
    decoder = None

    def __init__(self):
        path = self.path
        cls = self.__class__
        if cls.decoder is None:
            config = Decoder.default_config()
            config.set_string("-hmm", os.path.join(path, "acoustic-model"))
            config.set_string(
                "-lm", os.path.join(path, "language-model.lm.bin")
            )
            config.set_string("-logfn", "nul")
            pron_dict = os.path.join(path, "pronounciation-dictionary.dict")
            if not os.path.exists(pron_dict):
                pron_dict = os.path.join(path, "pronunciation-dictionary.dict")
            config.set_string("-dict", pron_dict)
            cls.decoder = Decoder(config)


class ClassLookup:
    def __init__(self, m):
        self.m = m

    def get(self, k: str) -> typing.Optional[typing.Callable]:
        return getattr(self.m, k, None)


class StateMachine(typing.Generic[_V]):
    def __init__(self, init_state: _V, start_model: DSModelProto):
        self.model = start_model
        self.state = init_state
        self.events = []

    def add_event(self, event: typing.Callable[['StateMachine'], None]):
        self.events.append(event)

    def _other_events(self):
        for e in self.events:
            e(self)

    def start_loop(self):

        in_speech_bf = False
        decoder = self.model.decoder
        decider = self.model.decider
        decoder.start_utt()
        self._other_events()
        while True:
            self._other_events()
            buf = stream.read(1024)
            if buf:
                decoder.process_raw(buf, False, False)
                if decoder.get_in_speech() != in_speech_bf:
                    in_speech_bf = decoder.get_in_speech()
                    if not in_speech_bf:
                        decoder.end_utt()
                        command = decider(decoder)
                        if command:
                            callback = self.model.commands.get(command)
                            if callback:
                                callback(self)
                            decoder = self.model.decoder
                            decider = self.model.decider
                        print(self.model.__class__.__name__, command)
                        decoder.start_utt()

            else:
                break
        decoder.end_utt()
