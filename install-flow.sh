pip install cmake cython opencv-python

# Install Flow
cd ~
git clone https://github.com/pcmoritz/flow.git
cd flow
git checkout web3d
pip install -e . --ignore-installed six
