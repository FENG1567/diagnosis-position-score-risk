"""Entry point for the four-panel score-specific risk figure."""
import sys

from build_jce_figures import main


if __name__ == "__main__":
    sys.argv[1:1] = ["--figure1"]
    raise SystemExit(main())
