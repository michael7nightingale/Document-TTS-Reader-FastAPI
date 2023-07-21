from gtts import gTTS
from threading import Thread


async def synth_audio(text: str, filepath: str, language: str) -> None:
    audio = gTTS(
        text=text,
        lang=language,

    )
    thread = Thread(
        target=audio.save,
        args=(filepath, )
    )
    thread.start()
    thread.join()
    print(2, filepath, language, text)
    print(3)
