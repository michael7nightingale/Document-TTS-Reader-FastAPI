from vosk_tts.model import Model
from vosk_tts.synth import Synth
from uuid import uuid4
import tempfile

model = Model("model_russian_tts")
synth = Synth(model)


def synth_audio(text: str, filepath: str):
    synth.synth(
        text=text,
        oname=filepath
    )
