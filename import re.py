import re
import zipfile
from pathlib import Path
from fpdf import FPDF

def clean_srt_to_pdf(zip_path: str, output_pdf: str = "cleaned_subtitles.pdf"):
    # 1. Extract the .srt file from the .zip archive
    with zipfile.ZipFile(zip_path, "r") as z:
        srt_files = [f for f in z.namelist() if f.endswith(".srt")]
        if not srt_files:
            raise FileNotFoundError("No .srt file found inside the ZIP archive.")
        raw_text = z.read(srt_files[0]).decode("utf-8", errors="ignore")

    # 2. Remove sequence numbers, timestamps, HTML tags, and [SDH] brackets
    lines = raw_text.splitlines()
    cleaned_lines = []
    timestamp_pattern = re.compile(r"C:\Users\ELCOT\Downloads\Avengers.Endgame.Encore.2026.720p.DSNP.WEB-DL.DD.5.1.Atmos.H.264-playWEB_SDH_[eng]\Avengers.Endgame.Encore.2026.720p.DSNP.WEB-DL.DD.5.1.Atmos.H.264-playWEB_SDH_[eng].srt")

    for line in lines:
        line = line.strip()
        if not line or line.isdigit() or timestamp_pattern.match(line):
            continue
        # Remove HTML formatting tags (e.g., <i>, </i>) and SDH cues like [MUSIC PLAYING]
        line = re.sub(r"<[^>]+>", "", line)
        line = re.sub(r"\[[^\]]+\]", "", line).strip()
        if line:
            cleaned_lines.append(line)

    # 3. Join broken subtitle lines into flowing sentences/paragraphs
    paragraphs = []
    buffer = ""
    for line in cleaned_lines:
        # Start a new paragraph on speaker changes (leading hyphen)
        if line.startswith("-"):
            if buffer:
                paragraphs.append(buffer.strip())
            buffer = line
        else:
            buffer = f"{buffer} {line}".strip()
            if buffer.endswith((".", "!", "?", '"')):
                paragraphs.append(buffer)
                buffer = ""
    if buffer:
        paragraphs.append(buffer)

    # 4. Generate a clean PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)

    for para in paragraphs:
        # Encode safely for standard PDF fonts
        safe_text = para.encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 6, safe_text)
        pdf.ln(2)

    pdf.output(output_pdf)
    print(f"Saved readable PDF to: {output_pdf}")

if __name__ == "__main__":
    zip_file = "Avengers.Endgame.Encore.2026.720p.DSNP.WEB-DL.DD.5.1.Atmos.H.264-playWEB_SDH_[eng].zip"
    clean_srt_to_pdf(zip_file, "Avengers_Endgame_Readable.pdf")