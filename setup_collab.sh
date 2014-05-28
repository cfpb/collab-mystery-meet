#!/bin/bash

git clone https://github.com/cfpb/collab.git

mv collab/collab/local_settings_template.py collab/collab/local_settings.py

echo "INSTALLED_APPS += ('mystery', )" >> collab/collab/local_settings.py
echo "INSTALLED_APPS += ('staff_directory', )" >> collab/collab/local_settings.py

pip install -r collab/requirements.txt
pip install -r collab/requirements-test.txt

git clone https://github.com/cfpb/collab-staff-directory.git

cd collab
ln -s ../mystery
ln -s ../collab-staff-directory/staff_directory
