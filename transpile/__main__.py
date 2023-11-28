# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes,
# files, tool windows, actions, and settings.

import argparse
import logging
from pathlib import Path
from transpile import generator

logger = logging.getLogger()


def main():
    # Use a breakpoint in the code line below to debug your script.
    # Press ⌘F8 to toggle the breakpoint.
    parser = argparse.ArgumentParser(description="Process a Python file")

    parser.add_argument("input_file", help="Input file name", type=Path)
    parser.add_argument(
        "-o", "--output", help="Output file name", default=None)
    # parser.add_argument('-v', '--verbose', help='verbose output')
    logging.basicConfig(level=logging.INFO)

    args = parser.parse_args()

    if not args.input_file.exists():
        parser.error("Input file does not exist: {}".format(args.input_file))

    # Process the input file
    processed_contents = generator.to_cpp(args.input_file)
    # Process the file contents
    # ...

    # Write the output to a file if specified
    if args.output:
        with Path(args.output).open("w") as f:
            f.write(processed_contents)


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
