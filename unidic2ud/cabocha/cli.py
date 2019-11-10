import sys

def main():
  argc=len(sys.argv)
  i=1
  f=0
  u="ipadic"
  while i<argc:
    o=sys.argv[i]
    if o.startswith("-f"):
      if o=="-f":
        i+=1
        f=int(sys.argv[i])
      else:
        f=int(sys.argv[i][2:])
      if f<0 or f>4:
        usage()
    elif o.startswith("-U"):
      if o=="-U":
        i+=1
        u=sys.argv[i]
      else:
        u=sys.argv[i][2:]
    elif o.startswith("--download="):
      d=sys.argv[i][11:]
      if d>"":
        from unidic2ud import download,dictlist
        s=dictlist().replace(".udpipe","").split()
        if d in s:
          print("udcabocha: "+d+" was already downloaded",file=sys.stderr)
        else:
          download(d)
      usage()
    elif o=="-h" or o=="--help":
      usage()
    else:
      break
    i+=1
  else:
    ja=parser(u,f)
    while True:
      try:
        s=input()
      except:
        return
      print(ja(s),end="")
  ja=parser(u,f)
  while i<argc:
    p=open(sys.argv[i],"r",encoding="utf-8")
    s=p.read()
    p.close()
    print(ja(s),end="")
    i+=1

class parser(object):
  def __init__(self,UniDic,format):
    self.format=format
    if format==4:
      from unidic2ud import load
      self.parse=load(UniDic)
    else:
      from unidic2ud.cabocha import Parser
      self.parse=Parser(UniDic).parse
  def __call__(self,sentence):
    if self.format==4:
      return self.parse(sentence,raw=True)
    return self.parse(sentence).toString(self.format)

def usage():
  print("Usage: udcabocha -U UniDic [-f 0-4] file",file=sys.stderr)
  print("       udcabocha --download=Dic",file=sys.stderr)
  from unidic2ud import dictlist
  s="  Dic: ipadic\n"+dictlist().replace(".udpipe","(udpipe)")
  print(s.replace("\n"," ").rstrip(),file=sys.stderr)
  sys.exit()

if __name__=="__main__":
  main()

