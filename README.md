# Monitor-PC

A lightweight Python-based background PC monitoring and live-streaming utility designed to stream screen updates seamlessly via Discord Webhooks using memory streaming.

## Features
- **Background Execution:** Runs silently and persistently in the background.
- **Memory Streaming:** Captures and streams live screen updates without saving heavy temporary files to the disk.
- **Discord Integration:** Sends real-time feed directly to a configured Discord channel using Webhooks.

## Tech Stack
- **Language:** Python
- **Libraries:** OpenCV, PyAutoGUI, requests (or relevant streaming libraries)
- **Delivery:** Discord Webhooks

## Usage
1. Configure your Discord Webhook URL in the script.
2. Run `updates.pyw` in a Python environment or compile it into an executable.
