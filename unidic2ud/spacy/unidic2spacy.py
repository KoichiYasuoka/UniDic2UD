#! /usr/bin/python3 -i
# coding=utf-8

import numpy
from spacy.language import Language
from spacy.symbols import LEMMA,POS,TAG,DEP,HEAD
from spacy.tokens import Doc,Span,Token
from spacy.util import get_lang_class

class UniDicLanguage(Language):
  def __init__(self,UniDic,UDPipe):
    self._lang="ja"
    self.Defaults=get_lang_class("ja").Defaults
    self.vocab=self.Defaults.create_vocab()
    self.tokenizer=UniDicTokenizer(UniDic,UDPipe,self.vocab)
    self.pipeline=[]
    self.max_length=10**6
    self._meta = {
      "author":"Koichi Yasuoka",
      "description":"derived from UniDic2UD",
      "lang":"UniDic_"+UniDic if UniDic!=None else "udpipe_ja-gsd",
      "license":"MIT",
      "name":UniDic if UniDic!=None else "ja-gsd",
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
    words=[]
    lemmas=[]
    pos=[]
    tags=[]
    heads=[]
    deps=[]
    spaces=[]
    for t in u.split("\n"):
      if t=="" or t.startswith("#"):
        continue
      s=t.split("\t")
      if len(s)!=10:
        continue
      id,form,lemma,upos,xpos,dummy_feats,head,deprel,dummy_deps,misc=s
      words.append(form)
      lemmas.append(self.vocab.strings.add(lemma))
      pos.append(self.vocab.strings.add(upos))
      tags.append(self.vocab.strings.add(xpos))
      if deprel=="root":
        heads.append(0)
        deps.append(self.vocab.strings.add("ROOT"))
      else:
        heads.append(int(head)-int(id))
        deps.append(self.vocab.strings.add(deprel))
      spaces.append(False if "SpaceAfter=No" in misc else True)
    doc=Doc(self.vocab,words=words,spaces=spaces)
    a=numpy.array(list(zip(pos,tags,deps,heads)),dtype="uint64")
    doc.from_array([POS,TAG,DEP,HEAD],a)
    b=numpy.array([[lemma] for lemma in lemmas],dtype="uint64")
    doc.from_array([LEMMA],b)
    doc.is_tagged=True
    doc.is_parsed=True
    return doc

def load(UniDic=None,UDPipe="japanese-gsd"):
  if UniDic==UDPipe:
    UniDic=None
  return UniDicLanguage(UniDic,UDPipe)

def to_conllu(item,offset=1):
  if type(item)==Doc:
    return "".join(to_conllu(s)+"\n" for s in item.sents)
  elif type(item)==Span:
    return "# text = "+str(item)+"\n"+"".join(to_conllu(t,1-item.start)+"\n" for t in item)
  elif type(item)==Token:
    return "\t".join([str(item.i+offset),item.orth_,item.lemma_,item.pos_,item.tag_,"_",str(0 if item.head==item else item.head.i+offset),item.dep_.lower(),"_","_" if item.whitespace_ else "SpaceAfter=No"])
  return item

