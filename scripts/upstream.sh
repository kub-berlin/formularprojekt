mkdir -p .upstream

for form_id in $(ls data); do
    file="data/$form_id/form.json"
    tmp=".upstream/${form_id}.pdf"

    if [ -f $file ]; then
        url=$(grep '"url"' $file | sed 's/.*: "//;s/",\?$//')
        checksum=$(grep '"checksum"' $file | sed 's/.*: "//;s/",\?$//')

        wget --quiet "$url" -O $tmp

        actual=$(md5sum $tmp | sed 's/  .*//')

        if [ "$checksum" != "$actual" ]; then
            echo $form_id $url $actual
        fi
    fi
done
