# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a tutorial repository for **Cohere Transcribe (cohere-transcribe-03-2026)**, an open-source ASR model. The tutorial provides hands-on guidance for AI engineers covering basic file transcription, multilingual support, long-form/batched inference, real-time microphone streaming, web demo (Gradio), and production deployment.

## Repository Structure

- `tutorial.MD` — Complete tutorial with 9 steps: environment setup, basic transcription, multilingual/punctuation control, long-form inference, real-time streaming, Gradio web demo, vLLM/API deployment, benchmarking, and troubleshooting.

## Key Technical Details

- **Model**: `CohereLabs/cohere-transcribe-03-2026` (2B-param Conformer-based ASR)
- **Requirements**: `transformers>=5.4.0`, `torch`, `huggingface_hub`, `soundfile`, `librosa`, `sentencepiece`, `protobuf`, `datasets`, `gradio`, `sounddevice`
- **Supported languages**: en, fr, de, it, es, pt, el, nl, pl, ar, vi, zh, ja, ko
- **Hardware**: GPU recommended (8GB+ VRAM); works on CPU with slower inference
- **License**: Apache 2.0

## Common Tasks

This is a documentation/tutorial repository — no build or test commands apply.
