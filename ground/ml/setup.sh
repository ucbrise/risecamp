#!/bin/bash
dropdb risecamp;
createdb risecamp;
psql risecamp < risecamp.out;
psql risecamp -f permissions.sql;
python driver.py i;
echo '#!/usr/bin/env python' > my_cleaner.py;
echo 'import pandas as pd' >> my_cleaner.py;
echo 'import numpy as np' >> my_cleaner.py;
echo '' >> my_cleaner.py;
echo 'def clean(df):' >> my_cleaner.py;
echo '    pass' >> my_cleaner.py;