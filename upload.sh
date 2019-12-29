#! /bin/sh
rm -fr build dist unidic2ud.egg-info
python3 setup.py sdist
git status
twine upload --repository pypi dist/*
exit 0
