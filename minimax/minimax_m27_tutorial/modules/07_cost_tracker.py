"""
Module 07 — Cost Tracking & Budget Management
───────────────────────────────────────────────
Covers:
  • Building a CostLedger to track across multiple calls
  • Per-call and aggregate cost reporting
  • Budget guards (hard limit enforcement)
  • Cache hit detection and savings calculation
  • Generating a cost summary report

M2.7 pricing (March 2025):
  Input  : $0.30 / 1M tokens
  Output : $1.20 / 1M tokens
  Automatic prompt caching — no setup required.
"""
import sys
from dataclasses import dataclass, field
from typing import Optional, Any
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import load_env, make_client, print_header, print_divider, log
from config import PRICE_INPUT_PER_1M, PRICE_OUTPUT_PER_1M


# ── Cost Ledger ───────────────────────────────────────────────────────────────

@dataclass
class CallRecord:
    label:        str
    input_tokens: int
    output_tokens: int
    cache_read:   int = 0
    cache_write:  int = 0
    cost_usd:     float = 0.0

    @classmethod
    def from_usage(cls, label: str, usage: Any) -> "CallRecord":
        inp  = getattr(usage, "input_tokens", 0) or 0
        out  = getattr(usage, "output_tokens", 0) or 0
        cr   = getattr(usage, "cache_read_input_tokens", 0) or 0
        cw   = getattr(usage, "cache_creation_input_tokens", 0) or 0
        cost = (inp / 1_000_000) * PRICE_INPUT_PER_1M \
             + (out / 1_000_000) * PRICE_OUTPUT_PER_1M
        return cls(label=label, input_tokens=inp, output_tokens=out,
                   cache_read=cr, cache_write=cw, cost_usd=cost)


class CostLedger:
    """Tracks API call costs across a session with optional budget guard."""

    def __init__(self, budget_usd: Optional[float] = None):
        self.records: list[CallRecord] = []
        self.budget_usd = budget_usd
        self._spent = 0.0

    def record(self, label: str, usage: Any) -> CallRecord:
        rec = CallRecord.from_usage(label, usage)
        self.records.append(rec)
        self._spent += rec.cost_usd
        log("USAGE", f"[{label}] in={rec.input_tokens:,} out={rec.output_tokens:,} "
                     f"cost=${rec.cost_usd:.6f} | session=${self._spent:.6f}")
        return rec

    def check_budget(self) -> None:
        """Raise if budget exceeded."""
        if self.budget_usd and self._spent >= self.budget_usd:
            raise RuntimeError(
                f"Budget exceeded: ${self._spent:.6f} >= ${self.budget_usd:.6f}"
            )

    def total_input(self)  -> int:   return sum(r.input_tokens  for r in self.records)
    def total_output(self) -> int:   return sum(r.output_tokens for r in self.records)
    def total_cost(self)   -> float: return self._spent
    def total_cache_read(self) -> int: return sum(r.cache_read for r in self.records)

    def cache_savings_usd(self) -> float:
        """Tokens served from cache avoid full input pricing."""
        return (self.total_cache_read() / 1_000_000) * PRICE_INPUT_PER_1M

    def report(self) -> None:
        print_divider("Cost Ledger Report")
        header = f"{'Call':<22} {'In':>8} {'Out':>8} {'Cache$':>6} {'Cost':>12}"
        print(f"\n  {header}")
        print(f"  {'─'*len(header)}")
        for r in self.records:
            cache_flag = "✓" if r.cache_read > 0 else " "
            print(f"  {r.label:<22} {r.input_tokens:>8,} {r.output_tokens:>8,} "
                  f"{cache_flag:>6} ${r.cost_usd:>10.6f}")
        print(f"  {'─'*len(header)}")
        print(f"  {'TOTAL':<22} {self.total_input():>8,} {self.total_output():>8,} "
              f"{'':>6} ${self.total_cost():>10.6f}")
        print()
        log("USAGE", f"Cache savings : ${self.cache_savings_usd():.6f} USD")
        log("USAGE", f"Calls tracked : {len(self.records)}")
        if self.budget_usd:
            remaining = self.budget_usd - self._spent
            log("USAGE", f"Budget used   : ${self._spent:.6f} / ${self.budget_usd:.2f} "
                         f"({100*self._spent/self.budget_usd:.1f}%)")
            log("USAGE", f"Budget remain : ${remaining:.6f}")


# ── Demonstration ──────────────────────────────────────────────────────────────

def run() -> None:
    print_header(
        "Module 07 · Cost Tracking & Budget Management",
        "CostLedger, per-call breakdown, cache savings, budget guard"
    )

    api_key, base_url, model = load_env()
    client = make_client(api_key, base_url)

    # Set a session budget of $0.01 (10,000 micro-dollars)
    ledger = CostLedger(budget_usd=0.01)

    prompts = [
        ("short-factual",
         "What year was Python created?"),
        ("medium-technical",
         "Explain Python's GIL in 3 sentences and when it matters for performance."),
        ("long-analytical",
         "Compare asyncio, threading, and multiprocessing for I/O-bound vs CPU-bound tasks. "
         "When would you choose each? Include a real-world example for each."),
        ("code-generation",
         "Write a Python class implementing a thread-safe LRU cache without using functools."),
    ]

    for label, prompt in prompts:
        print_divider(f"Call: {label}")
        try:
            ledger.check_budget()  # Guard before each call
        except RuntimeError as e:
            log("WARN", f"Budget guard triggered: {e}")
            break

        try:
            response = client.messages.create(
                model=model,
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}]
            )
            ledger.record(label, getattr(response, "usage", None))

            # Print truncated answer
            from utils import extract_text
            answer = extract_text(response)
            preview = answer[:200] + ("…" if len(answer) > 200 else "")
            print(f"\n  {preview}\n")

        except RuntimeError as e:
            log("ERROR", str(e))
            break
        except Exception as e:
            log("ERROR", f"API error: {e}")

    # ── Final report ──────────────────────────────────────────────────────────
    ledger.report()

    # ── Per-million projection ────────────────────────────────────────────────
    print_divider("Cost Projection")
    if ledger.records:
        avg_in  = ledger.total_input()  / len(ledger.records)
        avg_out = ledger.total_output() / len(ledger.records)
        per_1k_calls = (avg_in / 1_000_000 * PRICE_INPUT_PER_1M
                      + avg_out / 1_000_000 * PRICE_OUTPUT_PER_1M) * 1000
        log("USAGE", f"Avg input  per call : {avg_in:.0f} tokens")
        log("USAGE", f"Avg output per call : {avg_out:.0f} tokens")
        log("USAGE", f"Est. cost per 1,000 calls: ${per_1k_calls:.4f} USD")
        log("USAGE", f"Est. cost per 1M   calls: ${per_1k_calls * 1000:.2f} USD")

    print_divider("Module 07 Complete")


if __name__ == "__main__":
    run()
