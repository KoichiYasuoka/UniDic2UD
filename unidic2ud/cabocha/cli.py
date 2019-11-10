import sys
from unidic2ud.cabocha import Parser

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
    elif o=="-h" or o=="--help":
      usage()
    else:
      break
    i+=1
  else:
    ja=Parser(u)
    while True:
      try:
        s=input()
      except:
        return
      print(ja.parse(s).toString(f),end="")
  ja=Parser(u)
  while i<argc:
    p=open(sys.argv[i],"r",encoding="utf-8")
    s=p.read()
    p.close()
    print(ja.parse(s).toString(f),end="")
    i+=1

def usage():
  print("Usage: udcabocha -U UniDic [-f 0-4] file",file=sys.stderr)
  sys.exit()

if __name__=="__main__":
  main()

