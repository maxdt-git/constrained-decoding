from llm_sdk import Small_LLM_Model
from src.models import FunctionDefinition
# from src.vocab import load_vocab
# from pathlib import Path


def valid_token_id(
        vocab: dict[int, str],
        generated_text: str,
        candidates: list[str],
) -> set[int]:
    """
    Create a set of valid token
    """

    # keep only tokens that still lead to at least one candidate name
    valid: set[int] = set()
    for token_id, token_text in vocab.items():
        combined = generated_text + token_text
        for name in candidates:
            if name.startswith(combined):
                valid.add(token_id)

    return valid


def generate_from_candidate(
        model: Small_LLM_Model,
        vocab: dict[int, str],
        input_ids: list[int],
        candidates: list[str],
) -> str:
    """
    Generate text token by token, constrained to match one of the candidates.
    """

    generated_text = ""
    candidates = list(candidates)

    # generate one token at a time, staying inside the candidate names
    while True:
        logits = model.get_logits_from_input_ids(input_ids)
        valid = valid_token_id(vocab, generated_text, candidates)
        if not valid:
            raise RuntimeError("No valid token found")

        # pick the best token among the valid ones only
        best_id = max(valid, key=lambda token_id: logits[token_id])
        input_ids.append(best_id)
        generated_text += vocab[best_id]

        # narrow down the candidates still matching what we generated
        candidates = [c for c in candidates if c.startswith(generated_text)]

        # stop once generated_text is one full, unambiguous function name
        if len(candidates) == 1 and candidates[0] == generated_text:
            break

    return generated_text


def chose_function_name(
        model: Small_LLM_Model,
        vocab: dict[int, str],
        prompt: str,
        functions: list[FunctionDefinition],
) -> tuple[str, list[int]]:
    """
    Chose function name for the given prompt using constrained decoding
    """

    full_prompt = build_function_selection_prompt(prompt, functions)
    input_ids: list[int] = model.encode(full_prompt).tolist()[0]
    function_names = [function.name for function in functions]
    name = generate_from_candidate(model, vocab, input_ids, function_names)
    return name, input_ids


def build_function_selection_prompt(
        prompt: str,
        functions: list[FunctionDefinition]
) -> str:
    """
    Build a prompt listing the available functions for the model
    """

    result: list[str] = []
    for function in functions:
        result.append(f"- {function.name}: {function.description}")
    descriptions = "\n".join(result)

    return ("You are a function-calling assistant. Choose the single function "
            "that best answers the user request.\n\n"
            f"Available functions:\n {descriptions}\n\n"
            f"User request: {prompt}\n"
            "Function to call: ")


# if __name__ == "__main__":
#     model = Small_LLM_Model()
#     vocab_path = model.get_path_to_vocab_file()
#     vocab = load_vocab(Path(vocab_path))
#     valid = valid_token_id(
# vocab, generated_text="", candidates=["fn_add_numbers", "fn_greet"])
#     chosen = chose_function_name(
# model, vocab, "What is the sum of 2 and 3?",
# ["fn_add_numbers", "fn_greet", "fn_reverse_string"])
#     print(chosen)
