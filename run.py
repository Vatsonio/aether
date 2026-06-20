#!/usr/bin/env python3
"""Convenience runner for Aether dashboard."""

import uvicorn
import os

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8090, reload=True)
