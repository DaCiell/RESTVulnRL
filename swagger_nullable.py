import yaml
import argparse


def remove_nullable(input_file, output_file):
    with open(input_file, 'r') as file:
        data = yaml.safe_load(file)

    def remove_nullable_recursive(d):
        if isinstance(d, dict):
            d.pop('nullable', None)
            for key, value in d.items():
                remove_nullable_recursive(value)
        elif isinstance(d, list):
            for item in d:
                remove_nullable_recursive(item)

    remove_nullable_recursive(data)

    with open(output_file, 'w') as file:
        yaml.dump(data, file, sort_keys=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove 'nullable' fields from a YAML file.")
    parser.add_argument("input_file", help="Path to the input YAML file")
    parser.add_argument("output_file", help="Path to the output YAML file")
    args = parser.parse_args()

    remove_nullable(args.input_file, args.output_file)
    print(f"Processed {args.input_file} and saved as {args.output_file}.")
