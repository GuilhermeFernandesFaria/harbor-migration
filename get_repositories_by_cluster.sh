#!/bin/bash

hour=$(date "+time-%H-%M")
file_csv="list_harbor-$hour.csv"



echo "Cluster;Project;Repository;Image name" >> $file_csv


for arg in $@; 
    do
        for cluster in $( kubectl ctx | grep -i "$arg");
            do 
                kubectl ctx $cluster

                if [[ $? == 0 ]]
                then
                    for ns in $( kubectl get ns --no-headers -o custom-columns=name:.metadata.name | egrep "*-prd|*-dev|*-hlg|*-sit|*-stg" )
                        do 
                            echo "NS --> $ns"

                            for deploy in $( kubectl get deploy -n $ns -o custom-columns=name:.metadata.name --no-headers )
                                do 
                                    echo "==========> $deploy"
                                    image=$(kubectl get deploy $deploy  -n $ns -o json | jq '.spec.template.spec.containers[0].image' | grep -i "harbor" | sed 's|"harbor01.viavarejo.com.br/||g' | cut -f1 -d ":")

                                    echo $image
                                    project=$(echo $image | awk -F  / '{print $1}')
                                    repo=$(echo $image | awk -F  / '{print $2}')
                                    name_img=$(echo $image | awk -F  / '{print $3}')

                                    echo "Project --> $project"
                                    echo "Repo --> $repo"
                                    echo "Name_img --> $name_img"
                                    echo ""

                                    echo "$cluster;$project;$repo;$name_img" >> $file_csv

                            done;
                    done;
                else
                    echo "$cluster not found."
                    continue
                fi;
        done;
done;