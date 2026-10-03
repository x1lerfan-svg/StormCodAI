import sys

from .cli import main as cli_main
from .server import main as server_main


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in {"serve", "web"}:
        server_main()
    else:
        cli_main()
