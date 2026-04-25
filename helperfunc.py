def centerMsg(msg):
    return (128 - len(msg) * 8) // 2

def convertTime(x):
    sec = x%60
    mins = int(x/60)%60