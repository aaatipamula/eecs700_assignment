from pprint import pprint
from z3 import *

_counter = 0

def wp(stmt, post, proc_env: dict):
    if stmt[0] == 'seq':
        for s in reversed(stmt[1:]):
            post = wp(s, post, proc_env)
        return post
    elif stmt[0] == 'assume':
        cond = expr_to_z3(stmt[1])
        return Implies(cond, post)
    elif stmt[0] == 'assert':
        cond = expr_to_z3(stmt[1])
        return And(cond, post)
    elif stmt[0] == 'if':
        test = expr_to_z3(stmt[1])
        body = stmt[2]
        orelse = stmt[3]
        wp_body = wp(['seq'] + body, post, proc_env)
        wp_orelse = wp(['seq'] + orelse, post, proc_env)
        return And(Implies(test, wp_body), Implies(Not(test), wp_orelse))
    elif stmt[0] == 'skip':
        return post
    elif stmt[0] == 'assign':
        var = stmt[1]
        expr = expr_to_z3(stmt[2])
        return substitute(post, (Int(var), expr))

    elif stmt[0] == 'tastore':
        A, I, E = stmt[1:]
        A_z3 = Array(A, IntSort(), IntSort())
        I_z3 = expr_to_z3(I)
        E_z3 = expr_to_z3(E)
        store = Store(A_z3, I_z3, E_z3)
        return substitute(post, (A_z3, store))

    elif stmt[0] == 'invariant':
        # invariants do not affect the weakest precondition
        return BoolVal(True)

    elif stmt[0] == 'while':
        cond = expr_to_z3(stmt[1])
        invariant = And(*list(map(expr_to_z3, stmt[3])))
        body = stmt[2]
        wp_body = wp(['seq'] + body, invariant, proc_env)
        return And(invariant, Implies(And(invariant, cond), wp_body), Implies(And(invariant, Not(cond)), post))

    elif stmt[0] == 'proc':
        name, params, body, req, ens, _ = stmt[1:]

        requires = expr_to_z3(req)
        ensures = expr_to_z3(ens)

        old_vars = find_old_vars(ens)
        for v in old_vars:
            requires = And(requires, Int(f"{v}_old") == Int(v))

        wp_body = wp(['seq'] + body, ensures, proc_env)

        return Implies(requires, wp_body)

    elif stmt[0] == 'return':
        replaced = ['assign', 'ret', stmt[1]]
        return wp(replaced, post, proc_env)

    elif stmt[0] == 'call':
        name, actuals, lhs = stmt[1:]
        params, body, req, ens, modifies = proc_env[name]

        requires = expr_to_z3(req)
        ensures = expr_to_z3(ens)

        # VC1 (substitute formals with actuals and ret with lhs)
        pairs = zip(map(Int, params), map(expr_to_z3, actuals))
        requires = substitute(requires, *pairs)
        ensures = substitute(ensures, *pairs)
        ensures = substitute(ensures, (Int('ret'), Int(lhs)))

        frame_pairs = []
        for var in find_old_vars(ens):
            if var not in modifies:
                frame_pairs.append(Int(f"{var}_old") == Int(var))
        frame_condition = And(*frame_pairs) if frame_pairs else BoolVal(True)

        # VC2 (Havoc step)
        havoc_list = havoc(modifies)
        post = substitute(post, *havoc_list)

        # return And(Implies(requires, ensures), post)
        return And(Implies(requires, And(ensures, frame_condition)), post)
    
    else:
        raise NotImplementedError(stmt)

def find_old_vars(expr):
    """Collect variable names appearing as x_old in an AST."""
    result = set()
    if isinstance(expr, list):
        if expr[0] == 'var' and expr[1].endswith('_old'):
            result.add(expr[1][:-4])  # strip '_old'
        else:
            for e in expr[1:]:
                result |= find_old_vars(e)
    return result

def havoc(modifies: list[str]) -> list[tuple[ArithRef, ArithRef]]:
    return [(Int(m), FreshInt(prefix=m)) for m in modifies]

def expr_to_z3(expr):
    if expr[0] == 'const':
        if isinstance(expr[1], bool):
            return BoolVal(expr[1])
        else:
            return IntVal(expr[1])
    elif expr[0] == 'var':
        return Int(expr[1])
    elif expr[0] == '<':
        return expr_to_z3(expr[1]) < expr_to_z3(expr[2])
    elif expr[0] == '<=':
        return expr_to_z3(expr[1]) <= expr_to_z3(expr[2])
    elif expr[0] == '>':
        return expr_to_z3(expr[1]) > expr_to_z3(expr[2])
    elif expr[0] == '>=':
        return expr_to_z3(expr[1]) >= expr_to_z3(expr[2])
    elif expr[0] == '==':
        return expr_to_z3(expr[1]) == expr_to_z3(expr[2])
    elif expr[0] == '!=':
        return expr_to_z3(expr[1]) != expr_to_z3(expr[2])
    elif expr[0] == '+':
        return expr_to_z3(expr[1]) + expr_to_z3(expr[2])
    elif expr[0] == '-':
        if len(expr) == 2:
            return -expr_to_z3(expr[1])
        else:
            return expr_to_z3(expr[1]) - expr_to_z3(expr[2])
    elif expr[0] == '*':
        return expr_to_z3(expr[1]) * expr_to_z3(expr[2])
    elif expr[0] == '/':
        return expr_to_z3(expr[1]) / expr_to_z3(expr[2])
    elif expr[0] == '==':
        return expr_to_z3(expr[1]) == expr_to_z3(expr[2])
    elif expr[0] == 'select':
        arr = Array(expr[1], IntSort(), IntSort())
        return Select(arr, expr_to_z3(expr[2]))
    else:
        raise NotImplementedError(expr)

def prove(stmt, proc_env):
    post = BoolVal(True)
    pre = wp(stmt, post, proc_env)
    print(pre)
    s = Solver()
    s.add(Not(pre))
    if s.check() == unsat:
        print("The program is correct.")
    else:
        print("The program is incorrect.")
        print(s.model())

if __name__ == "__main__":
    from parser import py_ast, WhilePyVisitor
    import sys
    filename = sys.argv[1]
    tree = py_ast(filename)
    visitor = WhilePyVisitor()
    stmt = visitor.visit(tree)
    print("Program AST:")
    pprint(stmt)
    prove(stmt, visitor.procs)
