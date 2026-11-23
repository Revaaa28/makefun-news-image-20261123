"""make.fun news-image-20261123 entry program (Python 3.13, standard library only).

The entry image is the entry.png committed beside this file; the program copies
it to the output directory. Outside the grader's container, MAKEFUN_OUTPUT_DIR
stands in for /output:

    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

The environment is read as data only (one directory name); no code is ever
loaded from it. The copy is byte-for-byte, so two runs write identical bytes.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")


def main() -> int:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SOURCE, target)
    # Self-check: the copy must be the same size as the committed image, so a
    # truncated write can never reach the gate unnoticed.
    if os.path.getsize(target) != os.path.getsize(SOURCE):
        raise IOError("copied entry.png differs in size from the source")
    return 0


if __name__ == "__main__":
    sys.exit(main())
