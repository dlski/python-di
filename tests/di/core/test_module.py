import pytest

from di.core.element import Element
from di.core.module import (
    Module,
    ModuleElementConsistencyCheck,
    ModuleElementConsistencyError,
    ModuleImportSolver,
    ModuleImportSolverError,
)


def test_module_cycle():
    modules = [Module(name=f"{index}") for index in range(3)]
    modules[0].imports = {modules[1]}
    modules[1].imports = {modules[2]}
    modules[2].imports = {modules[0]}

    solver = ModuleImportSolver()
    with pytest.raises(ModuleImportSolverError):
        solver.solve(modules)


def test_module_simple():
    modules = [Module(name=f"{index}") for index in range(4)]
    modules[1].imports = {modules[0]}
    modules[2].imports = {modules[0]}
    modules[3].imports = {modules[1], modules[2]}

    solver = ModuleImportSolver()
    plan = solver.solve(modules)
    order = plan.steps
    assert len(order[0]) == 1 and modules[0] in order[0]
    assert len(order[1]) == 2 and modules[1] in order[1] and modules[2] in order[1]
    assert len(order[2]) == 1 and modules[3] in order[2]


def test_module_consistency_check_internals():
    check = ModuleElementConsistencyCheck()
    elements = [Element(injector=..., strategy=...) for _ in range(4)]

    check.check([Module(elements={*elements}, exports={*elements[:2]})])
    with pytest.raises(ModuleElementConsistencyError):
        check.check([Module(elements={*elements[:2]}, exports={*elements[1:]})])

    a = Module(elements={*elements[:2]}, exports={*elements[:2]})
    b = Module(elements={*elements[2:]}, exports={*elements}, imports={a})
    check.check([a, b])
    a = Module(elements={*elements[:2]}, exports={*elements[:1]})
    b = Module(elements={*elements[2:]}, exports={*elements}, imports={a})
    with pytest.raises(ModuleElementConsistencyError):
        check.check([a, b])

    a = Module(elements={*elements}, bootstrap={*elements})
    check.check([a])
    a = Module(elements={*elements[:2]}, bootstrap={*elements})
    with pytest.raises(ModuleElementConsistencyError):
        check.check([a])
    a = Module(elements={*elements[:2]}, exports={*elements[:1]})
    b = Module(elements={*elements[2:]}, bootstrap={*elements})
    with pytest.raises(ModuleElementConsistencyError):
        check.check([a, b])


def test_module_consistency_check_duplicates():
    check = ModuleElementConsistencyCheck()
    elements = [Element(injector=..., strategy=...) for _ in range(8)]

    check.check(
        [
            Module(elements={*elements[:4]}, exports={*elements[:2]}),
            Module(elements={*elements[4:]}, exports={*elements[6:]}),
        ]
    )
    with pytest.raises(ModuleElementConsistencyError):
        check.check(
            [
                Module(elements={*elements}, exports={*elements[:2]}),
                Module(elements={*elements[4:]}, exports={*elements[6:]}),
            ]
        )
