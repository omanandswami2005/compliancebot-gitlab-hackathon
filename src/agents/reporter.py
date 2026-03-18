import argparse

def generate_report(output_format):
    print(f"Generating report in {output_format} format")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="mr-comment")
    args = parser.parse_args()
    generate_report(args.output)
