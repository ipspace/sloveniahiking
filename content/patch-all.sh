for i in */*/*.md; do
#  echo $i
  sed -i -e 's/mapzs.projekti.si/mapzs.pzs.si/g' "$i"
done
