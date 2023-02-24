import logging
from OfflineSuperResolution.run import run
logging.basicConfig(format='--> %(levelname)s : %(message)s', level=logging.ERROR) # DEBUG

if __name__ == '__main__':
    run()