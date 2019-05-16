all:

.PHONY:	dist update
dist:
	rm -f dist/*.whl dist/*.tar.gz
	python3 setup.py sdist
	python3 setup.py bdist_wheel

release:
	twine upload dist/*.tar.gz 
	twine upload dist/*.whl
