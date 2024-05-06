import tempfile
import time

from io import BytesIO
from pydub import AudioSegment
from typing import List


def split_text_into_chunks(text, max_length=4096) -> List[str]:
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        if len(" ".join(current_chunk)) + len(word) + 1 <= max_length:
            current_chunk.append(word)
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def generate_audio(client, text) -> List[AudioSegment]:
    chunks = split_text_into_chunks(text)
    audio_segments = []
    for chunk in chunks:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=chunk
        )
        audio_data = BytesIO(response.content)
        audio_segments.append(AudioSegment.from_file(audio_data, format="mp3"))
    return audio_segments


def merge_audio_segments(audio_segments) -> AudioSegment:
    merged_audio = AudioSegment.empty()
    for segment in audio_segments:
        merged_audio += segment
    return merged_audio


def save_audio_to_temp_file(merged_audio) -> str:
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        merged_audio.export(temp_file.name, format="mp3")
        temp_file.seek(0)
        return temp_file.name


def time_audio_generation_per_character(client, text):
    start_time = time.time()
    audio_segments = generate_audio(client, text)
    merged_audio = merge_audio_segments(audio_segments)
    end_time = time.time()

    generation_time = end_time - start_time
    average_time_per_character = generation_time / len(text)

    print(f"Total generation time: {generation_time:.2f} seconds")
    print(f"Average time per character: {average_time_per_character:.4f} seconds")

    return average_time_per_character