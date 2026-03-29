#!/usr/bin/env python3
"""bencode - BitTorrent bencoding encoder and decoder."""
import sys

def encode(val):
    if isinstance(val, int): return f"i{val}e".encode()
    if isinstance(val, bytes): return f"{len(val)}:".encode() + val
    if isinstance(val, str): return encode(val.encode())
    if isinstance(val, list): return b"l" + b"".join(encode(v) for v in val) + b"e"
    if isinstance(val, dict):
        items = sorted(val.items(), key=lambda x: x[0] if isinstance(x[0], bytes) else x[0].encode())
        return b"d" + b"".join(encode(k) + encode(v) for k, v in items) + b"e"
    raise TypeError(f"Cannot encode {type(val)}")

def decode(data):
    if isinstance(data, str): data = data.encode()
    val, _ = _decode(data, 0)
    return val

def _decode(data, i):
    if data[i:i+1] == b"i":
        end = data.index(b"e", i)
        return int(data[i+1:end]), end + 1
    if data[i:i+1] == b"l":
        lst, i = [], i + 1
        while data[i:i+1] != b"e":
            val, i = _decode(data, i)
            lst.append(val)
        return lst, i + 1
    if data[i:i+1] == b"d":
        d, i = {}, i + 1
        while data[i:i+1] != b"e":
            key, i = _decode(data, i)
            val, i = _decode(data, i)
            d[key] = val
        return d, i + 1
    colon = data.index(b":", i)
    n = int(data[i:colon])
    s = data[colon+1:colon+1+n]
    return s, colon + 1 + n

def test():
    assert encode(42) == b"i42e"
    assert encode("hello") == b"5:hello"
    assert encode([1, "two"]) == b"li1e3:twoe"
    assert encode({"a": 1, "b": 2}) == b"d1:ai1e1:bi2ee"
    assert decode(b"i42e") == 42
    assert decode(b"5:hello") == b"hello"
    assert decode(b"li1e3:twoe") == [1, b"two"]
    d = decode(b"d1:ai1e1:bi2ee")
    assert d[b"a"] == 1
    roundtrip = decode(encode({"key": [1, 2, 3]}))
    assert roundtrip[b"key"] == [1, 2, 3]
    print("bencode: all tests passed")

if __name__ == "__main__":
    test() if "--test" in sys.argv else print("Usage: bencode.py --test")
