#! /usr/bin/python3 -i
# coding=utf-8

import unidic2ud

class Tree(unidic2ud.UDPipeEntry):
  def _makeChunks(self):
    m={"NOUN","PROPN","PRON","NUM","VERB","ADJ","DET","ADV","SYM"}
    p,s,c=[],[],[]
    x=0
    for i in range(1,len(self)):
      id=self[i].id
      if id==1:
        if c!=[]:
          s.append(c)
          c=[]
        if s!=[]:
          p.append(s)
          s=[]
      if x>id:
        c.append(i)
      elif x==id:
        c.append(i)
        x=0
        d=self[i].deprel
        if d=="compound" or d=="nummod":
          if self[i].head.id>id:
            x=self[i].head.id
        elif d=="advcl" or d=="obl":
          if self[i].head.id-id==1 and self[i].upos!="ADJ":
            x=id+1
      elif self[i].upos in m:
        if self[i].head.id<id:
          c.append(i)
        else:
          if c!=[]:
            s.append(c)
          c=[i]
          d=self[i].deprel
          if d=="compound" or d=="nummod":
            if self[i].head.id>id:
              x=self[i].head.id
          elif d=="advcl" or d=="obl":
            if self[i].head.id-id==1 and self[i].upos!="ADJ":
              x=id+1
      else:
        c.append(i)
    if c!=[]:
      s.append(c)
    if s!=[]:
      p.append(s)
    self._sentences=p
    self._chunkinfo=[]
    k=0
    for s in p:
      ix=[-1]
      for i,c in enumerate(s):
        ix.extend([i]*len(c))
      cf=[]
      for i,c in enumerate(s):
        y=z=-1
        for j,t in enumerate(c):
          if ix[self[t].head.id]!=i:
            y=j
            z=ix[self[t].head.id]
          elif self[t].head is self[t]:
            y=j
          elif y<0 or self[t].upos in m:
            pass
          else:
            break
        else:
          y=max(y,0)
          j=y
        w=""
        for t in c:
          w+=self[t].form
          if self[t].misc.find("SpaceAfter=No")<0:
            w+=" "
        cf.append((i,z,c[0]-1,y,j,w,k))
        k+=1
      self._chunkinfo.append(cf)
  def _makeFeatures(self):
    self._features=[""]
    for t in range(1,len(self)):
      x=(self[t].xpos+"-*-*-*-*-*-*-*-*-*").split("-")
      x[6]=self[t].lemma
      j=self[t].misc.find("Translit=")
      if j>=0:
        x[7]=self[t].misc[j+9:]
      x[9]=self[t].upos
      self._features.append(",".join(x[0:10]))
  def toString(self,format=4):
    if format==4:
      return str(self)
    if not hasattr(self,"_sentences"):
      self._makeChunks()
    if format>0 and not hasattr(self,"_features"):
      self._makeFeatures()
    result=""
    for k,s in enumerate(self._sentences):
      if format==0 or format==2:
        x=len(self._chunkinfo[k])
        l,m,n=[],[],[" "*(x*2)]*x
        for i,d,t,h,f,w,z in self._chunkinfo[k]:
          l.append(len(w)+len([c for c in w if ord(c)>127]))
          m.append(w)
          if d<0:
            continue
          n[i]="-"*(d*2-1)+"D"+n[i][d*2:]
          for j in range(i+1,d-1):
            n[j]=n[j][0:d*2-1]+"|"+n[j][d*2:]
        h=max([(x-i)*2+j for i,j in enumerate(l)])
        for i in range(x):
          result+=" "*(h-(x-i)*2-l[i])+m[i]+n[i][i*2:].rstrip()+"\n"
        result+="EOS\n"
      if format==1 or format==2:
        for i,d,t,h,f,w,z in self._chunkinfo[k]:
          result+="* "+str(i)+" "+str(d)+"D "+str(h)+"/"+str(f)+" 0.000000\n"
          for t in s[i]:
            result+=self[t].form+"\t"+self._features[t]+"\t"+str(self[t].id)+"<-"+self[t].deprel
            if self[t] is self[t].head:
              result+="\n"
            else:
              result+="-"+str(self[t].head.id)+"\n"
        result+="EOS\n"
      if format==3:
        result+="<sentence>\n"
        for i,d,t,h,f,w,z in self._chunkinfo[k]:
          result+=' <chunk id="'+str(i)+'" link="'+str(d)+'" rel="D" score="0.000000" head="'+str(self[s[i][h]].id)+'" func="'+str(self[s[i][f]].id)+'">\n'
          for t in s[i]:
            result+='  <tok id="'+str(self[t].id)+'" feature="'+self._features[t]+'" head="'+str(self[t].head.id)+'" rel="'+self[t].deprel+'">'+self[t].form+'</tok>\n'
          result+=" </chunk>\n"
        result+="</sentence>\n"
    return result
  def size(self):
    return len(self)-1
  def token_size(self):
    return len(self)-1
  def token(self,index):
    if not hasattr(self,"_sentences"):
      self._makeChunks()
    c=None
    for s1,s2 in zip(self._sentences,self._chunkinfo):
      for c1,c2 in zip(s1,s2):
        i,d,t,h,f,w,z=c2
        if t==index:
          c=Chunk(c1,c2)
          break
    return Token(self,c,index)
  def chunk_size(self):
    if not hasattr(self,"_sentences"):
      self._makeChunks()
    return sum(len(s) for s in self._sentences)
  def chunk(self,index):
    if not hasattr(self,"_sentences"):
      self._makeChunks()
    for s1,s2 in zip(self._sentences,self._chunkinfo):
      for c1,c2 in zip(s1,s2):
        i,d,t,h,f,w,z=c2
        if z==index:
          return Chunk(c1,c2)
    return None
  def sentence_size(self):
    if not hasattr(self,"_sentences"):
      self._makeChunks()
    return len(self._sentences)
  def sentence(self,index=0):
    p=self._result.split("# text = ")
    return p[index+1].split("\n")[0]

class Chunk(object):
  additional_info=None
  feature_list_size=0
  score=0.0
  def __init__(self,chunk,chunkinfo):
    i,d,t,h,f,w,z=chunkinfo
    self.token_pos=t
    self.head_pos=h
    self.func_pos=f
    self.link=-1 if d<0 else d-i+z
    self.token_size=len(chunk)
    self._surface=w
  def __repr__(self):
    return self._surface
  def feature_list(self,index):
    return None

class Token(object):
  additional_info=ne=None
  def __init__(self,tree,chunk,index):
    self.surface=self.normalized_surface=tree[index+1].form
    self.chunk=chunk
    if not hasattr(tree,"_features"):
      tree._makeFeatures()
    self.feature=tree._features[index+1]
    self.feature_list_size=len(self.feature.split(","))
  def __repr__(self):
    return self.normalized_surface
  def feature_list(self,index):
    return self.feature.split(",")[index]

class UniDic2CaboCha(object):
  def __init__(self,UniDic):
    self.UniDic2UD=unidic2ud.UniDic2UD(UniDic,"japanese-gsd")
  def parse(self,sentence):
    return Tree(self.UniDic2UD(sentence,raw=True))
  def parseToString(self,sentence):
    return self.parse(sentence).toString(0)

def Parser(UniDic=None):
  if UniDic==None:
    UniDic="ipadic"
  return UniDic2CaboCha(UniDic)

