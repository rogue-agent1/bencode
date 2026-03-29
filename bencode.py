#!/usr/bin/env python3
"""Bencode encoder/decoder (BitTorrent)."""

def encode(obj) -> bytes:
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
    raise TypeError(f"Cannot bencode {type(obj)}")

def decode(data: bytes):
    val, _ = _decode(data, 0)
    return val

def _decode(data, pos):
    if data[pos:pos+1] == b"i":
        end = data.index(b"e", pos)
        return int(data[pos+1:end]), end + 1
    if data[pos:pos+1] == b"l":
        pos += 1; items = []
        while data[pos:pos+1] != b"e":
            val, pos = _decode(data, pos)
            items.append(val)
        return items, pos + 1
    if data[pos:pos+1] == b"d":
        pos += 1; d = {}
        while data[pos:pos+1] != b"e":
            key, pos = _decode(data, pos)
            val, pos = _decode(data, pos)
            d[key if isinstance(key, str) else key.decode()] = val
        return d, pos + 1
    # String
    colon = data.index(b":", pos)
    length = int(data[pos:colon])
    start = colon + 1
    return data[start:start+length], start + length

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], "rb") as f:
            print(decode(f.read()))

def test():
    assert encode(42) == b"i42e"
    assert encode("hello") == b"5:hello"
    assert encode([1, "a"]) == b"li1e1:ae"
    assert encode({"b": 2, "a": 1}) == b"d1:ai1e1:bi2ee"
    assert decode(b"i42e") == 42
    assert decode(b"5:hello") == b"hello"
    assert decode(b"li1e1:ae") == [1, b"a"]
    assert decode(b"d1:ai1e1:bi2ee") == {"a": 1, "b": 2}
    # Round-trip
    obj = {"name": "test", "pieces": [1, 2, 3]}
    assert decode(encode(obj)) == {"name": b"test", "pieces": [1, 2, 3]}
    print("  bencode: ALL TESTS PASSED")
