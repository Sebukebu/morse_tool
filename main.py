
import numpy as np
import sounddevice as sd


morse_code_map = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
    'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
    '3': '...--', '4': '....-', '5': '.....', '6': '-....',
    '7': '--...', '8': '---..', '9': '----.', ' ': '_'
}

wpm = int(20)
farnsworthwpm = None




def text_to_morse(text: str) -> str:

    text = text.upper()
    morse_code = []
    for char in text:
        if char in morse_code_map:
            morse_code.append(morse_code_map[char])
        else:
            raise ValueError(f"Character '{char}' not supported in Morse code.")
    return ' '.join(morse_code)


def morse_to_audio(morse: str, wpm: int = 18, farnsworthwpm: int = 0, amplitude: float = 0.5, frequency: int = 440, samplerate: int = 44100) -> np.ndarray:
  
    unit = 1.2 / wpm

    # if farnsworthwpm is not none, set the timing according to Farsworth timing
    if farnsworthwpm:
        dot_duration = unit
        dash_duration = 3 * unit
        farnsworth_addition = (60 * wpm - 37.2 * farnsworthwpm) / (wpm * farnsworthwpm)
        between_characters = (3 * farnsworth_addition) / 19
        between_words = (7 * farnsworth_addition) / 19
    else:
        dot_duration = unit
        between_characters = 3 * unit
        between_words = 7 * unit
        dash_duration = 3 * unit


    audio_signal = []

    def tone(duration):
        t = np.linspace(0, duration, int(samplerate * duration), False)
        return amplitude * np.sin(2 * np.pi * frequency * t)

    def silence(duration):
        return np.zeros(int(samplerate * duration))

    for symbol in morse:
        if symbol == '.':
            audio_signal.append(tone(dot_duration))
            audio_signal.append(silence(unit))
        elif symbol == '-':
            audio_signal.append(tone(dash_duration))
            audio_signal.append(silence(unit))
        elif symbol == ' ':
            audio_signal.append(silence(between_characters))
        elif symbol == '_':
            audio_signal.append(silence(between_words))
        else:
            raise ValueError(f"Unsupported Morse code symbol: {symbol}")

    return np.concatenate(audio_signal)

def play_morse_audio(buffered: np.ndarray):

    sd.play(buffered)
    sd.wait()


# Example usage
if __name__ == "__main__":

    try:
        morse = text_to_morse("Hello World")
        print(f"Morse Code: {morse}")
        morse_audio = morse_to_audio(morse, wpm = wpm, farnsworthwpm = farnsworthwpm, amplitude=0.5, frequency=440)
        play_morse_audio(morse_audio)
    except ValueError as e:
        print(e)


