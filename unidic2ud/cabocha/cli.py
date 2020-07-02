import sys

def main():
  argc=len(sys.argv)
  i=1
  f=0
  u=None
  while i<argc:
    o=sys.argv[i]
    if o.startswith("-f"):
      if o=="-f":
        i+=1
        f=int(sys.argv[i])
      else:
        f=int(sys.argv[i][2:])
      if f<0 or f>8:
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
    elif o=="-h" or o=="--help" or o=="-v" or o=="--version":
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
    if format>3:
      from unidic2ud import load
      self.parse=load(UniDic)
    else:
      from unidic2ud.cabocha import Parser
      self.parse=Parser(UniDic).parse
  def __call__(self,sentence):
    if self.format==4:
      return self.parse(sentence,raw=True)
    elif self.format==5:
      return self.parse(sentence).to_tree()
    elif self.format==6:
      return self.parse(sentence).to_tree(2)
    elif self.format==7:
      return self.parse(sentence).to_svg()
    elif self.format==8:
      import deplacy
      d=deplacy.dot(self.parse(sentence,raw=True)).split("\n")
      d[0]=d[0].replace("deplacy","udcabocha")
      return "\n".join(d)
    return self.parse(sentence).toString(self.format)

def usage():
  from pkg_resources import get_distribution
  from unidic2ud import dictlist
  print("UniDic2UD Version "+get_distribution("unidic2ud").version,file=sys.stderr)
  print("Usage: udcabocha -U Dict [-f 0-8] file",file=sys.stderr)
  print("       udcabocha --download=Dict",file=sys.stderr)
  s=" Dict:\n"+dictlist().replace(".udpipe","(udpipe)")
  print(s.replace("\n"," ").rstrip(),file=sys.stderr)
  sys.exit()

if __name__=="__main__":
  main()

