import sys
import unidic2ud

def main():
  argc=len(sys.argv)
  d="japanese-modern"
  optu=optt=False
  i=w=1
  while i<argc:
    o=sys.argv[i]
    if o=="-h" or o=="--help" or o=="-v" or o=="--version":
      usage()
    elif o.startswith("-U"):
      if o=="-U":
        i+=1
        d=sys.argv[i]
      else:
        d=sys.argv[i][2:]
    elif o=="-u":
      optu=True
    elif o=="-t" or o=="-t1":
      optt=True
      w=1
    elif o=="-t2":
      optt=True
      w=2
    elif o.startswith("--download="):
      d=sys.argv[i][11:]
      if d>"":
        s=unidic2ud.dictlist().replace(".udpipe","").split()
        if d in s:
          print("unidic2ud: "+d+" was already downloaded",file=sys.stderr)
        else:
          unidic2ud.download(d)
      usage()
    else:
      break
    i+=1
  else:
    if d.find("-")>0:
      nlp=unidic2ud.load(None,d)
    else:
      nlp=unidic2ud.load(d)
    while True:
      try:
        s=input()
      except:
        return
      print(output(nlp,optu,optt,w,s),end="")
  if d.find("-")>0:
    nlp=unidic2ud.load(None,d)
  else:
    nlp=unidic2ud.load(d)
  while i<argc:
    f=open(sys.argv[i],"r",encoding="utf-8")
    s=f.read()
    f.close()
    print(output(nlp,optu,optt,w,s),end="")
    i+=1

def output(nlp,optu,optt,width,sentence):
  if optu:
    if optt:
      return nlp(sentence).to_svg()
    return nlp(sentence,raw=True)
  if optt:
    return nlp(sentence).to_tree(BoxDrawingWidth=width,Japanese=True)
  return nlp(sentence,raw=True)

def usage():
  from pkg_resources import get_distribution
  print("Unidic2UD Version "+get_distribution("unidic2ud").version,file=sys.stderr)
  print("Usage: unidic2ud -U Dict [-u|-t|-t2] file",file=sys.stderr)
  print("       unidic2ud --download=Dict",file=sys.stderr)
  s=" Dict:\n"+unidic2ud.dictlist().replace(".udpipe","(udpipe)")
  print(s.replace("\n"," ").rstrip(),file=sys.stderr)
  sys.exit()

if __name__=="__main__":
  main()

