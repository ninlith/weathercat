"""Test command-line interface."""

import random
from weathercat.config.cli import parse_arguments

def test_cli():
    """Test argument parsing."""
    random.seed(0)
    for _ in range(10):
        ϕ, λ = random.uniform(-100, 100), random.uniform(-100, 100)
        for expected in [[f"{ϕ}", f"{λ}"],
                         [f"{ϕ}", ",", f"{λ}"],
                         [f"{ϕ},", f"{λ}"],
                         [f"{ϕ},{λ}"],
                         [f"{ϕ}, {λ}"],
                         [f"geo:{ϕ},{λ};u=35"],
                         ["x, y, z"],
                         ["x", "y", "z"]]:
            actual = parse_arguments(expected + ["-d"]).location
            assert actual == expected
