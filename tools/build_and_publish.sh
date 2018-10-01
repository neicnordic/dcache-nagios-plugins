#
# Utility script to build and publish a new version on pypi
#
rm -rf build/ *.egg-info dist/
python setup.py sdist bdist_wheel --universal 
twine upload dist/*
