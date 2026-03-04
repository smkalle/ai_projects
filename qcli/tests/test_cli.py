from qcli.cli import build_parser


def test_default_args() -> None:
    parser = build_parser()
    args = parser.parse_args([])
    assert args.model == "Qwen/Qwen3.5-2B"
    assert args.temperature == 0.7
    assert args.top_p == 0.9
    assert args.max_new_tokens == 512
    assert args.quantized == "none"


def test_quantized_arg() -> None:
    parser = build_parser()
    args = parser.parse_args(["--quantized", "4bit"])
    assert args.quantized == "4bit"
