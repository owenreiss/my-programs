# plays 2 similar pitches and asks user to identify the higher pitch, difficulty increases after more right answers

import pygame
import numpy
import math
import time
import random

pygame.init()

bits = 16
sample_rate = 44100
A4 = 440
txt_size = 30
note_indexes = {"A": 0.0, "A#": 1, "Bb": 1.0, "B": 2.0, "Cb": 2, "C": 3.0, "B#": 3, "C#": 4.0, "Db": 4, "D": 5.0, "D#": 6, "Eb": 6.0, "E": 7.0, "Fb": 7, "F": 8.0, "E#": 8, "F#": 9.0, "Gb": 9, "G": 10.0, "G#": 11.0, "Ab": 11.0} # G# and Ab are equally "right" as they are the 3rd change in key signature for sharps and flats
notes = ["C0/B#", "C#/Db", "D", "D#/Eb", "E0/Fb", "F0/E#", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B0/Cb"]
notes_next_to_white = {"C", "B", "F", "E"}
pygame.mixer.pre_init(sample_rate, bits)

class Tone:
    def __init__(self, hz=A4, duration=1):
        if hz < 20 or hz > 20000:
            raise ValueError(f"{hz}hz cannot be played") 
        self.hz = hz
        self.duration = duration
    
    def play(self, mult=False):
        num_samples = int(round(self.duration * sample_rate))
        sound_buffer = numpy.zeros((num_samples, 2), dtype=numpy.int16)
        amplitude = 2 ** (bits - 1) - 1
        
        for sample_num in range(num_samples):
            t = float(sample_num) / sample_rate
            sine = sine_x(amplitude, self.hz, t)
            sound_buffer[sample_num][0] = sine
            sound_buffer[sample_num][1] = sine

        sound = pygame.sndarray.make_sound(sound_buffer)
        sound.play(loops=1, maxtime=int(self.duration * 1000))
        # if not mult:
        #     time.sleep(self.duration)

class Note(Tone):
    def __init__(self, note=None, octave=None, duration=None):
        self.note = note
        self.octave = octave
        self.hz = A4 * (2 ** (get_note_distance(("A", 4), (note, octave)) / 12))
        self.duration = duration

    def __repr__(self):
        return f'Note("{self.note}", {self.octave}, {self.duration})'

def get_note_distance(note1, note2):
    return (notes.index(note2[0]) + (note2[1] * 12)) - (notes.index(note1[0]) + (note1[1] * 12))

def sine_x(amp, freq, time):
    return int(round(amp * math.sin(2 * math.pi * freq * time)))

def play_mult_sines(sines: tuple[Tone]):
    max_dur = 0
    for tone in sines:
        if tone.duration > max_dur:
            max_dur = tone.duration
        tone.play(True)
    time.sleep(max_dur)

def is_valid_note(arg_note: str) -> bool:
    for note in notes:
        if arg_note.upper() in note.upper() and arg_note not in "#/0/":
            return True
    return False

def play_perfect_pitch():
    oct_range = ((1, 8), (3, 6), (4, 5))[int(input("Do you want hard mode (type 1), medium mode (type 2), or easy mode (type 3): ")) - 1]
    print('Guess what the musical note is that you are hearing. Type "b" for flat and "#" for sharp. Type "repeat" to repeat the note and "exit" to stop.')
    score = (0, 1)
    while True:
        print("What note is this: \r", end="")
        random_note, random_octave = random.randint(0, 11), random.randint(*oct_range)
        while True:
            print("What note is this: \r", end="")
            Tone(Note(notes[random_note], random_octave).hz, 2).play()
            given_note = input("What note is this: ")
            if not is_valid_note(given_note):
                orig_given = given_note
                given_note = given_note.upper()
            else:
                break
            if given_note == "EXIT":
                return score
            elif given_note != "REPEAT":
                print(f"{orig_given} is not a valid note, replaying note")
            else:
                print("Repeating note")
        try:
            if notes.index(given_note.upper()) == random_note:
                print("Correct")
            else:
                print(f"Incorrect, answer is {notes[random_note] if '0' not in notes[random_note] else notes[random_note][0] + notes[random_note][2:]}")
        except ValueError:
            if given_note in notes_next_to_white:
                given_note += "0"
            for idx, note in enumerate(notes):
                if (given_note.upper() == note[0:2].upper() or given_note.upper() == note[3:5].upper()) and random_note == idx:
                    print("Correct")
                    break
            else:
                print(f"Incorrect, answer is {notes[random_note] if '0' not in notes[random_note] else notes[random_note][0] + notes[random_note][2:]}")


def play_intonation():
    print('Guess whether the second note is higher or lower than the first. Type "exit" when done, and type "repeat" to hear the notes again.')
    ranges = ((Note("C0/B#", 2).hz*10, Note("C0/B#", 7).hz*10), (Note("C0/B#", 3).hz*10, Note("C0/B#", 6).hz*10), (Note("C0/B#", 4).hz*10, Note("C0/B#", 7-1).hz*10))
    oct_range = ranges[int(input("Do you want hard mode (type 1), medium mode (type 2), or easy mode (type 3): ")) - 1]
    end = False
    cent_changes = [100, 50, 30, 20, 15, 12, 10, 9, 8, 7, 7-1, 5.5, 5, 4.5, 4, 3.7, 3.3, 3, 2.7, 2.3, 2, 1.8, 1.4, 1.2, 1.0] + [x/10 for x in range(9, 0, -1)]
    cent_diff = 100
    while not end:
        print()
        start_hz = random.randint(*[int(x) for x in oct_range])/10
        higher = bool(random.randint(0, 1))
        end_hz = start_hz * (2 ** ((cent_diff if higher else -cent_diff)/ 1200))
        while True:
            print(f"Difference is {cent_diff}% of a semitone\nListen...", end="\r")
            Tone(start_hz, 1.25).play()
            time.sleep(1.5)
            Tone(end_hz, 1.25).play()
            given_input = input("Was the second pitch higher or lower (h/l): ").lower()
            if given_input == "exit":
                print("Thanks for playing!")
                end = True
                break
            elif given_input == "repeat":
                print("Repeating notes...", end="\r")
            elif given_input != "h" and given_input != "l":
                print(f'{given_input} is not a valid answer. Type "h" for higher, "l" for lower, "repeat" to hear the notes again, or "exit" to stop. Replaying pitches...', end="\r")
            elif (given_input == "h") == higher:
                print(f"Correct, the first note was {start_hz}hz and the second note was {round(end_hz, 1)}hz")
                if cent_changes.index(cent_diff) + 1 == len(cent_changes):
                    print("Congratulations! You won!")
                    end = True
                else:
                    cent_diff = cent_changes[cent_changes.index(cent_diff) + 1]
                break
            else:
                print(f"Incorrect, the first note was {start_hz}hz and the second note was {round(end_hz, 1)}hz")
                if cent_changes.index(cent_diff) - 2 >= 0:
                    cent_diff = cent_changes[cent_changes.index(cent_diff) - 2]
                else:
                    cent_diff = 100
                break


if __name__ == "__main__":
    play_intonation()
