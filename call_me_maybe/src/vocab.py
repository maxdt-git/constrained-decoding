from pathlib import Path
import json


def load_vocab(path: Path) -> dict[int, str]:
    """
    Load the tokenizer vocabulary and load it to id -> token
    """
    
