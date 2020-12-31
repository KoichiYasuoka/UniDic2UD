#! /bin/sh
# 舞姬-Benchmark with spaCy and conll18_ud_eval.py

MODULE=${1-'spacy'}
LOAD=${2-'load("ja_core_news_sm")'}
CONLLU=${3-'maihime.conllu'}
TMP=/tmp/$MODULE.$$.$CONLLU

echo '###' $MODULE.$LOAD $CONLLU
python3 -c '
import '$MODULE'
nlp='"$MODULE.$LOAD"'
with open("'$CONLLU'","r",encoding="utf-8") as f:
  r=f.read()
for s in r.split("\n"):
  if s.startswith("# text = "):
    doc=nlp(s[9:])
    for t in doc:
      print("\t".join([str(t.i+1),t.orth_,t.lemma_,t.pos_,t.tag_,"_",str(0 if t.head==t else t.head.i+1),t.dep_.lower(),"_","_" if t.whitespace_ else "SpaceAfter=No"]))
    print("")
' > $TMP

python3 conll18_ud_eval.py $CONLLU $TMP
rm -f $TMP
exit 0
