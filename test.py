from bencode import dumps, loads
assert loads(dumps(42)) == 42
assert loads(dumps("hello")) == "hello"
assert loads(dumps([1, "two", 3])) == [1, "two", 3]
assert loads(dumps({"a": 1, "b": "two"})) == {"a": 1, "b": "two"}
assert loads(b"i-5e") == -5
print("Bencode tests passed")