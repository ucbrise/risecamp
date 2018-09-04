# Install SUMO
cd ~
git clone https://github.com/eclipse/sumo.git
cd sumo
git checkout 1d4338ab80
make -f Makefile.cvs
./configure
make -j10
