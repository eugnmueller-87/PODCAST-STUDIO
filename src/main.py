import os
import sys
from pathlib import Path

from dotenv import load_dotenv
import gradio as gr

load_dotenv(Path(__file__).parent.parent / ".env")
sys.path.insert(0, str(Path(__file__).parent))

from data_processor import process
from llm_processor import generate_script
from tts_generator import synthesise_script
from models import PodcastSettings, PodcastStyle, SourceType

STYLE_MAP = {
    "Educational": PodcastStyle.EDUCATIONAL,
    "Debate": PodcastStyle.DEBATE,
    "News Brief": PodcastStyle.NEWS_BRIEF,
    "Deep Dive": PodcastStyle.DEEP_DIVE,
}

SOURCE_MAP = {
    "Text": SourceType.TEXT,
    "URL": SourceType.URL,
    "YouTube": SourceType.YOUTUBE,
    "PDF": SourceType.PDF,
}


def run_pipeline(
    source_type_label,
    text_input,
    url_input,
    youtube_input,
    pdf_input,
    style_label,
    host_a_name,
    host_b_name,
    target_minutes,
    progress=gr.Progress(),
):
    try:
        source_type = SOURCE_MAP[source_type_label]

        progress(0.1, desc="Reading source...")
        if source_type == SourceType.TEXT:
            source = text_input
        elif source_type == SourceType.URL:
            source = url_input
        elif source_type == SourceType.YOUTUBE:
            source = youtube_input
        else:
            source = pdf_input

        if not source:
            return None, "No input provided.", "", "", ""

        podcast_input = process(source, source_type)

        settings = PodcastSettings(
            style=STYLE_MAP[style_label],
            host_a_name=host_a_name or "Alex",
            host_b_name=host_b_name or "Sam",
            target_minutes=int(target_minutes),
        )

        progress(0.35, desc="Generating script with Claude...")
        script = generate_script(podcast_input, settings)

        progress(0.65, desc="Generating audio...")
        audio_output = synthesise_script(script, settings)

        script_text = "\n\n".join(
            f"{line.host_name.upper()}: {line.text}" for line in script.lines
        )

        metadata_text = (
            f"Title: {script.metadata.title}\n"
            f"Summary: {script.metadata.summary}\n"
            f"Tags: {', '.join(script.metadata.tags)}\n"
            f"Duration: ~{script.metadata.estimated_duration_min} min"
        )

        duration_min = round(audio_output.duration_seconds / 60, 1)
        stats = f"Generated {len(script.lines)} dialogue lines | Audio: {duration_min} min | Source: {podcast_input.word_count} words"

        progress(1.0, desc="Done!")
        return audio_output.file_path, script_text, metadata_text, stats, audio_output.file_path

    except Exception as e:
        return None, f"Error: {str(e)}", "", "", ""


STUDIO_SVG = """
<div style="background:linear-gradient(135deg,#f0f4ff 0%,#e8eeff 100%);border-radius:16px;padding:24px 32px 16px;margin-bottom:20px;text-align:center;border:1px solid #d0d8f0;">
  <div style="font-size:2rem;font-weight:900;color:#1a237e;letter-spacing:2px;">🎙️ PodcastIQ</div>
  <div style="color:#5c6bc0;font-size:0.95rem;margin-top:4px;margin-bottom:20px;">Turn any content about AI into a two-host podcast episode</div>
  <svg viewBox="0 0 620 200" xmlns="http://www.w3.org/2000/svg" style="max-width:580px;width:100%;">
    <!-- Studio floor -->
    <rect width="620" height="200" fill="#eef1fb" rx="12"/>
    <!-- Floor line -->
    <rect x="0" y="165" width="620" height="35" fill="#dde3f5" rx="0"/>
    <!-- ON AIR sign -->
    <rect x="258" y="12" width="104" height="26" rx="6" fill="#c0392b"/>
    <circle cx="262" cy="25" r="5" fill="#ff6b6b" opacity="0.9"/>
    <text x="305" y="30" text-anchor="middle" fill="white" font-family="Arial" font-weight="bold" font-size="12">ON AIR</text>

    <!-- ── LEFT HOST (Alex) ── -->
    <!-- Couch body -->
    <rect x="30" y="130" width="170" height="38" rx="10" fill="#5c6bc0"/>
    <!-- Couch back -->
    <rect x="30" y="100" width="170" height="38" rx="10" fill="#7986cb"/>
    <!-- Couch left arm -->
    <rect x="25" y="108" width="22" height="60" rx="8" fill="#5c6bc0"/>
    <!-- Couch right arm -->
    <rect x="183" y="108" width="22" height="60" rx="8" fill="#5c6bc0"/>
    <!-- Body -->
    <rect x="88" y="88" width="54" height="48" rx="10" fill="#c0392b"/>
    <!-- Head -->
    <ellipse cx="115" cy="72" rx="22" ry="24" fill="#f0c27f"/>
    <!-- Hair -->
    <ellipse cx="115" cy="52" rx="22" ry="10" fill="#3b2314"/>
    <!-- Eyes -->
    <circle cx="107" cy="70" r="3" fill="#3b2314"/>
    <circle cx="123" cy="70" r="3" fill="#3b2314"/>
    <!-- Smile -->
    <path d="M 108 80 Q 115 86 122 80" stroke="#3b2314" stroke-width="1.5" fill="none"/>
    <!-- Headphones band -->
    <path d="M 93 68 Q 115 48 137 68" stroke="#222" stroke-width="5" fill="none" stroke-linecap="round"/>
    <!-- Headphone cups -->
    <rect x="88" y="65" width="14" height="20" rx="6" fill="#333"/>
    <rect x="128" y="65" width="14" height="20" rx="6" fill="#333"/>
    <rect x="90" y="67" width="10" height="16" rx="4" fill="#555"/>
    <rect x="130" y="67" width="10" height="16" rx="4" fill="#555"/>
    <!-- Desk mic -->
    <rect x="148" y="120" width="3" height="30" fill="#888"/>
    <line x1="135" y1="150" x2="165" y2="150" stroke="#888" stroke-width="2.5" stroke-linecap="round"/>
    <rect x="141" y="104" width="17" height="28" rx="8" fill="#444"/>
    <rect x="143" y="106" width="13" height="24" rx="6" fill="#666"/>
    <!-- Mic grill lines -->
    <line x1="144" y1="110" x2="155" y2="110" stroke="#888" stroke-width="1" opacity="0.6"/>
    <line x1="144" y1="114" x2="155" y2="114" stroke="#888" stroke-width="1" opacity="0.6"/>
    <line x1="144" y1="118" x2="155" y2="118" stroke="#888" stroke-width="1" opacity="0.6"/>
    <line x1="144" y1="122" x2="155" y2="122" stroke="#888" stroke-width="1" opacity="0.6"/>
    <!-- Alex label -->
    <text x="115" y="190" text-anchor="middle" fill="#3949ab" font-family="Arial" font-size="13" font-weight="bold">Alex</text>

    <!-- ── SOUND WAVES (center) ── -->
    <path d="M 287 85 Q 310 68 333 85" stroke="#e74c3c" stroke-width="2.5" fill="none" opacity="0.9" stroke-linecap="round"/>
    <path d="M 277 97 Q 310 72 343 97" stroke="#e74c3c" stroke-width="2" fill="none" opacity="0.55" stroke-linecap="round"/>
    <path d="M 267 109 Q 310 76 353 109" stroke="#e74c3c" stroke-width="1.5" fill="none" opacity="0.25" stroke-linecap="round"/>
    <!-- Center table -->
    <rect x="248" y="138" width="124" height="12" rx="5" fill="#5c6bc0"/>
    <rect x="265" y="150" width="10" height="18" rx="3" fill="#5c6bc0"/>
    <rect x="345" y="150" width="10" height="18" rx="3" fill="#5c6bc0"/>

    <!-- ── RIGHT HOST (Sam) ── -->
    <!-- Couch body -->
    <rect x="420" y="130" width="170" height="38" rx="10" fill="#5c6bc0"/>
    <!-- Couch back -->
    <rect x="420" y="100" width="170" height="38" rx="10" fill="#7986cb"/>
    <!-- Couch left arm -->
    <rect x="415" y="108" width="22" height="60" rx="8" fill="#5c6bc0"/>
    <!-- Couch right arm -->
    <rect x="573" y="108" width="22" height="60" rx="8" fill="#5c6bc0"/>
    <!-- Body -->
    <rect x="478" y="88" width="54" height="48" rx="10" fill="#16a085"/>
    <!-- Head -->
    <ellipse cx="505" cy="72" rx="22" ry="24" fill="#f0c27f"/>
    <!-- Hair (longer) -->
    <ellipse cx="505" cy="50" rx="22" ry="9" fill="#1a0a00"/>
    <rect x="483" y="48" width="8" height="22" rx="4" fill="#1a0a00"/>
    <rect x="509" y="48" width="8" height="22" rx="4" fill="#1a0a00"/>
    <!-- Eyes -->
    <circle cx="497" cy="70" r="3" fill="#3b2314"/>
    <circle cx="513" cy="70" r="3" fill="#3b2314"/>
    <!-- Smile -->
    <path d="M 498 80 Q 505 86 512 80" stroke="#3b2314" stroke-width="1.5" fill="none"/>
    <!-- Headphones band -->
    <path d="M 483 68 Q 505 48 527 68" stroke="#222" stroke-width="5" fill="none" stroke-linecap="round"/>
    <!-- Headphone cups -->
    <rect x="478" y="65" width="14" height="20" rx="6" fill="#333"/>
    <rect x="518" y="65" width="14" height="20" rx="6" fill="#333"/>
    <rect x="480" y="67" width="10" height="16" rx="4" fill="#555"/>
    <rect x="520" y="67" width="10" height="16" rx="4" fill="#555"/>
    <!-- Desk mic (left side of Sam = toward center) -->
    <rect x="469" y="120" width="3" height="30" fill="#888"/>
    <line x1="456" y1="150" x2="486" y2="150" stroke="#888" stroke-width="2.5" stroke-linecap="round"/>
    <rect x="462" y="104" width="17" height="28" rx="8" fill="#444"/>
    <rect x="464" y="106" width="13" height="24" rx="6" fill="#666"/>
    <!-- Mic grill lines -->
    <line x1="465" y1="110" x2="476" y2="110" stroke="#888" stroke-width="1" opacity="0.6"/>
    <line x1="465" y1="114" x2="476" y2="114" stroke="#888" stroke-width="1" opacity="0.6"/>
    <line x1="465" y1="118" x2="476" y2="118" stroke="#888" stroke-width="1" opacity="0.6"/>
    <line x1="465" y1="122" x2="476" y2="122" stroke="#888" stroke-width="1" opacity="0.6"/>
    <!-- Sam label -->
    <text x="505" y="190" text-anchor="middle" fill="#3949ab" font-family="Arial" font-size="13" font-weight="bold">Sam</text>
  </svg>
</div>
"""

with gr.Blocks(title="PodcastIQ", css="""
    .gradio-container { background: #f5f7ff !important; }
    .gr-button-primary { background: #c0392b !important; border: none !important; }
    footer { display: none !important; }
""") as demo:
    gr.HTML(STUDIO_SVG)

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Input")

            source_type = gr.Radio(
                choices=["Text", "URL", "YouTube", "PDF"],
                value="Text",
                label="Source Type",
            )

            text_input = gr.Textbox(
                label="Paste text",
                lines=6,
                placeholder="Paste any article, notes, or content about AI startups...",
                visible=True,
            )
            url_input = gr.Textbox(
                label="Article URL",
                placeholder="https://techcrunch.com/...",
                visible=False,
            )
            youtube_input = gr.Textbox(
                label="YouTube URL",
                placeholder="https://www.youtube.com/watch?v=...",
                visible=False,
            )
            pdf_input = gr.Textbox(
                label="PDF file path",
                placeholder="/path/to/file.pdf",
                visible=False,
            )

            def toggle_inputs(choice):
                return (
                    gr.update(visible=choice == "Text"),
                    gr.update(visible=choice == "URL"),
                    gr.update(visible=choice == "YouTube"),
                    gr.update(visible=choice == "PDF"),
                )

            source_type.change(
                toggle_inputs,
                inputs=source_type,
                outputs=[text_input, url_input, youtube_input, pdf_input],
            )

            gr.Markdown("### Settings")

            style = gr.Dropdown(
                choices=["Educational", "Debate", "News Brief", "Deep Dive"],
                value="Educational",
                label="Podcast Style",
            )

            with gr.Row():
                host_a = gr.Textbox(label="Host A name", value="Alex", scale=1)
                host_b = gr.Textbox(label="Host B name", value="Sam", scale=1)

            duration = gr.Slider(minimum=2, maximum=10, value=5, step=1, label="Target length (minutes)")

            generate_btn = gr.Button("Generate Episode", variant="primary", size="lg")

        with gr.Column(scale=1):
            gr.Markdown("### Output")

            stats_box = gr.Textbox(label="Stats", interactive=False, lines=1)
            audio_player = gr.Audio(label="Episode Audio", type="filepath")
            download_btn = gr.File(label="Download MP3")

            with gr.Accordion("Episode Metadata", open=True):
                metadata_box = gr.Textbox(label="", interactive=False, lines=4)

            with gr.Accordion("Full Script", open=False):
                script_box = gr.Textbox(label="", interactive=False, lines=20)

    generate_btn.click(
        fn=run_pipeline,
        inputs=[source_type, text_input, url_input, youtube_input, pdf_input,
                style, host_a, host_b, duration],
        outputs=[audio_player, script_box, metadata_box, stats_box, download_btn],
    )

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())
