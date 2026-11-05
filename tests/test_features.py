from urlsentry.features import FEATURES, extract_features


def test_fixed_feature_contract_and_no_network_primitives():
    value = "https://sub.example.co.uk/login?user=7"
    x = extract_features(value)
    assert len(x) == len(FEATURES) == 18
    assert x[1] == len("sub.example.co.uk")
    assert x[5] == 2
    assert x[12] == 1
    assert x[14] == 1


def test_explicit_port_and_ip():
    x = extract_features("http://192.0.2.1:8080/a")
    assert x[11] == 1
    assert x[17] == 1


def test_empty_and_hostname_inputs_are_deterministic():
    assert extract_features("example.com") == extract_features("example.com")
    assert len(extract_features("")) == 18
