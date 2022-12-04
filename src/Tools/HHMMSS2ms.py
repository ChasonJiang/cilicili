def HHMMSS2ms(string:str):
    s1 = string.split(".")
    s2 = s1[0].split(":")
    ms = float(s2[0])*60*60*1000  +float(s2[1])*60*1000 + float(s2[2])*1000
    if len(s1)>1:
        ms += float(s1[1][0:3])
    return ms


if __name__ == "__main__":
    print(HHMMSS2ms("00:00:05.013000000"))