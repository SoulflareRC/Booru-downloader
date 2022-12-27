import os
path = 'images/miazi-txt'
fs = os.listdir(path)
for idx,f in enumerate(fs):
    print(idx)
    with open(os.path.join(path,f),'r',encoding='utf8') as txt:
        try:
            print(txt.read())
        except:
            print(txt.name)
            exit(0)
