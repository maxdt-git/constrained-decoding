import json
import argparse
from pathlib import Path
from src.loader import load_function_definition, load_prompt
from src.models import FunctionResult
from src.chose_function import chose_function_name
from llm_sdk import Small_LLM_Model
from src.vocab import load_vocab
from src.parameters import generate_parameter_value


def parse_args() -> argparse.Namespace:
    """
    Parse the command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--functions_definition",
        type=Path,
        default=Path("data/input/functions_definition.json"),
        help="Path to the JSON functions_definitions",)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/input/function_calling_tests.json"),
        help="Path to the JSON containing prompts",)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/output/function_calling_results.json"),
        help="Path to write the the resulting function calls",)

    return parser.parse_args()


def main() -> int:
    """
    Run the pipeline: load inputs, generate calls, write output.
    """
    args = parse_args()
    try:
        functions = load_function_definition(args.functions_definition)
        prompts = load_prompt(args.input)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error : {e}")
        return 1

    model = Small_LLM_Model(device="cpu")
    vocab = load_vocab(Path(model.get_path_to_vocab_file()))

    results: list[FunctionResult] = []

    for item in prompts:
        print(f"Processing: {item.prompt}")
        parameters = {}
        name = ""
        try:
            name, _ = chose_function_name(model, vocab, item.prompt, functions)
            function = next(f for f in functions if f.name == name)
            for param_name, param_spec in function.parameters.items():
                parameters[param_name] = generate_parameter_value(
                    model, vocab, item.prompt, function,
                    param_name, param_spec.type)
        except (RuntimeError, ValueError) as e:
            print(f"Error on {item.prompt}: {e}")

        results.append(
            FunctionResult(
                prompt=item.prompt, name=name, parameters=parameters))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as f:
        json.dump([r.model_dump() for r in results], f, indent=2)

    print(f"Wrote {len(results)} results to {args.output}")
    return 0


if __name__ == "__main__":
    main()
