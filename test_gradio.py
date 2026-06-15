#!/usr/bin/env python
"""Minimal test to verify Gradio works"""

import gradio as gr

def hello(name):
    return f"Hello, {name}!"

with gr.Blocks() as demo:
    gr.Markdown("# Hello World")
    with gr.Row():
        inp = gr.Textbox(placeholder="Enter name")
        out = gr.Textbox()
    btn = gr.Button("Submit")
    btn.click(hello, inputs=inp, outputs=out)

if __name__ == "__main__":
    print("Starting minimal Gradio test...")
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
