#! /usr/bin/python -i
# coding=utf-8

import os
PACKAGE_DIR=os.path.abspath(os.path.dirname(__file__))
DOWNLOAD_DIR=os.path.join(PACKAGE_DIR,"download")

UNIDIC_URL="https://unidic.ninjal.ac.jp/unidic_archive/"
UNIDIC_URLS={
  "gendai":UNIDIC_URL+"cwj/2.3.0/unidic-cwj-2.3.0.zip",
  "spoken":UNIDIC_URL+"csj/2.3.0/unidic-csj-2.3.0.zip",
  "qkana":UNIDIC_URL+"qkana/1603/UniDic-qkana_1603.zip",
  "kindai":UNIDIC_URL+"kindai/1603/UniDic-kindai_1603.zip",
  "kinsei":UNIDIC_URL+"kinsei/1603/UniDic-kinsei_1603.zip",
  "kyogen":UNIDIC_URL+"kyogen/1603/UniDic-kyogen_1603.zip",
  "wakan":UNIDIC_URL+"wakan/1603/UniDic-wakan_1603.zip",
  "wabun":UNIDIC_URL+"wabun/1603/UniDic-wabun_1603.zip",
  "manyo":UNIDIC_URL+"manyo/1603/UniDic-manyo_1603.zip"
}
UDPIPE_URL="https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2998/"
UDPIPE_VERSION="ud-2.4-190531"

def download(model,option=None):
  os.makedirs(DOWNLOAD_DIR,exist_ok=True)
  import logging
  logging.getLogger("pip._internal.download").setLevel(level=logging.INFO)
  from pip._internal.models.link import Link
  if option=="unidic":
    u=UNIDIC_URLS[model]
  elif option=="udpipe":
    u=False
  else:
    try:
      u=UNIDIC_URLS[model]
    except:
      u=False
  if u:
    from pip._internal.download import unpack_url
    unpack_url(Link(u),os.path.join(DOWNLOAD_DIR,model))
  else:
    from pip._internal.download import PipSession,_download_http_url
    _download_http_url(Link(UDPIPE_URL+model+"-"+UDPIPE_VERSION+".udpipe"),PipSession(),DOWNLOAD_DIR,None,"on")
    os.rename(os.path.join(DOWNLOAD_DIR,model+"-"+UDPIPE_VERSION+".udpipe"),os.path.join(DOWNLOAD_DIR,model+".udpipe"))

class UDPipeEntry(object):
  def __init__(self,result):
    if "\n" in result:
      t=[UDPipeEntry("0\t_\t_\t_\t_\t_\t0\t_\t_\t_")]
      for r in result.split("\n"):
        w=UDPipeEntry(r)
        if w.id>0:
          t.append(w)
      self._tokens=t
      for w in t:
        w._parent=self
        w.head=w._head
      self._result=result
    else:
      w=result.split("\t")
      try:
        w[0],w[6]=int(w[0]),int(w[6])
      except:
        w=[0]*10
      self.id,self.form,self.lemma,self.upos,self.xpos,self.feats,self._head,self.deprel,self.deps,self.misc=w if len(w)==10 else [0]*10
      self._result=""
  def __setattr__(self,name,value):
    v=value
    if name=="head":
      t=self._parent._tokens
      i=t.index(self)
      v=self if v==0 else t[i+v-self.id]
    if hasattr(self,name):
      if getattr(self,name)!=v:
        super(UDPipeEntry,self._parent).__setattr__("_result","")
        if name=="id":
          t=self._parent._tokens
          i=t.index(self)
          j=i+v-self.id
          super(UDPipeEntry,t[j]).__setattr__("id",t[i].id)
          t[i],t[j]=t[j],t[i]
    super(UDPipeEntry,self).__setattr__(name,v)
  def __repr__(self):
    if self._result!="":
      r=self._result
    elif hasattr(self,"_tokens"):
      r="".join(str(t)+"\n" for t in self._tokens[1:]).replace("\n1\t","\n\n1\t")
    else:
      r="\t".join([str(self.id),self.form,self.lemma,self.upos,self.xpos,self.feats,str(0 if self.head is self else self.head.id),self.deprel,self.deps,self.misc])
    return r if type(r) is str else r.encode("utf-8")
  def __getitem__(self,item):
    return self._tokens[item]
  def __len__(self):
    return len(self._tokens)
  def index(self,item):
    return self._tokens.index(item)
  def to_svg(self,item=0):
    if not hasattr(self,"_tokens"):
      return self._parent.to_svg(self._parent.index(self))
    s='<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"  width="100%" height="100%" onload="conllusvg.view(this,+conllu+)" onresize="conllusvg.rewrite(+conllu+)">\n'.replace("+","'")
    s+='<text id="conllu" fill="none" visibility="hidden">\n'
    if item==0:
      s+=str(self)
    else:
      from itertools import takewhile
      i=item-self[item].id
      for j in takewhile(lambda j:j-self[j].id==i,range(i+1,len(self))):
        s+=str(self[j])+'\n'
    s+='</text>\n<script type="text/javascript"><![CDATA[\n'
    f=open(os.path.join(PACKAGE_DIR,"conllusvgview.js"),"r")
    s+=f.read()
    f.close()
    s+=']]></script>\n</svg>\n'
    return s

class UniDic2UD(object):
  def __init__(self,UniDic,UDPipe):
    self.UniDic=UniDic
    if UniDic=="ipadic":
      import MeCab
      self.mecab=MeCab.Tagger().parse
    elif UniDic!=None:
      d=os.path.join(DOWNLOAD_DIR,UniDic)
      if os.path.isdir(d):
        import MeCab
        self.mecab=MeCab.Tagger("-d "+d).parse
      else:
        d={ "gendai":"dic1", "spoken":"dic2", "qkana":"dic3", "kindai":"dic4", "kinsei":"dic5", "kyogen":"dic6", "wakan":"dic7", "wabun":"dic8", "manyo":"dic9" }
        self.dictkey=d[UniDic]
        self.mecab=self.ChamameWebAPI
    self.model=UDPipe
    m=os.path.join(DOWNLOAD_DIR,self.model+".udpipe")
    if os.path.isfile(m):
      import ufal.udpipe
      self.model=ufal.udpipe.Model.load(m)
      if UniDic==None:
        self.udpipe=ufal.udpipe.Pipeline(self.model,"tokenizer=presegmented","","","").process
      else:
        self.udpipe=ufal.udpipe.Pipeline(self.model,"conllu","none","","").process
    else:
      self.udpipe=self.UDPipeWebAPI
  def __call__(self,sentence,raw=False):
    if self.UniDic==None:
      u=self.udpipe(sentence).replace("# newdoc\n# newpar\n","")
      if raw:
        return u
      return UDPipeEntry(u)
    f={ "接頭辞":"NOUN", "接頭詞":"NOUN", "代名詞":"PRON", "連体詞":"DET", "動詞":"VERB", "形容詞":"ADJ", "形状詞":"ADJ", "副詞":"ADV", "感動詞":"INTJ", "フィラー":"INTJ", "助動詞":"AUX", "接続詞":"CCONJ", "補助記号":"PUNCT", "記号":"SYM" }
    u=""
    for t in sentence.split("\n"):
      u+="# text = "+t+"\n"
      v=t
      misc=""
      id=0
      for s in self.mecab(t).split("\n"):
        i=s.find("\t")
        if i>0:
          form=s[0:i]
          a=s[i+1:].split(",")
          xpos=a[0]
          for t in a[1:4]:
            if t!="*" and t!="　" and t!="":
              xpos+="-"+t
          if self.UniDic=="ipadic":
            if len(a)>7:
              lemma=a[6]
              translit=a[7]
            else:
              lemma=translit=""
          elif len(a)<11:
            lemma=translit=""
          else:
            lemma=a[7]
            translit=a[6] if self.UniDic=="gendai" or self.UniDic=="spoken" else a[10]
          id+=1
        else:
          a=s.split(",")
          if len(a)<6:
            continue
          if a[1]=="B":
            id=1
          elif a[1]=="I":
            id+=1
          else:
            continue
          form=a[2]
          lemma=a[3]
          xpos=a[4]
          translit=a[5].replace("　","")
        if xpos=="空白" or xpos=="記号-空白":
          id-=1
          continue
        if v.startswith(form):
          v=v[len(form):]
        else:
          v=v[v.find(form)+len(form):]
          if misc=="SpaceAfter=No":
            u=u.rstrip("\t"+misc+"\n")+"\t_\n"
          elif "SpaceAfter=No|" in misc:
            u=u.rstrip(misc+"\n")+misc.replace("SpaceAfter=No|","")+"\n"
        lemma=lemma.replace("*","")
        i=lemma.find("-")
        if i>0:
          lemma=lemma[0:i]
        if lemma=="":
          lemma=form
        translit=translit.replace("*","")
        if translit==form:
          translit=""
        upos="X"
        x=(xpos+"-").replace("　","").split("-")
        if x[0]=="名詞":
          upos="NOUN"
          if x[1]=="固有名詞":
            upos="PROPN" 
          elif x[1]=="数詞" or x[1]=="数":
            upos="NUM"
          elif x[1]=="代名詞":
            upos="PRON"
        elif x[0]=="助詞":
          upos="ADP"
          if x[1]=="接続助詞":
            upos="SCONJ" if lemma=="て" else "CCONJ"
          elif x[1]=="終助詞":
            upos="PART" 
        elif x[0]=="接尾辞":
          upos="NOUN" if x[1]=="名詞的" else "PART"
        elif x[0] in f:
          upos=f[x[0]]
        misc="SpaceAfter=No" if translit=="" else "SpaceAfter=No|Translit="+translit
        u+="\t".join([str(id),form,lemma,upos,xpos,"_","_","_","_",misc])+"\n"
      u+="\n"
    if raw:
      return self.udpipe(u)
    return UDPipeEntry(self.udpipe(u))
  def ChamameWebAPI(self,sentence):
    import random,urllib.request,json
    f={ self.dictkey:"UniDic-"+self.UniDic, "st":sentence+"\n\n", "f1":"1", "f3":"1", "f10":"1", "out-e":"csv", "c-code":"utf-8" }
    b="".join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for i in range(10))
    d="\n".join("--"+b+"\nContent-Disposition:form-data;name="+k+"\n\n"+v for k,v in f.items())+"\n--"+b+"--\n"
    h={ "Content-Type":"multipart/form-data;charset=utf-8;boundary="+b }
    u=urllib.request.Request("https://unidic.ninjal.ac.jp/chamame/chamamebin/webchamame.php",d.encode(),h)
    with urllib.request.urlopen(u) as r:
      q=r.read()
    return q.decode("utf-8").replace("\r","")
  def UDPipeWebAPI(self,sentence):
    import urllib.request,urllib.parse,json
    c="http://lindat.mff.cuni.cz/services/udpipe/api/process?model="+self.model
    u=urllib.parse.quote(sentence)
    if self.UniDic==None:
      sp="\n"
      opt="&tokenizer=presegmented&tagger&parser"
    else:
      sp="\n\n"
      opt="&parser"
    if len(u)<8000:
      with urllib.request.urlopen(c+opt+"&data="+u) as r:
        q=r.read()
      return json.loads(q)["result"]
    u=""
    for t in sentence.split(sp):
      if t=="":
        continue
      with urllib.request.urlopen(c+opt+"&data="+urllib.parse.quote(t+sp)) as r:
        q=r.read()
      u+=json.loads(q)["result"]
    return u

def load(UniDic=None,UDPipe="japanese-gsd"):
  if UniDic==UDPipe:
    UniDic=None
  return UniDic2UD(UniDic,UDPipe)

