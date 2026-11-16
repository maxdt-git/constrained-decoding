from llm_sdk import Small_LLM_Model
from src.models import FunctionDefinition
from src.chose_function import generate_from_candidate


def is_valid_number_token(
        token_text: str,
        generated: str) -> bool:
    """
    Check if token_text is the continuation of number in generated
    """

    if generated == "":
        if token_text != "-" and not token_text.isdigit():
            return False
        return True
    if generated == "-":
        if not token_text.isdigit():
            return False
        return True
    if "." not in generated:
        if token_text != "." and not token_text.isdigit():
            return False
        return True
    if "." in generated:
        if not token_text.isdigit():
            return False
        return True

    return False


def generate_number_value(
        model: Small_LLM_Model,
        vocab: dict[int, str],
        input_ids: list[int],
) -> int | float:
    """
    Generate a numeric parameter using constrained decoding
    """

    generated: str = ""
    while True:
        logits = model.get_logits_from_input_ids(input_ids)
        best_unconstrained = logits.index(max(logits))
        token_text = vocab[best_unconstrained]
        if is_valid_number_token(token_text, generated):
            input_ids.append(best_unconstrained)
            generated += token_text

        elif generated and generated not in ("-", "") \
                and not generated.endswith("."):
            break
        else:
            valid: dict[int, str] = {}
            for token_id, text in vocab.items():
                if is_valid_number_token(text, generated):
                    valid[token_id] = text
            best_id = max(valid, key=lambda token_id: logits[token_id])
            input_ids.append(best_id)
            generated += valid[best_id]

    if "." in generated:
        return float(generated)
    return int(generated)


def build_number_prompt(
        prompt: str,
        function: FunctionDefinition,
        parameter_name: str
) -> str:
    """
    Build a prompt so can now which number parameter
    """
    return (
        f"Function: {function.name} - {function.description}\n\n"
        f"User request: {prompt}\n"
        f"Parameter '{parameter_name}' (number): "
    )


def build_string_prompt(
        prompt: str,
        function: FunctionDefinition,
        parameter_name: str,
) -> str:
    """
    Build a prompt for a string parameter
    """
    other_params = ", ".join(function.parameters.keys())
    return (
        f"Extract or infer the correct value of parameter '{parameter_name}' "
        "for this function call. If the value appears literally in the user "
        "request, copy it exactly. If it must be expressed as a pattern "
        "(e.g. a regular expression) matching the description, provide that "
        "pattern instead.\n\n"
        f"Parameters: {other_params}\n\n"
        f"Function: {function.name} - {function.description}\n\n"
        f"User request: {prompt}\n"
        f"Parameter '{parameter_name}' (string): \""
    )


def generate_string_value(
        model: Small_LLM_Model,
        vocab: dict[int, str],
        input_ids: list[int],
        max_tokens: int = 50,
) -> str:
    """
    Generate a string parameter stopping at "
    """
    generated = ""
    for _ in range(max_tokens):
        logits = model.get_logits_from_input_ids(input_ids)
        best_id = logits.index(max(logits))
        token_text = vocab[best_id]
        if '"' in token_text:
            break
        else:
            input_ids.append(best_id)
            generated += vocab[best_id]

    return generated


def generate_bool_value(
        model: Small_LLM_Model,
        vocab: dict[int, str],
        input_ids: list[int],
) -> bool:
    """
    Generate a boolean value by choosing between "true" and "false".
    """

    text = generate_from_candidate(model, vocab, input_ids, ["true", "false"])
    return text == "true"


def build_bool_prompt(
        prompt: str,
        function: FunctionDefinition,
        parameter_name: str,
) -> str:
    """
    Build a prompt for bool value
    """
    return (
        f"Function: {function.name} - {function.description}\n\n"
        f"User request: {prompt}\n"
        f"Parameter '{parameter_name}' (boolean): ")


def generate_parameter_value(
        model: Small_LLM_Model,
        vocab: dict[int, str],
        prompt: str,
        function: FunctionDefinition,
        parameter_name: str,
        parameter_type: str,
) -> int | float | str | bool:
    """
    Generate one parameter with good type
    """
    if parameter_type == "number":
        param_prompt = build_number_prompt(prompt, function, parameter_name)
        input_ids = model.encode(param_prompt).tolist()[0]
        return generate_number_value(model, vocab, input_ids)

    if parameter_type == "string":
        param_prompt = build_string_prompt(prompt, function, parameter_name)
        input_ids = model.encode(param_prompt).tolist()[0]
        return generate_string_value(model, vocab, input_ids)

    if parameter_type == "boolean":
        param_prompt = build_bool_prompt(prompt, function, parameter_name)
        input_ids = model.encode(param_prompt).tolist()[0]
        return generate_bool_value(model, vocab, input_ids)

    raise ValueError("Wrong parameter type")
