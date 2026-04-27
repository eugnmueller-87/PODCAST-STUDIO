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


with gr.Blocks(title="PodcastIQ", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # PodcastIQ — AI Startup Podcast Studio
        *Turn any content about AI into a two-host podcast episode.*
        """
    )

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
    demo.launch()
