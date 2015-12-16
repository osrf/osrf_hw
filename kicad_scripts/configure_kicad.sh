#!/bin/bash

usage()
{
    echo ""
    echo "usage: ./configure_kicad.sh <cmd>"
    echo "possible <cmd>:"
    echo "      --install-update-modules    (clone/update all the modules from KiCad github organization and populate the kicad workspace)"
    echo "      --install-update-libraries  (clone/update libraries from kicad-library repo and populate the kicad workspace)"
    echo "      --install-update-3dmodels   (clone/update 3dmodels from osrf_hw_nonfree repo and populate the kicad workspace)"
    echo "      --install-update-utils      (clone/update and install utils to parse and modify kicad files)"
    echo "      --update-kicad-config       (update the kicag configuration files in ~/.config/kicad)"
    echo "      --all                       (all the previous commands sequentialy)"

}

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

checkout_or_update_modules()
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
                # That way those repos can serve as pretty libraries
    
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

checkout_or_update_repo()
{
    if [ ! -e "$WORKING_TREES/$2" ];then
        git clone "https://github.com/$1/$2" "$WORKING_TREES/$2"
    else
        cd "$WORKING_TREES/$2"
        git pull
    fi
}

update_config_files()
{
    MODULE_LIST=$(ls $MODULE_DIR)
    FILENAME=$HOME/.config/kicad/fp-lib-table
    # Creating fp-lib-table if doesn't exist
    if [ ! -f $FILENAME ];then
        echo "$FILENAME doesnt exist, creating a new footprint library table file"
        touch $FILENAME
    fi

    # Adding KiCad modules
    echo "(fp_lib_table" > "$FILENAME"
    for mod in $MODULE_LIST;do
        echo "  (lib (name ${mod%".pretty"})(type KiCad)(uri \${KISYSMOD}/$mod)(options \"\")(descr \"\"))" >> "$FILENAME"    
    done
    
    # Adding osrf modules
    MODULE_LIST=$(ls "$WORKING_TREES/osrf_hw/kicad_modules")
    for mod in $MODULE_LIST;do
        echo "  (lib (name ${mod%".pretty"})(type KiCad)(uri \${KIWORKSPACE}/osrf_hw/kicad_modules/$mod)(options \"\")(descr \"\"))" >> "$FILENAME"    
    done
        echo ")" >> "$FILENAME"    
    
    # Update the global kicad config file
    CONFFILE=$HOME/.config/kicad/kicad_common
    if [ -f $CONFFILE ];then
        declare -A arr=( ["Editor"]="/usr/bin/vim" ["KISYSMOD"]="$MODULE_DIR" ["KISYS3DMOD"]="$MODELS_DIR" ["KIWORKSPACE"]="$WORKING_TREES" ["KISYSLIB"]="$LIB_DIR")
        for key in ${!arr[@]};do
            if grep -q "$key *=" $CONFFILE; then
                sed -i "s#\(${key} *= *\).*#\1${arr[${key}]}#" $CONFFILE
            else
                echo "$key=${arr[${key}]}" >> $CONFFILE
            fi
        done
    else
        echo "file $CONFFILE doesnt exist, please open KiCad software and launch eeschema or pcbnew to create it"
    fi
    
    # add the BOM scripts to eeschema
    EESCHEMAFILE=$HOME/.config/kicad/eeschema
    if [ -f $EESCHEMAFILE ];then
        declare -A arr=( ["FieldNames"]="(templatefields (field (name MFN)(value _)) (field (name MFP)(value _)) (field (name D1)(value digikey)) (field (name D2)(value mouser)) (field (name D1PN)(value _)) (field (name D1PL)(value _)) (field (name D2PN)(value _)) (field (name D2PL)(value _)) (field (name Package)(value _)) (field (name Description)(value _) visible) (field (name Voltage)(value _)) (field (name Power)(value _)) (field (name Tolerance)(value _)) (field (name Temperature)(value _)) (field (name ReverseVoltage)(value _)) (field (name ForwardVoltage)(value _)) (field (name Cont.Current)(value _)) (field (name Frequency)(value _)) (field (name ResonnanceFreq)(value _)))" ["bom_plugins"]="(plugins  (plugin generateBOM (cmd \"python \\\\\\\\\"$WORKING_TREES/osrf_hw/kicad_scripts/editSch.py\\\\\\\\\" \\\\\\\\\"%I\\\\\\\\\" \\\\\\\\\"%O.csv\\\\\\\\\" generate\"))  (plugin editBOM_SCH_PyQt (cmd \"python \\\\\\\\\"$WORKING_TREES/osrf_hw/kicad_scripts/editSch.py\\\\\\\\\" \\\\\\\\\"%I\\\\\\\\\" \\\\\\\\\"%O\\\\\\\\\" edit\")))" ["bom_plugin_selected"]="editBOM_SCH_PyQt")
        for key in ${!arr[@]};do
            if grep -q "$key *=" $EESCHEMAFILE; then
                sed -i "s#\(${key} *= *\).*#\1${arr[${key}]}#" $EESCHEMAFILE
            else
                echo "$key=${arr[${key}]}" >> $EESCHEMAFILE
            fi
        done
    else
        echo "file $EESCHEMAFILE doesnt exist, please open KiCad software and launch eeschema to create it"
    fi
}

install_update_all_modules()
{
    checkout_or_update_modules "KiCad"

    #Replace fp-lib-table with list of all new modules
    MODULE_LIST=$(ls $MODULE_DIR)
    FILENAME=$HOME/.config/kicad/fp-lib-table
    # Creating fp-lib-table if doesn't exist
    if [ ! -f $FILENAME ];then
        echo "$FILENAME doesnt exist, creating a new footprint library table file"
        touch $FILENAME
    fi

    # Adding KiCad modules
    echo "(fp_lib_table" > "$FILENAME"
    for mod in $MODULE_LIST;do
        echo "  (lib (name ${mod%".pretty"})(type KiCad)(uri \${KISYSMOD}/$mod)(options \"\")(descr \"\"))" >> "$FILENAME"    
    done
    
    # Adding osrf modules
    MODULE_LIST=$(ls "$WORKING_TREES/osrf_hw/kicad_modules")
    for mod in $MODULE_LIST;do
        echo "  (lib (name ${mod%".pretty"})(type KiCad)(uri \${KIWORKSPACE}/osrf_hw/kicad_modules/$mod)(options \"\")(descr \"\"))" >> "$FILENAME"    
    done
        echo ")" >> "$FILENAME"    
}

# beginning of main script
b="osrf_hw"
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
while [ "$( basename "$DIR" )" != "$b" ];do
    DIR=$( dirname "$DIR" )
done

DIR=$( dirname "$DIR" )
WORKING_TREES=$DIR

DIRS="3dmodels modules libraries"
for dirtocreate in $DIRS;do
    if [ ! -d "$WORKING_TREES/resources/$dirtocreate" ]; then
        mkdir -p "$WORKING_TREES/resources/$dirtocreate"
    fi
done

MODULE_DIR="$WORKING_TREES/resources/modules"
LIB_DIR="$WORKING_TREES/resources/libraries"
MODELS_DIR="$WORKING_TREES/resources/3dmodels"


if [ $# -eq 1 -a "$1" == "--install-update-modules" ]; then
    ##FIXME not use kicatTools organization ?
    install_update_all_modules
    exit
fi

if [ $# -eq 1 -a "$1" == "--install-update-libraries" ]; then
#    checkout_or_update_repo "keulYSMB" "kicad-library"
    checkout_or_update_repo "KiCad" "kicad-library"
    # copy content in workspace resources
    cp -r "$WORKING_TREES/kicad-library/library"/* "$LIB_DIR"
    #FIXME should copy only the .3dshape folders ?
    cp -r "$WORKING_TREES/kicad-library/modules/packages3d"/* "$MODELS_DIR"
    exit
fi

if [ $# -eq 1 -a "$1" == "--install-update-utils" ]; then
    checkout_or_update_repo "keulYSMB" "kicad-library-utils"
    cd "$WORKING_TREES/kicad-library-utils"
    sudo python setup.py install
    exit
fi

if [ $# -eq 1 -a "$1" == "--install-update-3dmodels" ]; then
    checkout_or_update_repo "osrf" "osrf_hw_nonfree"
    exit
fi

if [ $# -eq 1 -a "$1" == "--update-kicad-config" ]; then
    update_config_files
    exit
fi

if [ $# -eq 1 -a "$1" == "--all" ]; then
    install_update_all_modules

    checkout_or_update_repo "KiCad" "kicad-library"
    # copy content in workspace resources
    cp -r "$WORKING_TREES/kicad-library/library"/* "$LIB_DIR"
    #FIXME should copy only the .3dshape folders ?
    cp -r "$WORKING_TREES/kicad-library/modules/packages3d"/* "$MODELS_DIR"

    checkout_or_update_repo "osrf" "osrf_hw_nonfree"

    checkout_or_update_repo "keulYSMB" "kicad-library-utils"
    cd "$WORKING_TREES/kicad-library-utils"
    sudo python setup.py install

    update_config_files
    exit
fi
usage

