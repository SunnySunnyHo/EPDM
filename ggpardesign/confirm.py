def crun(cfactors):
    """runs the c code on lists of input values, returns the resulting Ry"""
    import os
    import string

    f = open("DUMP_FILE_PATCH", "w")
    #write the list to a file in the expected way
    for line in cfactors:
        lnth = range(len(line))
        lnth.reverse()
        for x, l in zip(line,lnth):
            if l == 0:
                f.write("%f\n"%x)
            else:
                f.write("%f|"%x)
    f.close()

    #run the c code
    os.system("./bridge")

    #read the results from the other file
    f = open("LOAD_FILE")
    
    c = []
    for line in f:
        c.append(line)
    c = map(lambda x: string.split(x), c[:])

    d = map(lambda x: map(lambda y: float(y), x), c)
    d = map(lambda x: x[0], d[:])

    f.close()
    #return the resulting values
    return d

def cgraph(filename):
    """creates a csv that can be graphed easily from a csv of input parameters"""
    #open up and read csv of designs to test
    import mainpatch
    import string
    #cfactors = mainpatch.dload(filename)
    f = open(filename)
    cfactors = []
    for line in f:
        cfactors.append(map(lambda x: float(x), string.split(line)))
    f.close()
    cf2= []
    for line in cfactors:
        Rc = (line[2]*line[1])/2
        cf2.append(line[0:2]+[Rc]+line[2:])
    #1000 points between plus and minus 0.2mA in a list
    pnts = 400
    oobc = map(lambda x: -0.002 + (0.004*x)/pnts, range(pnts))
    print oobc
    rd = []
    #for every row create a list of lists of control factors to evaluate 
    for line in cf2:
        cf3=[]
        for c in oobc:
            cf3.append(line + [c])
        #evaluate all currents
        out = crun(cf3)
        #reset values between plus and minus 0.2 mA to zero
        #slice up based on indexes of oobc
        oobci = map(lambda x: int(round(x*1000000)), oobc)
        #I really shouldn't be allowed to write code
        out = out[:oobci.index(-200)] + map(lambda x: 2, out[oobci.index(-200):oobci.index(200)+1]) + out[oobci.index(200):]
        #then save the results in a list
        rd.append(out)
    #then write the lists to a file
    f = open("rgraphs.csv", "w")
    for line in zip(oobc,*rd):
        ln = range(len(line))
        ln.reverse()
        for x in zip(line, ln):
            if x[1] == 0:
                f.write("%f\n"%x[0])
            else:
                f.write("%f,"%x[0])
    f.close()
    return None

if __name__ == "__main__":
    while 1:
        q = raw_input("evaluate confirmation run(cr) or csv of runs(csv)?")
        if q == "csv":
            #query for file name
            filename = raw_input("file name:")
            cgraph(filename)
            break
        elif q == "cr":
            import string
            #query for circuit input values
            icfactors = map(lambda x: float(x), string.split(raw_input("Ra,Rb,Rc,Rd,Ve,Vf:"), ","))
            cfactors = []
            cfactors.append(icfactors + [-0.0002])
            cfactors.append(icfactors + [0])
            cfactors.append(icfactors + [0.0002])
            #send this to crun
            out = crun(cfactors)
            #calculate delta y
            mean = out[1]
            dy1 = out[0]-mean
            dy2 = mean-out[2]
            print "circuit balanced at %s Ohms"%(mean)
            print "worst case delta y: %s"%(max([dy1,dy2]))
            break
