#!/bin/bash

detect_pretty_repos()
{
    # Check for the correct option to enable extended regular expressions in
    # sed. This is '-r' for GNU sed and '-E' for (older) BSD-like sed, as on
    # Mac OSX.
    if [ $(echo | sed -r '' &>/dev/null; echo $?) -eq 0 ]; then
        SED_EREGEXP="-r"
    elif [ $(echo | sed -E '' &>/dev/null; echo $?) -eq 0 ]; then
        SED_EREGEXP="-E"
    else
        echo "Your sed command does not support extended regular expressions. Cannot continue."
        exit 1
    fi

    # Use github API to list repos for provided organization, then subset the JSON reply for only
    # *.pretty repos
    PRETTY_REPOS=`curl https://api.github.com/orgs/$1/repos?per_page=2000 2> /dev/null \
        | grep full_name | grep pretty \
        | sed $SED_EREGEXP 's:.+ "'$1'/(.+)",:\1:'`
    echo "PRETTY_REPOS:$PRETTY_REPOS"

    PRETTY_REPOS=`echo $PRETTY_REPOS | tr " " "\n" | sort`

    echo "PRETTY_REPOS sorted:$PRETTY_REPOS"
}

checkout_or_update_libraries()
{
    if [ ! -d "$MODULE_DIR" ]; then
        sudo mkdir -p "$MODULE_DIR"
        echo " mark $MODULE_DIR as owned by me"
        sudo chown -R `whoami` "$MODULE_DIR"
    fi
    cd $MODULE_DIR

    for org in $1;do

        detect_pretty_repos $org
    
        for repo in $PRETTY_REPOS; do
            # echo "repo:$repo"
    
            if [ ! -e "$MODULE_DIR/$repo" ]; then
    
                # Preserve the directory extension as ".pretty".
                # That way those repos can serve as pretty libraries directly if need be.
    
                echo "installing $MODULE_DIR/$repo"
                git clone "https://github.com/$org/$repo" "$MODULE_DIR/$repo"
            else
                echo "updating $MODULE_DIR/$repo"
                cd "$MODULE_DIR/$repo"
                git pull
            fi
        done
    done
}

b="osrf_hw"
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
while [ "$( basename "$DIR" )" != "$b" ];do
    DIR=$( dirname "$DIR" )
done

DIR=$( dirname "$DIR" )
WORKING_TREES=$DIR
#echo "$WORKING_TREES"

DIRS="3dmodels modules libraries"
for dirtocreate in $DIRS;do
    if [ ! -d "$WORKING_TREES/resources/$dirtocreate" ]; then
        mkdir -p "$WORKING_TREES/resources/$dirtocreate"
    fi
done

MODULE_DIR="$WORKING_TREES/resources/modules"
LIB_DIR="$WORKING_TREES/resources/libraries"
MODELS_DIR="$WORKING_TREES/resources/3dmodels"
echo $MODULE_DIR

### clone osrf and kicad pretty repositories
#FIXME not use kicatTools organization ?
#checkout_or_update_libraries "kicadTools KiCad"
checkout_or_update_libraries "KiCad"


### clone/update kicad-library repo
if [ ! -e "$WORKING_TREES/kicad-library" ];then
    git clone "https://github.com/KiCad/kicad-library.git" "$WORKING_TREES/kicad-library"
else
    cd "$WORKING_TREES/kicad-library"
    git pull
fi
# copy content in workspace resources
cp -r "$WORKING_TREES/kicad-library/library"/* "$LIB_DIR"
#FIXME should copy only the .3dshape folders ?
cp -r "$WORKING_TREES/kicad-library/modules/packages3d"/* "$MODELS_DIR"

MODULE_LIST=$(ls $MODULE_DIR)
FILENAME=$HOME/.config/kicad/fp-lib-table
echo "(fp_lib_table" > "$FILENAME"
for mod in $MODULE_LIST;do
    echo "  (lib (name ${mod%".pretty"})(type KiCad)(uri \${KISYSMOD}/$mod)(options \"\")(descr \"\"))" >> "$FILENAME"    
done

## Now handling osrf libraries

MODULE_LIST=$(ls "$WORKING_TREES/osrf_hw/kicad_modules")
for mod in $MODULE_LIST;do
    echo "  (lib (name ${mod%".pretty"})(type KiCad)(uri \${KIWORKSPACE}/osrf_hw/kicad_modules/$mod)(options \"\")(descr \"\"))" >> "$FILENAME"    
done
    echo ")" >> "$FILENAME"    

### now update the global kicad config file
CONFFILE=$HOME/.config/kicad/kicad_common

declare -A arr=( ["Editor"]="/usr/bin/vim" ["KISYSMOD"]="$MODULE_DIR" ["KISYS3DMOD"]="$MODELS_DIR" ["KIWORKSPACE"]="$WORKING_TREES" ["KISYSLIB"]="$LIB_DIR")
for key in ${!arr[@]};do
    if grep -q "$key *=" $CONFFILE; then
        sed -i "s#\(${key} *= *\).*#\1${arr[${key}]}#" $CONFFILE
    else
        echo "$key=${arr[${key}]}" >> $CONFFILE
    fi
done

