import os
import torch
import soundfile as sf
import librosa
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline


INPUT_AUDIO_DIR = r"D:\Tata Motors Internship\Source-Code\Media-Downloader\Linkedin\Linkedin-Engine\audio"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_TXT_DIR = os.path.join(BASE_DIR, "transcribe")

os.makedirs(OUTPUT_TXT_DIR, exist_ok=True)


device = "cuda:0" if torch.cuda.is_available() else "cpu"
dtype = torch.float16 if torch.cuda.is_available() else torch.float32


model_id = "openai/whisper-large-v3-turbo"

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id,
    torch_dtype=dtype,
    low_cpu_mem_usage=True,
    use_safetensors=True
).to(device)

processor = AutoProcessor.from_pretrained(model_id)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    torch_dtype=dtype,
    device=device,
)


for file in os.listdir(INPUT_AUDIO_DIR):
    if not file.lower().endswith((".mp3", ".wav", ".m4a")):
        continue

    audio_path = os.path.join(INPUT_AUDIO_DIR, file)
    base_name = os.path.splitext(file)[0]
    output_txt = os.path.join(OUTPUT_TXT_DIR, base_name + ".txt")

    print(f"Transcribing: {file}")

    # Load audio
    audio, sr = sf.read(audio_path)

    # Convert to mono
    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    # Resample to 16kHz
    if sr != 16000:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
        sr = 16000

    # Transcribe
    result = pipe(
        {"array": audio, "sampling_rate": sr},
        return_timestamps=True
    )

    # Save transcript
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(result["text"])

    print(f"Saved transcript: {output_txt}")

print("All files transcribed.")
