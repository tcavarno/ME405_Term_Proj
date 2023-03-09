from array import array
gaus_kern_5x5 = array('f',[0,.01,.01,.01,0,.01,.05,.11,.05,.01,.01,.11,.25,.11,.01,.01,.05,.11,.05,.01,0,.01,.01,.01,0])

def 

if __name__ == "__main__":
    for i in range(0,25,5):
        print(gaus_kern_5x5[i:i+5])