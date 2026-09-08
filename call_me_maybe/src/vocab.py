from pathlib import Path
import json
# from llm_sdk import Small_LLM_Model


def load_vocab(path: Path) -> dict[int, str]:
    """
    Load the tokenizer vocabulary and load it to id -> token
    """
    # read vocab.json: token -> id
    with path.open('r') as file:
        raw = json.load(file)

    # invert to id -> token
    use: dict[int, str] = {}

    for key, value in raw.items():
        use[value] = key

    # ascii printable
    first = [c for c in range(ord("!"), ord("~") + 1)]
    # 2 -> latin-1
    second = [c for c in range(ord("¡"), ord("¬") + 1)]
    third = [c for c in range(ord("®"), ord("ÿ") + 1)]
    # concat all
    all_bytes = first + second + third
    # print(len(all_bytes))

    # octet goes from 0 to 255
    mapping: dict[int, str] = {}
    next_code = 256

    for b in range(256):
        if b in all_bytes:
            mapping[b] = chr(b)
        else:
            mapping[b] = chr(next_code)
            next_code += 1

    # invert byte -> char mapping to get char -> byte
    char_to_bytes: dict[str, int] = {}

    for key, value in mapping.items():
        char_to_bytes[value] = key

    # decode each token back to its real text
    result: dict[int, str] = {}

    for key, value in use.items():
        byte_list = [char_to_bytes[c] for c in value]
        raw_bytes = bytes(byte_list)
        # replace: some tokens are only part of a multi-byte char
        decoded = raw_bytes.decode(errors="replace")
        result[key] = decoded

    return result


# if __name__ == "__main__":
    # model = Small_LLM_Model()
    # vocab_path = model.get_path_to_vocab_file()
    # vocab = load_vocab(Path(vocab_path))
    # print(vocab[220])
    # print(vocab[0])
