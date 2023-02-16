publish:
	rm -rf build mipt_npm_hv_controls.egg-info
	pip install -U twine build
	python3 -m build
	python3 -m twine upload dist/*
