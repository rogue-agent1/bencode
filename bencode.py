#!/usr/bin/env python3
"""Bencode encoder/decoder (BitTorrent). Zero dependencies."""
import sys

def encode(obj):
    if isinstance(obj, int): return f"i{obj}e".encode()
    if isinstance(obj, bytes): return f"{len(obj)}:".encode() + obj
    if isinstance(obj, str): b = obj.encode(); return f"{len(b)}:".encode() + b
    if isinstance(obj, list): return b"l" + b"".join(encode(i) for i in obj) + b"e"
    if isinstance(obj, dict):
        items = sorted(obj.items(), key=lambda x: x[0].encode() if isinstance(x[0], str) else x[0])
        return b"d" + b"".join(encode(k) + encode(v) for k, v in items) + b"e"
    raise TypeError(f"Cannot bencode {type(obj)}")

def decode(data, offset=0):
    if data[offset:offset+1] == b"i":
        end = data.index(b"e", offset)
        return int(data[offset+1:end]), end+1
    if data[offset:offset+1] == b"l":
        offset += 1; items = []
        while data[offset:offset+1] != b"e":
            v, offset = decode(data, offset); items.append(v)
        return items, offset+1
    if data[offset:offset+1] == b"d":
        offset += 1; d = {}
        while data[offset:offset+1] != b"e":
            k, offset = decode(data, offset)
            v, offset = decode(data, offset)
            d[k if isinstance(k, str) else k.decode()] = v
        return d, offset+1
    colon = data.index(b":", offset)
    n = int(data[offset:colon])
    s = data[colon+1:colon+1+n]
    try: s = s.decode()
    except: pass
    return s, colon+1+n

def loads(data):
    if isinstance(data, str): data = data.encode()
    return decode(data, 0)[0]

def dumps(obj): return encode(obj)

if __name__ == "__main__":
    obj = {"announce": "http://tracker.example.com", "info": {"name": "test", "length": 12345}}
    enc = dumps(obj)
    print(f"Encoded: {enc}")
    dec = loads(enc)
    print(f"Decoded: {dec}")
