#!/bin/sh

basedir=`dirname $0`
libraries_path=libraries
libraries=libraries/*
tags="0.2.0 0.3.0 0.3.1 0.4.0 0.4.2 0.5.0 0.5.2 0.6.0-beta1 trunk"

tags_url="https://svn.apache.org/repos/asf/libcloud/tags"
trunk_url="https://svn.apache.org/repos/asf/libcloud/trunk"

# Checkout tags and trunk
for tag in $tags
do
    if [ $tag == "trunk" ]; then
        url=${trunk_url}
        path="${libraries_path}/trunk"

        echo "Checking out trunk"
    else
        url="${tags_url}/${tag}"
        name="v${tag//\./}"
        name="${name//\-/}"
        path="${libraries_path}/${name}"

        if [ -d $path ]; then
            echo "Tag ${tag} already checked out, skipping.."
            continue
        fi

        echo "Checking out tag: ${tag}"
    fi

    svn checkout ${url} ${path}
done

# Creating __init__.py files
for file in $libraries
do
    init_path="${file}/__init__.py"
    if [ ! -f $init_path ]; then
        echo "Creating file: ${init_path}"
        touch $init_path
    fi
done
