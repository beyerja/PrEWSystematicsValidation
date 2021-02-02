#!/bin/bash

echo "#########################################################################"
echo "### Loading needed software versions ####################################" 
echo "#########################################################################"

# Load the config to determine the iLCSoft version
dir="$( cd "$( dirname "${BASH_SOURCE[0]}"  )" && pwd  )" # this script
config_dir="${dir}/../scripts/config"
. ${config_dir}/software.config

if [[ "${ILCSOFT}" == *"${ilcsoft_dir}"* ]]; then
  echo "iLCSoft version is already loaded."
elif [ ! -z "${ILCSOFT}" ]; then
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "ERROR: Another iLCSoft version is already loaded!"
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
else 
  echo "Loading iLCSoft - version: ${ilcsoft_version}"
  source ${ilcsoft_dir}/init_ilcsoft.sh
fi

# Add the MarlinHelp package path
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/afs/desy.de/group/flc/pool/beyerjac/TGCAnalysis/SampleProduction/MarlinAnalysis/MarlinHelp/lib