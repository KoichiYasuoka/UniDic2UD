#! /usr/bin/python3 -i
# coding=utf-8

import numpy
from spacy.language import Language
from spacy.symbols import LANG,NORM,LEMMA,POS,TAG,DEP,HEAD
from spacy.tokens import Doc,Span,Token
from spacy.util import get_lang_class

class UniDicLanguage(Language):
  lang="ja"
  max_length=10**6
  def __init__(self,UniDic,UDPipe):
    self.Defaults.lex_attr_getters[LANG]=lambda _text:"ja"
    self.vocab=self.Defaults.create_vocab()
    self.tokenizer=UniDicTokenizer(UniDic,UDPipe,self.vocab)
    self.pipeline=[]
    self._meta={
      "author":"Koichi Yasuoka",
      "description":"derived from UniDic2UD",
      "lang":"UniDic_"+UniDic if UniDic!=None else "udpipe_ja-modern",
      "license":"MIT",
      "name":UniDic if UniDic!=None else "ja-modern",
      "parent_package":"spacy_unidic",
      "pipeline":"Tokenizer, POS-Tagger, Parser",
      "spacy_version":">=2.1.0"
    }
    self._path=None

class UniDicTokenizer(object):
  to_disk=lambda self,*args,**kwargs:None
  from_disk=lambda self,*args,**kwargs:None
  to_bytes=lambda self,*args,**kwargs:None
  from_bytes=lambda self,*args,**kwargs:None
  def __init__(self,unidic,udpipe,vocab):
    import unidic2ud
    self.model=unidic2ud.load(unidic,udpipe)
    self.vocab=vocab
  def __call__(self,text):
    u=self.model(text,raw=True) if text else ""
    vs=self.vocab.strings
    r=vs.add("ROOT")
    words=[]
    lemmas=[]
    pos=[]
    tags=[]
    heads=[]
    deps=[]
    spaces=[]
    norms=[]
    for t in u.split("\n"):
      if t=="" or t.startswith("#"):
        continue
      s=t.split("\t")
      if len(s)!=10:
        continue
      id,form,lemma,upos,xpos,dummy_feats,head,deprel,dummy_deps,misc=s
      words.append(form)
      lemmas.append(vs.add(lemma))
      pos.append(vs.add(upos))
      tags.append(vs.add(xpos))
      if deprel=="root":
        heads.append(0)
        deps.append(r)
      else:
        heads.append(int(head)-int(id))
        deps.append(vs.add(deprel))
      spaces.append(False if "SpaceAfter=No" in misc else True)
      i=misc.find("Translit=")
      norms.append(vs.add(form if i<0 else misc[i+9:]))
    doc=Doc(self.vocab,words=words,spaces=spaces)
    a=numpy.array(list(zip(lemmas,pos,tags,deps,heads,norms)),dtype="uint64")
    doc.from_array([LEMMA,POS,TAG,DEP,HEAD,NORM],a)
    doc.is_tagged=True
    doc.is_parsed=True
    return doc

class MeCab2Sudachi(object):
  def __init__(self,UniDic):
    import unidic2ud
    self.tagger=unidic2ud.UniDic2UD(UniDic,None)
    self.UniDic=UniDic
  def __call__(self,text):
    r=[]
    for t in text.split("\n"):
      for s in self.tagger.mecab(t).split("\n"):
        if s=="" or s=="EOS":
          continue
        if s.find("\t")>0:
          if self.UniDic in {"gendai","spoken"}:
            b=s.split("\t")
            a=b[1].split(",")
            if len(a)>20:
              a[9]=a[20]
            if len(a)>10:
              a[10]=a[9]
            for i in range(len(a)):
              if a[i]=="":
                a[i]="*"
            r.append(UniDicMorph(b[0]+"\t"+",".join(a)))
          else:
            r.append(UniDicMorph(s))
        else:
          a=s.split(",")
          if a[1]!="B" and a[1]!="I":
            continue
          if a[4]=="名詞":
            p=["名詞","普通名詞","一般","*"]
          else:
            p=(a[4]+"-*-*-*-*").split("-")
          r.append(UniDicMorph(a[2]+"\t"+",".join([p[0],p[1],p[2],p[3],"*","*","*",a[3],a[2],a[5],a[5]])))
    return r

class UniDicMorph(object):
  def __init__(self,line):
    self.morph_line=line.split("\t")
  def surface(self):
    return self.morph_line[0]
  def part_of_speech(self):
    try:
      return self.morph_line[1].split(",")[0:6]
    except:
      return ["名詞","普通名詞","一般","*","*","*"]
  def normalized_form(self):
    try:
      n=self.morph_line[1].split(",")[7]
    except:
      return self.surface()
    i=n.find("-")
    if i<1:
      return n
    return n[0:i]
  def reading_form(self):
    try:
      return self.morph_line[1].split(",")[10]
    except:
      return ""

def load(UniDic=None,parser="japanese-modern"):
  if UniDic==parser:
    UniDic=None
  if UniDic==None or not parser.startswith("ja_"):
    return UniDicLanguage(UniDic,parser)
  import spacy
  nlp=spacy.load(parser)
  nlp.tokenizer.tokenizer.tokenize=MeCab2Sudachi(UniDic)
  return nlp

def to_conllu(item,offset=1):
  if type(item)==Doc:
    return "".join(to_conllu(s)+"\n" for s in item.sents)
  elif type(item)==Span:
    return "# text = "+str(item)+"\n"+"".join(to_conllu(t,1-item.start)+"\n" for t in item)
  elif type(item)==Token:
    m="_"
    if item.ent_iob_ in {"B","I"}:
      m="NE="+item.ent_iob_+"-"+item.ent_type_
    if not item.whitespace_:
      m+="|SpaceAfter=No"
    if item.norm_!="":
      if item.norm_!=item.orth_:
        m+="|Translit="+item.norm_
    m=m.replace("_|","")
    return "\t".join([str(item.i+offset),item.orth_,item.lemma_,item.pos_,item.tag_,"_",str(0 if item.head==item else item.head.i+offset),item.dep_.lower(),"_",m])
  return "".join(to_conllu(s)+"\n" for s in item)

