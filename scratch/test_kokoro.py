import time
import torch
import soundfile as sf
from kokoro import KPipeline

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Device: {torch.cuda.get_device_name(0)}")

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Initializing Kokoro KPipeline on {device}...")
t0 = time.time()
pipeline = KPipeline(lang_code='a', device=device)
print(f"Pipeline initialized in {time.time() - t0:.2f}s")

text = "Welcome to this educational module. Today, we will explore the fundamental principles of data science and artificial intelligence."
print("Synthesizing educational text with voice 'af_heart'...")
t1 = time.time()
generator = pipeline(text, voice='af_heart', speed=0.95)

audio_chunks = []
for i, (gs, ps, audio) in enumerate(generator):
    audio_chunks.append(audio)

if audio_chunks:
    full_audio = torch.cat([torch.from_numpy(chunk) if not isinstance(chunk, torch.Tensor) else chunk for chunk in audio_chunks], dim=0).numpy()
    out_path = "output/test_kokoro_educational.wav"
    sf.write(out_path, full_audio, 24000)
    print(f"Audio synthesized in {time.time() - t1:.2f}s, saved to {out_path} ({len(full_audio)} samples, {len(full_audio)/24000:.2f}s duration)")
else:
    print("No audio was generated.")
