benchmarks=("bm_json_dumps" "bm_deltablue" "bm_mako" "bm_pidigits" "bm_regex_v8")

for i in "${benchmarks[@]}"
do
	wsk -i action create $i --kind python:3 $i/$i.zip --web true
done
