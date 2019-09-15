import setuptools
with open("README.md","r") as r:
  long_description=r.read()
URL="https://github.com/KoichiYasuoka/UniDic2UD"

setuptools.setup(
  name="unidic2ud",
  version="1.1.4",
  description="Tokenizer POS-tagger Lemmatizer and Dependency-parser for modern and contemporary Japanese",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url=URL,
  author="Koichi Yasuoka",
  author_email="yasuoka@kanji.zinbun.kyoto-u.ac.jp",
  license="MIT",
  keywords="unidic udpipe mecab nlp",
  packages=setuptools.find_packages(),
  install_requires=["ufal.udpipe>=1.2.0","mecab-python3>=0.996","pip>=10.0.1"],
  python_requires=">=3.6",
  package_data={
    "unidic2ud":["./*.js"],
  },
  classifiers=[
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Operating System :: OS Independent",
    "Topic :: Text Processing :: Linguistic",
    "Natural Language :: Japanese",
  ],
  project_urls={
    "ud-ja-kanbun":"https://corpus.kanji.zinbun.kyoto-u.ac.jp/gitlab/Kanbun/ud-ja-kanbun",
    "Source":URL,
    "Tracker":URL+"/issues",
  }
)
