"""Budgeted compile-time interpreter for pure scalar IR functions.

This is used to populate lookup tables and constant-return summaries. It is a
best-effort analysis: any unsupported operation, unknown value or budget
exhaustion simply aborts the query and leaves the function untouched.
"""

from __future__ import annotations

import math
import time

from optimizer.config import OptimizerConfig
from optimizer.ir import (
    Constant,
    Function,
    Module,
    Op,
    IRType,
    Value,
)

_UNKNOWN = object()


class SimulationError(Exception):
    pass


class SimulationBudget:
    def __init__(self, config: OptimizerConfig):
        self.config = config
        self.steps = 0
        self.calls = 0
        self.deadline = time.monotonic() + config.max_sim_time_ms / 1000.0

    def tick(self) -> None:
        self.steps += 1
        if self.steps > self.config.max_sim_steps:
            raise SimulationError("simulation step budget exhausted")
        if (self.steps & 255) == 0 and time.monotonic() > self.deadline:
            raise SimulationError("simulation time budget exhausted")

    def call(self) -> None:
        self.calls += 1
        if self.calls > self.config.max_sim_calls:
            raise SimulationError("simulation call budget exhausted")


def _value(v, env: dict[int, object]):
    if isinstance(v, Constant):
        return v.value
    if isinstance(v, Value):
        if v.id in env:
            return env[v.id]
        inst = v.defining_inst
        if inst is not None:
            if inst.op == Op.CONST_INT:
                return int(inst.imm_int or 0)
            if inst.op == Op.CONST_BOOL:
                return bool(inst.imm_int)
            if inst.op == Op.CONST_FLOAT:
                return float(inst.imm_float or 0.0)
            if inst.op == Op.CONST_STR:
                return inst.imm_str or ""
        raise SimulationError(f"unknown value {v}")
    return v


class PureInterpreter:
    def __init__(self, module: Module, config: OptimizerConfig):
        self.module = module
        self.config = config
        self.budget = SimulationBudget(config)
        self.depth = 0

    def run(self, func: Function, args: list) -> object:
        self.budget.call()
        if self.depth > 32:
            raise SimulationError("recursion depth budget exhausted")
        if func.entry is None:
            raise SimulationError("function has no entry")
        env: dict[int, object] = {}
        for param, arg in zip(func.params, args):
            env[param.id] = arg

        block = func.entry
        pred = None
        steps = 0
        while block is not None:
            steps += 1
            if steps > 10000:
                raise SimulationError("block execution budget exhausted")
            next_block = None
            new_pred = block
            for inst in block.instructions:
                self.budget.tick()
                if inst.op == Op.PHI:
                    if inst.result is None:
                        continue
                    chosen = None
                    for i, operand in enumerate(inst.operands):
                        if i < len(inst.target_blocks) and inst.target_blocks[i] is pred:
                            chosen = operand
                            break
                    if chosen is None and inst.operands:
                        chosen = inst.operands[0]
                    if chosen is None:
                        raise SimulationError("phi has no inputs")
                    env[inst.result.id] = _value(chosen, env)
                    continue

                if inst.op == Op.JUMP:
                    next_block = inst.target_blocks[0] if inst.target_blocks else None
                    break
                if inst.op == Op.BRANCH:
                    cond = bool(_value(inst.operands[0], env))
                    if len(inst.target_blocks) < 2:
                        raise SimulationError("branch targets missing")
                    next_block = inst.target_blocks[0] if cond else inst.target_blocks[1]
                    break
                if inst.op == Op.RETURN:
                    return _value(inst.operands[0], env) if inst.operands else None
                if inst.op == Op.RETURN_VOID:
                    return None
                if inst.op in (Op.TRY_BEGIN, Op.RAISE, Op.PRINT, Op.PRINTLN, Op.INPUT):
                    raise SimulationError("impure operation")
                if inst.op in (Op.CALL_EXTERN,):
                    raise SimulationError("external call")

                result = self._eval(inst, env)
                if inst.result is not None:
                    env[inst.result.id] = result
            block = next_block
            pred = new_pred
        raise SimulationError("fell off function")

    def _eval(self, inst, env):
        op = inst.op
        args = [_value(v, env) for v in inst.operands]

        if op == Op.CONST_INT:
            return int(inst.imm_int or 0)
        if op == Op.CONST_BOOL:
            return bool(inst.imm_int)
        if op == Op.CONST_FLOAT:
            return float(inst.imm_float or 0.0)
        if op == Op.CONST_STR:
            return inst.imm_str or ""
        if op == Op.COPY:
            return args[0] if args else None
        if op == Op.NOP:
            return None
        if op == Op.ADD:
            return int(args[0]) + int(args[1])
        if op == Op.SUB:
            return int(args[0]) - int(args[1])
        if op == Op.MUL:
            return int(args[0]) * int(args[1])
        if op == Op.DIV:
            a, b = int(args[0]), int(args[1])
            if b == 0:
                raise SimulationError("division by zero")
            q = abs(a) // abs(b)
            return q if (a < 0) == (b < 0) else -q
        if op == Op.MOD:
            a, b = int(args[0]), int(args[1])
            if b == 0:
                raise SimulationError("division by zero")
            q = abs(a) // abs(b)
            q = q if (a < 0) == (b < 0) else -q
            return a - q * b
        if op == Op.NEG:
            return -args[0]
        if op in (Op.FADD, Op.FSUB, Op.FMUL, Op.FDIV, Op.FNEG):
            a, b = (args + [0.0, 0.0])[:2]
            if op == Op.FADD:
                return float(a) + float(b)
            if op == Op.FSUB:
                return float(a) - float(b)
            if op == Op.FMUL:
                return float(a) * float(b)
            if op == Op.FDIV:
                return float(a) / float(b)
            return -float(a)
        if op in (Op.LT, Op.GT, Op.LE, Op.GE, Op.EQ, Op.NE):
            a, b = args[0], args[1]
            return {
                Op.LT: a < b,
                Op.GT: a > b,
                Op.LE: a <= b,
                Op.GE: a >= b,
                Op.EQ: a == b,
                Op.NE: a != b,
            }[op]
        if op == Op.AND:
            return bool(args[0]) and bool(args[1])
        if op == Op.OR:
            return bool(args[0]) or bool(args[1])
        if op == Op.NOT:
            return not bool(args[0])
        if op == Op.SHL:
            return int(args[0]) << int(args[1])
        if op == Op.SHR:
            return int(args[0]) >> int(args[1])
        if op == Op.BIT_AND:
            return int(args[0]) & int(args[1])
        if op == Op.BIT_OR:
            return int(args[0]) | int(args[1])
        if op == Op.BIT_XOR:
            return int(args[0]) ^ int(args[1])
        if op == Op.SELECT:
            return args[1] if args[0] else args[2]
        if op == Op.INT_TO_FLOAT:
            return float(args[0])
        if op == Op.FLOAT_TO_INT:
            return int(args[0])
        if op == Op.TO_BOOL:
            return bool(args[0])
        if op == Op.ABS:
            return abs(args[0])
        if op == Op.MIN:
            return min(args[0], args[1])
        if op == Op.MAX:
            return max(args[0], args[1])
        if op == Op.SQRT:
            return math.sqrt(float(args[0]))
        if op == Op.SIN:
            return math.sin(float(args[0]))
        if op == Op.COS:
            return math.cos(float(args[0]))
        if op == Op.TAN:
            return math.tan(float(args[0]))
        if op == Op.FLOOR:
            return math.floor(float(args[0]))
        if op == Op.CEIL:
            return math.ceil(float(args[0]))
        if op == Op.ROUND:
            x = float(args[0])
            return math.floor(x + 0.5) if x >= 0 else math.ceil(x - 0.5)
        if op == Op.POW:
            return args[0] ** args[1]
        if op == Op.CALL:
            target = self.module.get_function(inst.imm_str or "")
            if target is None or target.is_extern:
                raise SimulationError("unknown callee")
            self.depth += 1
            try:
                return self.run(target, args)
            finally:
                self.depth -= 1
        if op == Op.CALL_BUILTIN:
            name = inst.imm_str or ""
            if name == "abs":
                return abs(args[0])
            if name == "min":
                return min(args[0], args[1])
            if name == "max":
                return max(args[0], args[1])
            if name == "int":
                return int(args[0])
            if name == "float":
                return float(args[0])
            if name == "bool":
                return bool(args[0])
            if name == "len" and isinstance(args[0], str):
                return len(args[0])
            if name == "sqrt":
                return math.sqrt(float(args[0]))
            if name == "pow":
                return args[0] ** args[1]
            if name == "floor":
                return math.floor(float(args[0]))
            if name == "ceil":
                return math.ceil(float(args[0]))
            if name == "round":
                x = float(args[0])
                return math.floor(x + 0.5) if x >= 0 else math.ceil(x - 0.5)
            raise SimulationError(f"unsupported builtin {name}")
        raise SimulationError(f"unsupported op {op}")


def evaluate_function(
    module: Module, func: Function, args: list, config: OptimizerConfig
):
    try:
        interpreter = PureInterpreter(module, config)
        return interpreter.run(func, args)
    except (SimulationError, ArithmeticError, ValueError, TypeError, RecursionError):
        return _UNKNOWN
