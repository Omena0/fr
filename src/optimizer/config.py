"""Tunable budgets for the optimizer.

Every speculative or potentially expensive analysis uses one of these limits.
Values can be overridden with environment variables so users can trade compile
time for code quality without rebuilding the compiler.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, replace


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return int(raw, 0)
    except ValueError:
        return default


@dataclass(frozen=True)
class OptimizerConfig:
    # Fixed-point and inlining budgets
    max_iterations: int = 20
    inline_max_inst: int = 20
    specialized_inline_max_inst: int = 60
    max_specializations: int = 64
    max_specialized_body: int = 120
    max_specialized_range: int = 64
    max_specialization_depth: int = 3

    # Interprocedural range analysis
    max_range_iterations: int = 6
    max_range_visits: int = 20000
    max_range_values: int = 4096
    range_widen_after: int = 6

    # Compile-time simulation / lookup tables
    max_sim_steps: int = 200000
    max_sim_calls: int = 2000
    max_sim_time_ms: int = 100
    max_table_entries: int = 64
    max_table_domain: int = 256
    min_table_entries: int = 2
    max_table_function_size: int = 120

    @classmethod
    def from_env(cls) -> "OptimizerConfig":
        return cls(
            max_iterations=_env_int("FR_OPT_ITERATIONS", cls.max_iterations),
            inline_max_inst=_env_int("FR_OPT_INLINE_MAX", cls.inline_max_inst),
            max_specializations=_env_int(
                "FR_OPT_MAX_SPECIALIZATIONS", cls.max_specializations
            ),
            max_specialized_body=_env_int(
                "FR_OPT_MAX_SPECIALIZED_BODY", cls.max_specialized_body
            ),
            max_specialized_range=_env_int(
                "FR_OPT_MAX_SPECIALIZED_RANGE", cls.max_specialized_range
            ),
            max_range_iterations=_env_int(
                "FR_OPT_RANGE_ITERATIONS", cls.max_range_iterations
            ),
            max_range_visits=_env_int("FR_OPT_RANGE_VISITS", cls.max_range_visits),
            max_sim_steps=_env_int("FR_OPT_SIM_STEPS", cls.max_sim_steps),
            max_sim_calls=_env_int("FR_OPT_SIM_CALLS", cls.max_sim_calls),
            max_sim_time_ms=_env_int("FR_OPT_SIM_MS", cls.max_sim_time_ms),
            max_table_entries=_env_int(
                "FR_OPT_TABLE_ENTRIES", cls.max_table_entries
            ),
            max_table_domain=_env_int("FR_OPT_TABLE_DOMAIN", cls.max_table_domain),
            min_table_entries=_env_int("FR_OPT_TABLE_MIN", cls.min_table_entries),
        )

    def with_overrides(self, **kwargs) -> "OptimizerConfig":
        return replace(self, **kwargs)
