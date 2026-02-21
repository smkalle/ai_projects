"""Tests for the sandboxed execution environment."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bioinfo_code_mcp.config import ServerConfig
from bioinfo_code_mcp.sandbox import Sandbox


@pytest.fixture
def sandbox():
    config = ServerConfig(execution_timeout_seconds=10, max_output_chars=10000)
    return Sandbox(config)


class TestSandboxBasicExecution:
    """Test basic code execution in the sandbox."""

    @pytest.mark.asyncio
    async def test_simple_return(self, sandbox):
        result = await sandbox.execute("return 42")
        assert result.success
        assert result.result == 42

    @pytest.mark.asyncio
    async def test_string_return(self, sandbox):
        result = await sandbox.execute('return "hello"')
        assert result.success
        assert result.result == "hello"

    @pytest.mark.asyncio
    async def test_dict_return(self, sandbox):
        result = await sandbox.execute('return {"key": "value", "num": 123}')
        assert result.success
        assert result.result == {"key": "value", "num": 123}

    @pytest.mark.asyncio
    async def test_list_return(self, sandbox):
        result = await sandbox.execute("return [1, 2, 3]")
        assert result.success
        assert result.result == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_none_return(self, sandbox):
        result = await sandbox.execute("x = 1")
        assert result.success
        assert result.result is None

    @pytest.mark.asyncio
    async def test_print_capture(self, sandbox):
        result = await sandbox.execute('print("hello world")\nreturn True')
        assert result.success
        assert "hello world" in result.stdout
        assert result.result is True

    @pytest.mark.asyncio
    async def test_multiline_code(self, sandbox):
        code = """
x = 10
y = 20
z = x + y
return z
"""
        result = await sandbox.execute(code)
        assert result.success
        assert result.result == 30

    @pytest.mark.asyncio
    async def test_loops_and_comprehensions(self, sandbox):
        code = """
squares = [i**2 for i in range(5)]
total = sum(squares)
return {"squares": squares, "total": total}
"""
        result = await sandbox.execute(code)
        assert result.success
        assert result.result["squares"] == [0, 1, 4, 9, 16]
        assert result.result["total"] == 30

    @pytest.mark.asyncio
    async def test_conditionals(self, sandbox):
        code = """
x = 42
if x > 40:
    result = "big"
else:
    result = "small"
return result
"""
        result = await sandbox.execute(code)
        assert result.success
        assert result.result == "big"


class TestSandboxState:
    """Test state persistence across executions."""

    @pytest.mark.asyncio
    async def test_state_persistence(self, sandbox):
        # Set state
        r1 = await sandbox.execute('state["counter"] = 1\nreturn state["counter"]')
        assert r1.success
        assert r1.result == 1

        # Read state from previous execution
        r2 = await sandbox.execute('state["counter"] += 10\nreturn state["counter"]')
        assert r2.success
        assert r2.result == 11

    @pytest.mark.asyncio
    async def test_state_keys_reported(self, sandbox):
        result = await sandbox.execute('state["a"] = 1\nstate["b"] = 2')
        assert result.success
        assert "a" in result.state_keys
        assert "b" in result.state_keys

    @pytest.mark.asyncio
    async def test_state_reset(self, sandbox):
        await sandbox.execute('state["x"] = 99')
        sandbox.reset_state()
        result = await sandbox.execute("return state.get('x', 'gone')")
        assert result.success
        assert result.result == "gone"

    @pytest.mark.asyncio
    async def test_complex_state(self, sandbox):
        await sandbox.execute('state["data"] = {"genes": ["TP53", "BRCA1"], "count": 2}')
        result = await sandbox.execute('return state["data"]["genes"][0]')
        assert result.success
        assert result.result == "TP53"


class TestSandboxErrors:
    """Test error handling in the sandbox."""

    @pytest.mark.asyncio
    async def test_syntax_error(self, sandbox):
        result = await sandbox.execute("def broken(")
        assert not result.success
        assert "SyntaxError" in result.error

    @pytest.mark.asyncio
    async def test_runtime_error(self, sandbox):
        result = await sandbox.execute("return 1/0")
        assert not result.success
        assert "ZeroDivisionError" in result.error

    @pytest.mark.asyncio
    async def test_name_error(self, sandbox):
        result = await sandbox.execute("return undefined_var")
        assert not result.success
        assert "NameError" in result.error

    @pytest.mark.asyncio
    async def test_type_error(self, sandbox):
        result = await sandbox.execute("return 'a' + 1")
        assert not result.success
        assert "TypeError" in result.error

    @pytest.mark.asyncio
    async def test_timeout(self):
        config = ServerConfig(execution_timeout_seconds=1)
        sb = Sandbox(config)
        result = await sb.execute("await asyncio.sleep(10)\nreturn 'done'")
        assert not result.success
        assert "timed out" in result.error.lower()

    @pytest.mark.asyncio
    async def test_empty_code(self, sandbox):
        result = await sandbox.execute("pass")
        assert result.success  # pass returns None
        assert result.result is None


class TestSandboxBuiltins:
    """Test that safe builtins work and dangerous ones are blocked."""

    @pytest.mark.asyncio
    async def test_safe_builtins_available(self, sandbox):
        code = """
results = {
    "abs": abs(-5),
    "max": max(1, 2, 3),
    "min": min(1, 2, 3),
    "len": len([1, 2, 3]),
    "sorted": sorted([3, 1, 2]),
    "sum": sum([1, 2, 3]),
    "round": round(3.14, 1),
    "range": list(range(3)),
    "isinstance": isinstance(42, int),
    "enumerate": list(enumerate(["a", "b"])),
}
return results
"""
        result = await sandbox.execute(code)
        assert result.success
        assert result.result["abs"] == 5
        assert result.result["max"] == 3
        assert result.result["sorted"] == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_json_available(self, sandbox):
        code = """
data = {"key": "value"}
text = json.dumps(data)
parsed = json.loads(text)
return parsed
"""
        result = await sandbox.execute(code)
        assert result.success
        assert result.result == {"key": "value"}

    @pytest.mark.asyncio
    async def test_import_blocked(self, sandbox):
        result = await sandbox.execute("import os\nreturn os.getcwd()")
        assert not result.success


class TestSandboxSequenceUtils:
    """Test that sequence utilities work in the sandbox."""

    @pytest.mark.asyncio
    async def test_gc_content(self, sandbox):
        result = await sandbox.execute('return seq_utils.gc_content("ATGCGCGC")')
        assert result.success
        assert abs(result.result - 0.75) < 0.01  # 6 G/C out of 8 bases

    @pytest.mark.asyncio
    async def test_reverse_complement(self, sandbox):
        result = await sandbox.execute('return seq_utils.reverse_complement("ATGC")')
        assert result.success
        assert result.result == "GCAT"

    @pytest.mark.asyncio
    async def test_translate(self, sandbox):
        result = await sandbox.execute('return seq_utils.translate("ATGGCC")')
        assert result.success
        assert result.result == "MA"

    @pytest.mark.asyncio
    async def test_find_orfs(self, sandbox):
        code = """
# Sequence with a clear ORF
dna = "ATGGCCATTGTAATGGGCCGCTGAAAGGGTGCCCGATAG" + "A" * 70
orfs = seq_utils.find_orfs(dna, min_length=30)
return len(orfs)
"""
        result = await sandbox.execute(code)
        assert result.success
        assert isinstance(result.result, int)

    @pytest.mark.asyncio
    async def test_restriction_sites(self, sandbox):
        code = """
# Sequence with a known EcoRI site (GAATTC)
dna = "ATGCGAATTCGATCG"
sites = seq_utils.restriction_sites(dna)
return sites
"""
        result = await sandbox.execute(code)
        assert result.success
        assert "EcoRI" in result.result
        assert result.result["EcoRI"] == [4]


class TestSandboxFormatUtils:
    """Test that format utilities work in the sandbox."""

    @pytest.mark.asyncio
    async def test_parse_fasta(self, sandbox):
        code = """
fasta = ">seq1 Test sequence\\nATGCGATCG\\n>seq2 Another\\nMEEPQSD"
records = fmt.parse_fasta(fasta)
return [r.to_dict() for r in records]
"""
        result = await sandbox.execute(code)
        assert result.success
        assert len(result.result) == 2
        assert result.result[0]["id"] == "seq1"
        assert result.result[0]["sequence"] == "ATGCGATCG"

    @pytest.mark.asyncio
    async def test_parse_bed(self, sandbox):
        code = """
bed = "chr1\\t100\\t200\\tgene1\\t0\\t+"
records = fmt.parse_bed(bed)
return [r.to_dict() for r in records]
"""
        result = await sandbox.execute(code)
        assert result.success
        assert len(result.result) == 1
        assert result.result[0]["chrom"] == "chr1"
        assert result.result[0]["start"] == 100
        assert result.result[0]["end"] == 200


class TestSandboxResultFormatting:
    """Test result formatting."""

    @pytest.mark.asyncio
    async def test_to_dict_success(self, sandbox):
        result = await sandbox.execute("return 42")
        d = result.to_dict()
        assert d["success"] is True
        assert d["result"] == 42

    @pytest.mark.asyncio
    async def test_to_dict_error(self, sandbox):
        result = await sandbox.execute("return 1/0")
        d = result.to_dict()
        assert d["success"] is False
        assert "error" in d

    @pytest.mark.asyncio
    async def test_to_text_success(self, sandbox):
        result = await sandbox.execute('return {"gene": "TP53"}')
        text = result.to_text()
        assert "TP53" in text

    @pytest.mark.asyncio
    async def test_to_text_error(self, sandbox):
        result = await sandbox.execute("raise ValueError('bad input')")
        text = result.to_text()
        assert "[error]" in text
        assert "bad input" in text

    @pytest.mark.asyncio
    async def test_to_text_no_output(self, sandbox):
        result = await sandbox.execute("pass")
        text = result.to_text()
        assert text == "[no output]"
