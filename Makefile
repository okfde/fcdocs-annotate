dependencies: pyproject.toml
	uv pip compile -o requirements.txt pyproject.toml -p 3.10
	uv pip compile -o requirements-dev.txt --extra dev pyproject.toml -p 3.10
