
def classLoader(class_path, class_name):
    moud = __import__(class_path, fromlist=[class_name])
    # 实例化类
    clas = getattr(moud, class_name)
    return clas