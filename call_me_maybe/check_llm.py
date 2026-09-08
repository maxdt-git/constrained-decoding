from llm_sdk import Small_LLM_Model


def main() -> None:
    model = Small_LLM_Model()

    prompt = "What is the sum of 2 and 3?"
    input_ids = model.encode(prompt)
    input_ids = input_ids.tolist()[0]
    print(input_ids)

    generated: list[int] = []
    for _ in range(20):
        context = input_ids + generated
        logits = model.get_logits_from_input_ids(context)
        next_id = logits.index(max(logits))
        generated.append(next_id)

    print(model.decode(generated))

    vocab_path = model.get_path_to_vocab_file()
    print(vocab_path)


if __name__ == "__main__":
    main()
