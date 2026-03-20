import argparse
from pathlib import Path

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    Environment = None
    FileSystemLoader = None

# default template environment for tests and runtime
template_env = None
if Environment and FileSystemLoader:
    template_dir = Path(__file__).resolve().parent.parent / "frameworks" / "templates"
    template_env = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=True)


def generate_report(output_format):
    print(f"Generating report in {output_format} format")
    if template_env:
        # no-op: placeholder rendering path for future implementation
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="mr-comment")
    args = parser.parse_args()
    generate_report(args.output)
