import yaml
import copy
import argparse


def resolve_references(spec):
    resolved_refs = {}

    def resolve_ref(obj, base, current_path=None):
        if current_path is None:
            current_path = []

        if isinstance(obj, dict):
            if '$ref' in obj:
                ref_path = obj['$ref']
                ref_keys = ref_path.lstrip('#/').split('/')

                if ref_path in resolved_refs:
                    return resolved_refs[ref_path]

                resolved = base
                for key in ref_keys:
                    resolved = resolved.get(key)
                    if resolved is None:
                        raise ValueError(f"Invalid reference path: {ref_path}")

                if ref_path in current_path:
                    print(f"Circular reference detected at {ref_path}")
                    return {"$ref": ref_path}

                current_path.append(ref_path)
                resolved_obj = resolve_ref(copy.deepcopy(resolved), base, current_path)
                resolved_refs[ref_path] = resolved_obj
                current_path.pop()
                return resolved_obj
            else:
                return {k: resolve_ref(v, base, current_path) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [resolve_ref(i, base, current_path) for i in obj]
        else:
            return obj

    return resolve_ref(spec, spec)


def main(input_file, output_file):
    with open(input_file, 'r') as file:
        swagger_spec = yaml.safe_load(file)

    resolved_spec = resolve_references(swagger_spec)

    with open(output_file, 'w') as file:
        yaml.dump(resolved_spec, file, sort_keys=False)

    print(f"Reference resolution completed. The resolved YAML has been saved to {output_file}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resolve $ref references in a YAML file.")
    parser.add_argument("input_file", help="Path to the input YAML file")
    parser.add_argument("output_file", help="Path to the output YAML file")
    args = parser.parse_args()

    main(args.input_file, args.output_file)
