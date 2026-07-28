#!/usr/bin/env python3
from pathlib import Path


SOURCE_ROOT = Path("/Users/heytea/Documents/myHeytea/code/tool_file/agent/bug-killer")


def main() -> None:
    print(f"source_root={SOURCE_ROOT}")
    print(f"agents={SOURCE_ROOT / 'agents'}")
    print(f"skills={SOURCE_ROOT / 'skills'}")


if __name__ == "__main__":
    main()
