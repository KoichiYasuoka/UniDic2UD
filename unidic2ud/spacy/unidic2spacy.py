#! /usr/bin/python3 -i
# coding=utf-8

import numpy
from spacy.language import Language
from spacy.symbols import LANG,NORM,LEMMA,POS,TAG,DEP,HEAD
from spacy.tokens import Doc,Span,Token
from spacy.util import get_lang_class
from unidic2ud.cabocha import Tree

class UniDicLanguage(Language):
  lang="ja"
  max_length=10**6
  def __init__(self,UniDic,UDPipe):
    self.Defaults.lex_attr_getters[LANG]=lambda _text:"ja"
    try:
      self.vocab=self.Defaults.create_vocab()
      self.pipeline=[]
    except:
      from spacy.vocab import create_vocab
      self.vocab=create_vocab("ja",self.Defaults)
      self._components=[]
      self._disabled=set()
    self.tokenizer=UniDicTokenizer(UniDic,UDPipe,self.vocab)
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
    feats=[]
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
      id,form,lemma,upos,xpos,feat,head,deprel,dummy_deps,misc=s
      words.append(form)
      lemmas.append(vs.add(lemma))
      pos.append(vs.add(upos))
      tags.append(vs.add(xpos))
      feats.append(feat)
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
    try:
      doc.is_tagged=True
      doc.is_parsed=True
    except:
      for i,j in enumerate(feats):
        if j!="_" and j!="":
          doc[i].set_morph(j)
    t=Tree(u)
    t._makeChunks()
    bunsetu=["I"]*len(doc)
    for s in t._cabocha._sentences:
      for w in s:
        try:
          bunsetu[w[0]-1]="B"
        except:
          pass
    doc.user_data["bunsetu_bi_labels"]=bunsetu
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
  def dictionary_form(self):
    return self.normalized_form()
  def reading_form(self):
    try:
      return self.morph_line[1].split(",")[10]
    except:
      return ""
  def split(self,mode):
    return [self]

def load(UniDic=None,parser="japanese-modern"):
  if parser==None:
    return UniDicLanguage(UniDic,None)
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
    l=item.lemma_
    if l=="":
      l="_"
    t=item.tag_
    if t=="":
      t="_"
    try:
      f=str(item.morph)
      if f.startswith("<spacy") or f=="":
        f="_"
    except:
      f="_"
    return "\t".join([str(item.i+offset),item.orth_,l,item.pos_,t,f,str(0 if item.head==item else item.head.i+offset),item.dep_.lower(),"_",m])
  return "".join(to_conllu(s)+"\n" for s in item)

def bunsetu_spans(doc):
  if type(doc)==Doc:
    b=[i for i,j in enumerate(doc.user_data["bunsetu_bi_labels"]) if j=="B"]
    b.append(len(doc))
    return [Span(doc,i,j) for i,j in zip(b,b[1:])]
  elif type(doc)==Span:
    b=doc[0].doc.user_data["bunsetu_bi_labels"]
    s=[bunsetu_span(doc[0])] if b[doc[0].i]=="I" else []
    for t in doc:
      if b[t.i]=="B":
        s.append(bunsetu_span(t))
    return s
  elif type(doc)==Token:
    return [bunsetu_span(doc)]

def bunsetu_span(token):
  b="".join(token.doc.user_data["bunsetu_bi_labels"])+"B"
  return Span(token.doc,b.rindex("B",0,token.i+1),b.index("B",token.i+1))

