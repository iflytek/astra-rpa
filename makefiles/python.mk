.PHONY: fmt-python check-python
# Backend Code Quality Commands
fmt-python:
	@echo "[Format] Running ruff format..."
	@uv run --project engine --dev ruff format ./engine
	@echo "[Done] Code formatting complete"

check-python:
	@echo "[Check] Running ruff check..."
	@uv run --project engine --dev ruff check --fix ./engine
	@uv run --project engine --dev ruff check ./engine
	@echo "[Done] Code check complete"