# coding=utf-8

import sys
from .unidic2ud import download,dictlist
if sys.argv[1]=="download":
  download(sys.argv[2],None)
elif sys.argv[1]=="download.unidic":
  download(sys.argv[2],"unidic")
elif sys.argv[1]=="download.udpipe":
  download(sys.argv[2],"udpipe")
elif sys.argv[1]=="dictlist":
  print(dictlist().replace("\n"," (unidic)\n").replace(".udpipe (unidic)"," (udpipe)"),end="")

