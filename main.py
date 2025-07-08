
import numpy as np
import sounddevice as sd
import random



morse_code_map = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
    'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
    '3': '...--', '4': '....-', '5': '.....', '6': '-....',
    '7': '--...', '8': '---..', '9': '----.', ' ': '_',
    '.': '.-.-.-', ',': '--..--', '?': '..--..', ';': '-.-.-.',
    ':': '---...', '-': '-....-', '/': '-..-.', "'": '.----.', '"': '.-..-.',
    '_': '..--.-', '+': '.-.-.', '*': '-..-', '=': '-...-'
    }

alphabet_chars = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J','K', 'L', 'M', 
    'N', 'O', 'P', 'Q', 'R', 'S', 'T','U', 'V', 'W', 'X', 'Y', 'Z'
    ]

number_chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

special_chars = ['.', ',', '?', ';', ':', '-', '/', "'", '"','_', '+', '*', '=']


class Settings():
    def __init__(self, wpm = 20, farnsworthwpm = None, amplitude = 0.5, frequency = 440,
                 samplerate = 44100, alphabet = True, numbers = False, specials = False):
        self.wpm = int(wpm)
        self.farnsworthwpm = int(farnsworthwpm) if farnsworthwpm else None
        self.amplitude = float(amplitude)
        self.frequency = int(frequency)
        self.samplerate = int(samplerate)
        self.alphabet = bool(alphabet)
        self.numbers = bool(numbers)
        self.specials = bool(specials)

        def __repr__(self):
            return (f"SETTINGS(wpm={self.wpm}, farnsworthwpm={self.farnsworthwpm}, amplitude={self.amplitude}, \
                    frequency={self.frequency}, samplerate={self.samplerate}, alphabet={self.alphabet},  \
                    numbers={self.numbers}, specials={self.specials})")
        
        def update(self, key, value):
            # Convert to correct type before updating
            current_value = getattr(self, key)

            try:
                if isinstance(current_value, int):
                    if value is None:
                        setattr(self, key, None)
                    else:
                        setattr(self, key, int(value))
                elif isinstance(current_value, float):
                    setattr(self, key, float(value))
                elif isinstance(current_value, bool):
                    setattr(self, key, bool(value))
                else:
                    setattr(self, key, value)
                print(f"'{key}' updated to {getattr(self, key)}")
            except ValueError:
                print(f"Invalid value for '{key}': {value}")

s = Settings()


def text_to_morse(text: str) -> str:

    text = text.upper()
    morse_code = []
    for char in text:
        if char in morse_code_map:
            morse_code.append(morse_code_map[char])
        else:
            raise ValueError(f"Character '{char}' not supported in Morse code.")
    return ' '.join(morse_code)


def morse_to_audio(morse: str, s) -> np.ndarray:
  
    unit = 1.2 / s.wpm

    # if farnsworthwpm is not none, set the timing according to Farsworth timing
    if s.farnsworthwpm and s.farnsworthwpm > 0:
        dot_duration = unit
        dash_duration = 3 * unit
        farnsworth_addition = (60 * s.wpm - 37.2 * s.farnsworthwpm) / (s.wpm * s.farnsworthwpm)
        between_characters = (3 * farnsworth_addition) / 19
        between_words = (7 * farnsworth_addition) / 19
    else:
        dot_duration = unit
        between_characters = 3 * unit
        between_words = 7 * unit
        dash_duration = 3 * unit


    audio_signal = []

    def tone(duration):
        t = np.linspace(0, duration, int(s.samplerate * duration), False)
        return s.amplitude * np.sin(2 * np.pi * s.frequency * t)

    def silence(duration):
        return np.zeros(int(s.samplerate * duration))

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


def create_random_text(s, length: int) -> str:
    chars = []
    if s.alphabet == True:
        chars.extend(alphabet_chars)
    if s.numbers == True:
        chars.extend(number_chars)
    if s.specials == True:
        chars.extend(special_chars)

    randomtext = ''
    probabilityforspace = 0.2
    for c in range(1, length +1):
        char = random.choice(chars)
        randomtext = randomtext + str(char)
        if random.random() < probabilityforspace:
            randomtext = randomtext + ' '

    return randomtext


# Example usage
if __name__ == "__main__":
    print("Do you want to write a text yourself, or create a random text?")
    while True:
        choice = input("1) Write text myself." \
                    "\n2) Create random text." \
                    "\nInput choice here(1 or 2): ")
        try:
            choice = int(choice)
            
            match choice:
                case 1:
                    text = input("Input the string you want to convert to morse: ")
                    break
                case 2:
                    text = create_random_text(s, 15)
                    break
                case _:
                    print("Choose either number 1 or number 2, and press enter")
                    print()
        except:
            print("Choose either number 1 or number 2, and press enter")
            print()
            
    try:
        morse = text_to_morse(text)
        print(f"Text: {text}")
        print(f"Morse Code: {morse}")
        morse_audio = morse_to_audio(morse, s)
        play_morse_audio(morse_audio)
    except ValueError as e:
        print(e)


