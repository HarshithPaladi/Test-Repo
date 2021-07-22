def scope_test():
    def do_local():
        spam="local value"
    def do_nonlocal():
        nonlocal spam
        spam="non local value"
    def do_global():
        global spam
        spam="global value"
    spam="Test spam"
    do_local()
    print("after local assignment:",spam)
    do_nonlocal()
    print("after non local assignment:",spam)
    do_global()
    print("afeter global assigbnmenrt:",spam)
scope_test()
print("In the name of the Galactic senate","You are under arrest:", spam)