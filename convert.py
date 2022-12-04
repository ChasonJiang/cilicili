import os
import sys

def findAllFile(base):
    for root, ds, fs in os.walk(base):
        for f in fs:
            fullname = os.path.join(root, f)
            yield fullname

def checkFileClass(path,fileclass):
    return path.split('.')[-1] == fileclass

def convertUI(indir,outdir):
    print("Convert begin")
    cmd="pyuic5 {} -o {}"
    for f in findAllFile(indir):
        if not checkFileClass(f,"ui"):
            continue
        mpath = os.sep.join(f.split(os.sep)[0:-2])
        filename = f.split(os.sep)[-1].split('.')[0]
        outname = filename+".py"
        save_dir = os.path.join(outdir,mpath)
        save_path = os.path.join(save_dir,outname)
        print("Convert {} to {}".format(f,save_path))
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        res=os.popen(cmd.format(f,save_path))
        print(res.read(),end="")
    print("Convert done")

def convertAssets(indir,outdir):
    print("Convert begin")
    cmd="pyrcc5 {} -o {}"
    for f in findAllFile(indir):
        if not checkFileClass(f,"qrc"):
            continue
        mpath = os.sep.join(f.split(os.sep)[0:-2])
        filename = f.split(os.sep)[-1].split('.')[0]
        outname = filename+".py"
        save_dir = os.path.join(outdir,mpath)
        save_path = os.path.join(save_dir,outname)
        print("Convert {} to {}".format(f,save_path))
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        res=os.popen(cmd.format(f,save_path))
        print(res.read(),end="")
    print("Convert done")



if __name__ == '__main__':
    # convertUI(sys.argv[1],sys.argv[2])
    # convertAssets(sys.argv[3],sys.argv[4])
    convertAssets("src\\player\\ui\\","src\\player\\ui\\")