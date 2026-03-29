#!/usr/bin/env python3
"""bencode: BitTorrent bencoding encoder/decoder."""
import sys

def encode(obj):
    if isinstance(obj, int):
        return f"i{obj}e".encode()
    if isinstance(obj, bytes):
        return f"{len(obj)}:".encode() + obj
    if isinstance(obj, str):
        b = obj.encode()
        return f"{len(b)}:".encode() + b
    if isinstance(obj, list):
        return b"l" + b"".join(encode(i) for i in obj) + b"e"
    if isinstance(obj, dict):
        items = sorted(obj.items(), key=lambda x: x[0].encode() if isinstance(x[0], str) else x[0])
        return b"d" + b"".join(encode(k) + encode(v) for k, v in items) + b"e"
    raise TypeError(f"Cannot encode {type(obj)}")

def decode(data, idx=0):
    if data[idx:idx+1] == b"i":
        end = data.index(b"e", idx)
        return int(data[idx+1:end]), end + 1
    if data[idx:idx+1] == b"l":
        result, idx = [], idx + 1
        while data[idx:idx+1] != b"e":
            val, idx = decode(data, idx)
            result.append(val)
        return result, idx + 1
    if data[idx:idx+1] == b"d":
        result, idx = {}, idx + 1
        while data[idx:idx+1] != b"e":
            key, idx = decode(data, idx)
            val, idx = decode(data, idx)
            result[key] = val
        return result, idx + 1
    colon = data.index(b":", idx)
    length = int(data[idx:colon])
    start = colon + 1
    return data[start:start+length], start + length

def test():
    # Integers
    assert encode(42) == b"i42e"
    assert encode(-3) == b"i-3e"
    assert decode(b"i42e")[0] == 42
    # Strings
    assert encode("spam") == b"4:spam"
    assert decode(b"4:spam")[0] == b"spam"
    # Lists
    assert encode(["spam", 42]) == b"l4:spami42ee"
    val, _ = decode(b"l4:spami42ee")
    assert val == [b"spam", 42]
    # Dicts
    enc = encode({"cow": "moo", "age": 3})
    val, _ = decode(enc)
    assert val[b"age"] == 3
    assert val[b"cow"] == b"moo"
    # Roundtrip
    obj = {"info": {"name": "test", "length": 1024}, "announce": "http://tracker"}
    data = encode(obj)
    decoded, _ = decode(data)
    assert decoded[b"announce"] == b"http://tracker"
    print("All tests passed!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test": test()
    else: print("Usage: bencode.py test")
