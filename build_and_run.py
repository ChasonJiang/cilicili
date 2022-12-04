import sys
from convert import convert
from main import main



if __name__ == "__main__":
    convert("./ui", "./src")
    main(sys.argv)
    
