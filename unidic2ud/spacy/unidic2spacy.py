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
    self._meta = {
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

def load(UniDic=None,UDPipe="japanese-modern"):
  if UniDic==UDPipe:
    UniDic=None
  return UniDicLanguage(UniDic,UDPipe)

def to_conllu(item,offset=1):
  if type(item)==Doc:
    return "".join(to_conllu(s)+"\n" for s in item.sents)
  elif type(item)==Span:
    return "# text = "+str(item)+"\n"+"".join(to_conllu(t,1-item.start)+"\n" for t in item)
  elif type(item)==Token:
    m="_" if item.whitespace_ else "SpaceAfter=No"
    if item.norm_!="":
      if item.norm_!=item.orth_:
        m+="|Translit="+item.norm_
        m=m.replace("_|","")
    return "\t".join([str(item.i+offset),item.orth_,item.lemma_,item.pos_,item.tag_,"_",str(0 if item.head==item else item.head.i+offset),item.dep_.lower(),"_",m])
  return "".join(to_conllu(s)+"\n" for s in item)

