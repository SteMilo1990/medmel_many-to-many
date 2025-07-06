import json
import re
from clean_melody import clean_melody
from pitch2interval import notes_to_intervals

consider_plica = False
def get_intervals_from_pitch(pitch_lines_ar):
    global consider_plica
    interval_ar = []
    for line in pitch_lines_ar:
        interval_ar.append(notes_to_intervals(line, consider_plica))
    return interval_ar

def prepare_corpus():
    excluded_songs = [1772, 491, 1554, 654, 732, 1333, 743, 789, 790, 1754, 1545]
    with open("files/mm_staves_stored.json", "r", encoding="utf-8") as file:
        medmel_data = json.load(file)

    corpus = []
    for song in medmel_data:
        print(song)
        if int(song["id_staves"]) not in excluded_songs \
                and not song["id"].startswith("RS") \
                and not song["id"].startswith("Sponsus") \
                and not song["id"].startswith("try"):

            melody_modern = json.loads(song["staves"])[0]
            melody_clean = clean_melody(melody_modern)

            pitch_lines_ar = melody_clean.split("\n")
            intervals_lines_ar = get_intervals_from_pitch(pitch_lines_ar)

            text_lines = json.loads(song["text"])[0].split("\n")

            corpus.append({
                'id_staves': song["id_staves"],
                'title': song["title"],
                'id': song["id"],
                'author': song["author"],
                'ms': song["ms"],
                'f': song["f"],
                'staves': pitch_lines_ar,
                'intervals': intervals_lines_ar,
                'text': text_lines
            })

    return corpus


def save_to_json(data, filename="output.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

corpus = prepare_corpus()
save_to_json(corpus, filename="files/medmel_corpus.json")