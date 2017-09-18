#!/usr/bin/env python3
import sys

if __package__ is None and not hasattr(sys, "frozen"):
    # directly call __main__.py
    import os.path
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))

import chyoa

if __name__ == "__main__":
    chyoa.main(sys.argv)

