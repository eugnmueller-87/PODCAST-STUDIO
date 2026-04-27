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
            source = pdf_input if isinstance(pdf_input, str) else (pdf_input.name if pdf_input else None)

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
<div style="background:linear-gradient(160deg,#2d2640 0%,#1e1a30 100%);border-radius:16px;padding:20px 24px 12px;margin-bottom:20px;text-align:center;border:1px solid #4a3f6a;">
  <div style="font-size:2rem;font-weight:900;color:#fff;letter-spacing:3px;text-shadow:0 0 20px #ff4da6;">🎙️ PodcastIQ</div>
  <div style="color:#c4b8e8;font-size:0.9rem;margin-top:4px;margin-bottom:16px;letter-spacing:1px;">Turn any content about AI into a two-host podcast episode</div>
  <svg viewBox="0 0 800 300" xmlns="http://www.w3.org/2000/svg" style="max-width:780px;width:100%;">
    <defs>
      <radialGradient id="bgG" cx="50%" cy="35%" r="55%">
        <stop offset="0%" stop-color="#3d3060"/>
        <stop offset="100%" stop-color="#1a1630"/>
      </radialGradient>
      <filter id="neon" x="-80%" y="-80%" width="260%" height="260%">
        <feGaussianBlur stdDeviation="4" result="b1"/>
        <feGaussianBlur stdDeviation="8" result="b2"/>
        <feMerge><feMergeNode in="b2"/><feMergeNode in="b1"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
      <filter id="warm" x="-60%" y="-60%" width="220%" height="220%">
        <feGaussianBlur stdDeviation="10" result="blur"/>
        <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
    </defs>

    <!-- Background -->
    <rect width="800" height="300" fill="#1e1a30"/>
    <rect width="800" height="300" fill="url(#bgG)"/>
    <rect x="0" y="0" width="800" height="190" fill="#2a2440" opacity="0.5"/>

    <!-- Edison bulb top right -->
    <line x1="718" y1="0" x2="718" y2="38" stroke="#7a5c14" stroke-width="3"/>
    <ellipse cx="718" cy="52" rx="13" ry="17" fill="#f9c74f" filter="url(#warm)" opacity="0.85"/>
    <ellipse cx="718" cy="52" rx="13" ry="17" fill="#f9e07a" opacity="0.3"/>
    <line x1="710" y1="65" x2="726" y2="65" stroke="#9a8050" stroke-width="3"/>

    <!-- Sign top right -->
    <rect x="698" y="74" width="88" height="82" rx="4" fill="#f0e8d0" stroke="#c8a87a" stroke-width="1.5"/>
    <text x="742" y="95"  text-anchor="middle" fill="#222" font-family="Arial" font-weight="bold" font-size="9">LISTEN</text>
    <text x="742" y="109" text-anchor="middle" fill="#222" font-family="Arial" font-weight="bold" font-size="9">LAUGH</text>
    <text x="742" y="123" text-anchor="middle" fill="#222" font-family="Arial" font-weight="bold" font-size="9">LEARN</text>
    <text x="742" y="137" text-anchor="middle" fill="#222" font-family="Arial" font-weight="bold" font-size="9">REPEAT</text>

    <!-- Left shelf -->
    <rect x="14" y="108" width="118" height="6" rx="2" fill="#5c3d1e"/>
    <rect x="18"  y="82" width="11" height="27" rx="1" fill="#c0392b"/>
    <rect x="30"  y="79" width="9"  height="30" rx="1" fill="#2471a3"/>
    <rect x="40"  y="85" width="8"  height="24" rx="1" fill="#1e8449"/>
    <rect x="49"  y="80" width="10" height="29" rx="1" fill="#7d3c98"/>
    <rect x="60"  y="84" width="9"  height="25" rx="1" fill="#d35400"/>
    <!-- Plant on shelf -->
    <rect x="82" y="88" width="18" height="20" rx="2" fill="#7a5c3a"/>
    <ellipse cx="91" cy="86" rx="13" ry="11" fill="#1b4332"/>
    <ellipse cx="84" cy="81" rx="7"  ry="8"  fill="#2d6a4f"/>
    <ellipse cx="98" cy="81" rx="7"  ry="8"  fill="#40916c"/>

    <!-- "stay curious" -->
    <text x="20" y="130" fill="#5a4a7a" font-family="Georgia,serif" font-style="italic" font-size="11">stay curious</text>

    <!-- Neon ON AIR speech bubble -->
    <path d="M 308 8 Q 308 0 318 0 L 482 0 Q 492 0 492 10 L 492 55 Q 492 65 482 65 L 415 65 L 400 82 L 385 65 L 318 65 Q 308 65 308 55 Z"
          fill="none" stroke="#ff4da6" stroke-width="2.5" filter="url(#neon)" opacity="0.95"/>
    <text x="400" y="30" text-anchor="middle" fill="#ff4da6" font-family="Georgia,serif" font-style="italic" font-size="22" font-weight="bold" filter="url(#neon)">on</text>
    <text x="400" y="56" text-anchor="middle" fill="#ff4da6" font-family="Georgia,serif" font-style="italic" font-size="22" font-weight="bold" filter="url(#neon)">air</text>

    <!-- ── DESK ── -->
    <rect x="60" y="218" width="680" height="14" rx="4" fill="#7a5230"/>
    <rect x="60" y="232" width="680" height="60" fill="#5c3d1e"/>
    <rect x="60" y="218" width="680" height="3"  rx="2" fill="#a07848"/>

    <!-- ── LEFT HOST (Alex — woman) ── -->
    <!-- Body dark sweater -->
    <rect x="105" y="158" width="66" height="63" rx="14" fill="#1a1a2e"/>
    <!-- Neck -->
    <rect x="130" y="145" width="22" height="18" rx="5" fill="#c68642"/>
    <!-- Head -->
    <ellipse cx="141" cy="128" rx="30" ry="32" fill="#c68642"/>
    <!-- Hair bun -->
    <ellipse cx="141" cy="105" rx="30" ry="16" fill="#4a2512"/>
    <ellipse cx="141" cy="92"  rx="15" ry="13" fill="#5c3018"/>
    <rect x="112" y="100" width="9" height="28" rx="4" fill="#4a2512"/>
    <rect x="161" y="100" width="9" height="28" rx="4" fill="#4a2512"/>
    <!-- Eyes -->
    <ellipse cx="131" cy="126" rx="5" ry="5.5" fill="#fff" opacity="0.9"/>
    <ellipse cx="151" cy="126" rx="5" ry="5.5" fill="#fff" opacity="0.9"/>
    <circle cx="131" cy="127" r="3" fill="#2c1810"/>
    <circle cx="151" cy="127" r="3" fill="#2c1810"/>
    <!-- Smile -->
    <path d="M 132 140 Q 141 148 150 140" stroke="#a0391a" stroke-width="2" fill="#d4705a" stroke-linecap="round"/>
    <!-- Earring -->
    <circle cx="111" cy="130" r="4" fill="#d4a017"/>
    <!-- Headphones -->
    <path d="M 111 117 Q 141 90 171 117" stroke="#111" stroke-width="7" fill="none" stroke-linecap="round"/>
    <rect x="104" y="113" width="15" height="22" rx="6" fill="#1e1e1e"/>
    <rect x="163" y="113" width="15" height="22" rx="6" fill="#1e1e1e"/>
    <rect x="106" y="115" width="11" height="18" rx="4" fill="#3a3a3a"/>
    <rect x="165" y="115" width="11" height="18" rx="4" fill="#3a3a3a"/>
    <!-- Angled desk mic left -->
    <ellipse cx="215" cy="225" rx="20" ry="5" fill="#2a2a2a"/>
    <line x1="215" y1="224" x2="198" y2="172" stroke="#333" stroke-width="6" stroke-linecap="round"/>
    <rect x="186" y="154" width="24" height="36" rx="11" fill="#1e1e1e"/>
    <rect x="188" y="156" width="20" height="32" rx="9" fill="#333"/>
    <line x1="189" y1="163" x2="207" y2="163" stroke="#666" stroke-width="1.2" opacity="0.7"/>
    <line x1="189" y1="169" x2="207" y2="169" stroke="#666" stroke-width="1.2" opacity="0.7"/>
    <line x1="189" y1="175" x2="207" y2="175" stroke="#666" stroke-width="1.2" opacity="0.7"/>
    <line x1="189" y1="181" x2="207" y2="181" stroke="#666" stroke-width="1.2" opacity="0.7"/>
    <!-- Coffee mug -->
    <rect x="255" y="200" width="33" height="36" rx="5" fill="#111"/>
    <path d="M 288 208 Q 298 208 298 216 Q 298 224 288 224" stroke="#111" stroke-width="3" fill="none"/>
    <text x="271" y="215" text-anchor="middle" fill="#555" font-family="Georgia,serif" font-style="italic" font-size="6">good</text>
    <text x="271" y="223" text-anchor="middle" fill="#555" font-family="Georgia,serif" font-style="italic" font-size="6">vibes ♡</text>

    <!-- ── LAPTOP (center) ── -->
    <rect x="328" y="158" width="144" height="96" rx="8" fill="#1e1e2e"/>
    <rect x="334" y="163" width="132" height="80" rx="5" fill="#0a0a22"/>
    <circle cx="400" cy="161" r="2" fill="#2a2a3a"/>
    <!-- Glowing screen content -->
    <rect x="340" y="170" width="120" height="2" rx="1" fill="#3a3aaa" opacity="0.5"/>
    <rect x="345" y="177" width="80"  height="2" rx="1" fill="#3a3aaa" opacity="0.35"/>
    <rect x="345" y="184" width="95"  height="2" rx="1" fill="#3a3aaa" opacity="0.35"/>
    <text x="400" y="214" text-anchor="middle" fill="#5577cc" font-family="Arial" font-size="9" opacity="0.9">good</text>
    <text x="400" y="226" text-anchor="middle" fill="#5577cc" font-family="Arial" font-size="9" opacity="0.9">conversations</text>
    <!-- Laptop base -->
    <rect x="308" y="252" width="184" height="8" rx="4" fill="#18182a"/>

    <!-- ── RIGHT HOST (Sam — man) ── -->
    <!-- Body dark jacket -->
    <rect x="629" y="158" width="66" height="63" rx="14" fill="#1a2a1a"/>
    <!-- Neck -->
    <rect x="648" y="145" width="22" height="18" rx="5" fill="#b07040"/>
    <!-- Head -->
    <ellipse cx="659" cy="128" rx="30" ry="32" fill="#b07040"/>
    <!-- Curly hair -->
    <ellipse cx="659" cy="103" rx="32" ry="18" fill="#3a1e0a"/>
    <ellipse cx="641" cy="110" rx="11" ry="13" fill="#4a2610"/>
    <ellipse cx="677" cy="110" rx="11" ry="13" fill="#4a2610"/>
    <ellipse cx="649" cy="97"  rx="11" ry="11" fill="#552e12"/>
    <ellipse cx="669" cy="96"  rx="11" ry="11" fill="#552e12"/>
    <ellipse cx="659" cy="93"  rx="10" ry="10" fill="#4a2610"/>
    <!-- Beard -->
    <ellipse cx="659" cy="149" rx="20" ry="9" fill="#3a1e0a" opacity="0.75"/>
    <!-- Eyes -->
    <ellipse cx="649" cy="126" rx="5" ry="5.5" fill="#fff" opacity="0.9"/>
    <ellipse cx="669" cy="126" rx="5" ry="5.5" fill="#fff" opacity="0.9"/>
    <circle cx="649" cy="127" r="3" fill="#2c1810"/>
    <circle cx="669" cy="127" r="3" fill="#2c1810"/>
    <!-- Glasses -->
    <rect x="640" y="119" width="15" height="12" rx="4" fill="none" stroke="#222" stroke-width="2.5"/>
    <rect x="662" y="119" width="15" height="12" rx="4" fill="none" stroke="#222" stroke-width="2.5"/>
    <line x1="655" y1="124" x2="662" y2="124" stroke="#222" stroke-width="2"/>
    <line x1="640" y1="123" x2="634" y2="125" stroke="#222" stroke-width="2"/>
    <line x1="677" y1="123" x2="683" y2="125" stroke="#222" stroke-width="2"/>
    <!-- Talking smile -->
    <path d="M 649 140 Q 659 149 669 140" stroke="#7a3510" stroke-width="2" fill="#b05030" stroke-linecap="round"/>
    <!-- Headphones -->
    <path d="M 629 117 Q 659 90 689 117" stroke="#111" stroke-width="7" fill="none" stroke-linecap="round"/>
    <rect x="622" y="113" width="15" height="22" rx="6" fill="#1e1e1e"/>
    <rect x="681" y="113" width="15" height="22" rx="6" fill="#1e1e1e"/>
    <rect x="624" y="115" width="11" height="18" rx="4" fill="#3a3a3a"/>
    <rect x="683" y="115" width="11" height="18" rx="4" fill="#3a3a3a"/>
    <!-- Angled desk mic right -->
    <ellipse cx="585" cy="225" rx="20" ry="5" fill="#2a2a2a"/>
    <line x1="585" y1="224" x2="602" y2="172" stroke="#333" stroke-width="6" stroke-linecap="round"/>
    <rect x="590" y="154" width="24" height="36" rx="11" fill="#1e1e1e"/>
    <rect x="592" y="156" width="20" height="32" rx="9" fill="#333"/>
    <line x1="593" y1="163" x2="611" y2="163" stroke="#666" stroke-width="1.2" opacity="0.7"/>
    <line x1="593" y1="169" x2="611" y2="169" stroke="#666" stroke-width="1.2" opacity="0.7"/>
    <line x1="593" y1="175" x2="611" y2="175" stroke="#666" stroke-width="1.2" opacity="0.7"/>
    <line x1="593" y1="181" x2="611" y2="181" stroke="#666" stroke-width="1.2" opacity="0.7"/>
    <!-- Paper coffee cup right -->
    <rect x="500" y="203" width="28" height="33" rx="3" fill="#ede0c4"/>
    <rect x="500" y="203" width="28" height="8"  rx="3" fill="#d4c09a"/>
    <text x="514" y="223" text-anchor="middle" fill="#8B7355" font-family="Georgia,serif" font-style="italic" font-size="5.5">coffee</text>
    <text x="514" y="230" text-anchor="middle" fill="#8B7355" font-family="Georgia,serif" font-style="italic" font-size="5.5">fuels ideas</text>
    <!-- Small desk plant right -->
    <rect x="536" y="206" width="20" height="18" rx="3" fill="#7a5c3a"/>
    <ellipse cx="546" cy="204" rx="12" ry="10" fill="#1b4332"/>
    <ellipse cx="539" cy="199" rx="6"  ry="7"  fill="#2d6a4f"/>
    <ellipse cx="553" cy="199" rx="6"  ry="7"  fill="#40916c"/>

    <!-- Lightboard sign on desk -->
    <rect x="300" y="243" width="96" height="44" rx="3" fill="#f0ead8"/>
    <text x="348" y="261" text-anchor="middle" fill="#2c2c2c" font-family="Arial" font-weight="bold" font-size="7">REAL TALK</text>
    <text x="348" y="272" text-anchor="middle" fill="#2c2c2c" font-family="Arial" font-weight="bold" font-size="7">GOOD PEOPLE</text>
    <text x="348" y="283" text-anchor="middle" fill="#2c2c2c" font-family="Arial" font-weight="bold" font-size="7">GREAT TOPICS</text>

    <!-- Name labels -->
    <text x="141" y="296" text-anchor="middle" fill="#cc88bb" font-family="Arial" font-size="12" font-weight="bold">Alex</text>
    <text x="659" y="296" text-anchor="middle" fill="#cc88bb" font-family="Arial" font-size="12" font-weight="bold">Sam</text>
  </svg>
</div>
"""

with gr.Blocks(title="PodcastIQ", css="""
    .gradio-container { background: #2a2440 !important; color: #e0d8f0 !important; }
    .gr-button-primary { background: linear-gradient(135deg,#ff4da6,#c0392b) !important; border: none !important; font-weight: bold !important; }
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
            pdf_input = gr.File(
                label="Upload PDF",
                file_types=[".pdf"],
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
