from llm_sdk import Small_LLM_Model
# from src.vocab import load_vocab
# from pathlib import Path


def valid_token_id(
        vocab: dict[int, str],
        generated_text: str,
        candidates: list[str],
) -> set[int]:

    # keep only tokens that still lead to at least one candidate name
    valid: set[int] = set()
    for token_id, token_text in vocab.items():
        combined = generated_text + token_text
        for name in candidates:
            if name.startswith(combined):
                valid.add(token_id)

    return valid


def chose_function_name(
        model: Small_LLM_Model,
        vocab: dict[int, str],
        prompt: str,
        function_names: list[str],
) -> str:

    input_ids = model.encode(prompt).tolist()[0]
    generated_text = ""
    candidates = list(function_names)

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


# if __name__ == "__main__":
#     model = Small_LLM_Model()
#     vocab_path = model.get_path_to_vocab_file()
#     vocab = load_vocab(Path(vocab_path))
#     valid = valid_token_id(vocab, generated_text="", candidates=["fn_add_numbers", "fn_greet"])
#     chosen = chose_function_name(model, vocab, "What is the sum of 2 and 3?", ["fn_add_numbers", "fn_greet", "fn_reverse_string"])
#     print(chosen)
