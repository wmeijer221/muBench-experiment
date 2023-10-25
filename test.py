import jsonmerge

original = {
    "key_a": "value_a",
    "key_b": "value_b",
    "nested_a": {"inner_a": 1, "inner_nested_a": {"inner_inner_a": 234}},
}

other = {
    "key_b": "value_b2",
    "key_c": "value_c",
    "nested_a": {"inner_a": 234, "inner_nested_a": {"inner_b": 234}},
}


res = jsonmerge.merge(other, original)
print(res)
