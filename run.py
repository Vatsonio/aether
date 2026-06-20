#!/usr/bin/env python3
"""Convenience runner for Aether dashboard."""

import uvicorn
import os

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    port = int(os.environ.get("PORT", "8090"))
    uvicorn.run("backend.app:app", host="0.0.0.0", port=port, reload=True)
