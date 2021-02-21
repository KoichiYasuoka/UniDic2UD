#! /bin/sh
# 舞姬/雪國/荒野より-Benchmarks with spaCy and conll18_ud_eval.py
# https://github.com/KoichiYasuoka/UniDic2UD/tree/master/benchmark

MODULE=${1-'unidic2ud.spacy'}
LOAD=${2-'load("kindai")'}
CONLLU=${3-'maihime.conllu'}
TMP=/tmp/$MODULE.$$.$CONLLU

python3 -c '
import '$MODULE'
nlp='"$MODULE.$LOAD"'
with open("'$CONLLU'","r",encoding="utf-8") as f:
  r=f.read()
d=[]
for s in r.split("\n"):
  if s.startswith("# text = "):
    d.append(s[9:])
doc=nlp("\n".join(d))
with open("'$TMP'","w",encoding="utf-8") as f:
  for s in doc.sents:
    print("# text = "+str(s),file=f)
    for t in s:
      print("\t".join([str(t.i-s.start+1),t.orth_,t.lemma_,t.pos_,t.tag_,"_",str(0 if t.head==t else t.head.i-s.start+1),t.dep_.lower(),"_","_" if t.whitespace_ else "SpaceAfter=No"]),file=f)
    print("",file=f)
'
echo '###' $MODULE.$LOAD $CONLLU
python3 conll18_ud_eval.py $CONLLU $TMP
rm -f $TMP
exit 0
