"""Entry point for the shared v2 audit reportability flow figure."""
import sys

from build_jce_figures import main


if __name__ == "__main__":
    sys.argv[1:1] = ["--figure2"]
    raise SystemExit(main())
