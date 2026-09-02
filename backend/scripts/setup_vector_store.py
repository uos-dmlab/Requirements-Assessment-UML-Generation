#!/usr/bin/env python3
"""
One-time script to create Vector Store with PlantUML documentation.
Run ONCE when setting up the project.

After execution, save vector_store_id to .env
"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from openai import OpenAI
except ImportError:
    print("[ERROR] OpenAI package not installed. Run: pip install openai")
    sys.exit(1)

PDF_PATH = Path(__file__).parent.parent / "resources" / "PlantUML_Language_Reference_Guide_en.pdf"


def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("[ERROR] OPENAI_API_KEY environment variable not set")
        print("  Set it with: export OPENAI_API_KEY=sk-...")
        return

    client = OpenAI(api_key=api_key)

    print("OpenAI Vector Store Setup for PlantUML RAG")
    print("-" * 50)

    if not PDF_PATH.exists():
        print(f"[ERROR] PDF not found at: {PDF_PATH}")
        print("  Please copy PlantUML_Language_Reference_Guide_en.pdf to resources/")
        print()
        print("  Download from:")
        print("  https://pdf.plantuml.net/PlantUML_Language_Reference_Guide_en.pdf")
        return

    print(f"[OK] Found PDF: {PDF_PATH}")
    print(f"  Size: {PDF_PATH.stat().st_size / 1024 / 1024:.1f} MB")

    print("\nUploading PDF to OpenAI...")

    with open(PDF_PATH, "rb") as f:
        file = client.files.create(
            file=f,
            purpose="assistants"
        )

    print(f"[OK] File uploaded: {file.id}")

    print("\nCreating Vector Store...")

    vector_store = client.beta.vector_stores.create(
        name="PlantUML Reference Documentation",
        file_ids=[file.id],
        chunking_strategy={
            "type": "static",
            "static": {
                "max_chunk_size_tokens": 1200,
                "chunk_overlap_tokens": 400
            }
        }
    )

    print(f"[OK] Vector Store created: {vector_store.id}")
    print(f"  Name: {vector_store.name}")
    print(f"  Status: {vector_store.status}")

    print("\nWaiting for processing...")

    while True:
        vs = client.beta.vector_stores.retrieve(vector_store.id)
        if vs.status == "completed":
            break
        elif vs.status == "failed":
            print(f"[ERROR] Processing failed: {vs.last_error}")
            return
        print(f"  Status: {vs.status}...")
        time.sleep(2)

    print("\n[OK] Setup complete!")
    print(f"\nVector Store ID: {vector_store.id}")
    print(f"\nAdd this to your .env file:")
    print(f"PLANTUML_VECTOR_STORE_ID={vector_store.id}")


if __name__ == "__main__":
    main()
