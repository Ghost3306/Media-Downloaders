import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise RuntimeError(" GROQ_API_KEY not found in .env")

client = Groq(api_key=API_KEY)


MODEL = "openai/gpt-oss-120b"   # as you requested
MAX_CHARS = 2500
TEMPERATURE = 0.3

TRANSCRIBE_DIR = BASE_DIR / "transcribe"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def chunk_text(text, max_chars=MAX_CHARS):
    chunks, current = [], ""
    for line in text.splitlines():
        if len(current) + len(line) < max_chars:
            current += line + "\n"
        else:
            chunks.append(current.strip())
            current = line + "\n"
    if current.strip():
        chunks.append(current.strip())
    return chunks


def analyze_chunk(chunk, part_no, file_name):
    prompt = f"""
You are an expert analyst.

Analyze PART {part_no} of the transcript from file "{file_name}".
Extract:
- Key points
- Insights
- Important statements

Transcript:
{chunk}
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=TEMPERATURE,
    )
    return response.choices[0].message.content


def final_analysis(partials, file_name):
    combined = "\n\n".join(partials)

    prompt = f"""
You are a neutral automotive reviewer.

Using the partial analyses below, generate a FINAL, easy-to-read summary
for the car-related transcript file "{file_name}".

IMPORTANT STYLE RULES:
- Keep the language simple and conversational
- Avoid marketing, campaign, or brand-promotion tone
- Do NOT write like an advertisement or corporate report
- Do NOT include tables, scores, or strategies
- Write as if explaining to a normal car buyer
- Keep it factual and grounded in what was actually said

Write the output in short paragraphs or bullet points under these sections:

1. Executive Summary  
   - What this video is mainly about in simple words

2. Car & Context  
   - Which car is discussed  
   - What type of video it is (review, info, safety explanation, comparison)

3. Important Points Mentioned  
   - Key things the speaker talks about (features, safety, performance, etc.)

4. Pros (if mentioned)  
   - Good points clearly stated in the video

5. Cons or Limitations (if mentioned)  
   - Problems, concerns, or missing points

6. Overall Sentiment  
   - General tone of the video (positive / neutral / mixed / negative)

7. Practical Takeaway  
   - What a viewer or buyer should understand after watching this video

If any section is not discussed in the transcript, simply say "Not discussed".

Partial Analyses:
{combined}
"""


    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.25,
    )
    return response.choices[0].message.content


# ----------------------------
# MAIN PROCESS
# ----------------------------
def process_transcript_file(txt_path: Path):
    print(f"\n Processing: {txt_path.name}")

    transcript = txt_path.read_text(encoding="utf-8", errors="ignore")
    chunks = chunk_text(transcript)

    print(f"Chunks: {len(chunks)}")

    partial_results = []
    for i, chunk in enumerate(chunks, start=1):
        print(f"Analyzing chunk {i}/{len(chunks)}")
        partial_results.append(
            analyze_chunk(chunk, i, txt_path.name)
        )

    print("    Generating final analysis...")
    final_report = final_analysis(partial_results, txt_path.name)

    output_file = OUTPUT_DIR / f"{txt_path.stem}_analysis.txt"
    output_file.write_text(final_report, encoding="utf-8")

    print(f"   Saved → {output_file.name}")


# ----------------------------
# ENTRY POINT
# ----------------------------
if __name__ == "__main__":
    txt_files = list(TRANSCRIBE_DIR.glob("*.txt"))

    if not txt_files:
        print("No .txt files found in transcribe/")
        exit(0)

    print(f"Found {len(txt_files)} transcript files")

    for txt_file in txt_files:
        process_transcript_file(txt_file)

    print("\nALL TRANSCRIPTS ANALYZED SUCCESSFULLY")


# from dotenv import load_dotenv
# from pathlib import Path
# import os
# from groq import Groq

# # FORCE load .env from this file's directory
# env_path = Path(__file__).resolve().parent / ".env"
# load_dotenv(env_path)

# API_KEY = os.getenv("GROQ_API_KEY")

# if not API_KEY:
#     raise RuntimeError("GROQ_API_KEY not loaded from .env")

# client = Groq(api_key=API_KEY)
# models = client.models.list()
# for m in models.data:
#     print(m.id)