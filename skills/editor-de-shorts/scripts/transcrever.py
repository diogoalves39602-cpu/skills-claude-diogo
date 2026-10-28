"""Transcreve uma narracao pronta com tempos por palavra (faster-whisper) -> words.json na pasta do audio.
Uso: python transcrever.py voz.wav [modelo=small]
"""
import json, os, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel

path = sys.argv[1]; model = sys.argv[2] if len(sys.argv) > 2 else "small"
# decodifica com ffmpeg: passar o caminho direto quebra com versoes novas do PyAV (erro 'metadata_errors')
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                     capture_output=True, check=True).stdout
segs, _ = WhisperModel(model, device="cpu", compute_type="int8").transcribe(
    np.frombuffer(raw, np.float32), language="pt", word_timestamps=True)
words = [(round(w.start, 3), round(w.end, 3), w.word.strip()) for s in segs for w in s.words]
out = os.path.join(os.path.dirname(os.path.abspath(path)), "words.json")
json.dump(words, open(out, "w", encoding="utf-8"), ensure_ascii=False)
print(len(words), "palavras ->", out)
print(" ".join(w[2] for w in words))
