from app.validation_pipeline import (
    calculate_final_status,
    create_validation_state,
    invalidate_downstream_levels,
    is_trusted,
    set_validation_level,
)


def test_new_validation_state_fails_closed():
    state = create_validation_state()

    assert state["final_status"] == "REVIEW"

    for level in (
        "extraction",
        "provenance",
        "semantic",
        "boundary",
    ):
        assert state[level]["status"] == "REVIEW"


def test_all_four_levels_are_required_for_trust():
    state = create_validation_state()

    for level in (
        "extraction",
        "provenance",
        "semantic",
        "boundary",
    ):
        state = set_validation_level(
            state,
            level,
            "PASS",
            f"{level} passed",
        )

    assert calculate_final_status(state) == "TRUSTED"
    assert is_trusted(state) is True


def test_one_failed_level_prevents_trust():
    state = create_validation_state()

    for level in (
        "extraction",
        "provenance",
        "semantic",
        "boundary",
    ):
        state = set_validation_level(
            state,
            level,
            "PASS",
            f"{level} passed",
        )

    state = set_validation_level(
        state,
        "semantic",
        "FAIL",
        "Semantic support failed.",
    )

    assert state["final_status"] == "REVIEW"
    assert is_trusted(state) is False


def test_semantic_change_invalidates_semantic_and_boundary():
    state = create_validation_state()

    for level in (
        "extraction",
        "provenance",
        "semantic",
        "boundary",
    ):
        state = set_validation_level(
            state,
            level,
            "PASS",
            f"{level} passed",
        )

    updated = invalidate_downstream_levels(
        state,
        "semantic",
        "Topic label changed after validation.",
    )

    assert updated["extraction"]["status"] == "PASS"
    assert updated["provenance"]["status"] == "PASS"

    assert updated["semantic"]["status"] == "REVIEW"
    assert updated["boundary"]["status"] == "REVIEW"

    assert updated["final_status"] == "REVIEW"


def test_boundary_change_requires_final_revalidation():
    state = create_validation_state()

    for level in (
        "extraction",
        "provenance",
        "semantic",
        "boundary",
    ):
        state = set_validation_level(
            state,
            level,
            "PASS",
            f"{level} passed",
        )

    updated = invalidate_downstream_levels(
        state,
        "boundary",
        "Boundary changed.",
    )

    assert updated["extraction"]["status"] == "PASS"
    assert updated["provenance"]["status"] == "PASS"
    assert updated["semantic"]["status"] == "PASS"

    assert updated["boundary"]["status"] == "REVIEW"
    assert updated["final_status"] == "REVIEW"