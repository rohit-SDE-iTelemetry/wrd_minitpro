#!/bin/bash
cd /home/rohit/Desktop/dev/env  #path to your virtual environment
. bin/activate  #Activate your virtual environment
cd /home/rohit/Desktop/dev/tpro_edge  #After that go to your project directory
python manage.py runserver  #run django server

