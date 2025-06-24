# If there is 1 Applicability that is not True, the whole rule is True, because the rule does not apply, so it is passed. 
# If every Applicability is True, the rule needs to be further investigated.

def A_check(*args):
    for arg in args:
        if arg == False:
            return True
    return False

# If there is no Selection, that is not True, the whole rule is True, because the rule does not apply, so it is passed. 
# If there is 1 Selection that is True, the rule needs to be further investigated.

def S_check(*args):
    for arg in args:
        if arg == True:
            return False
    return True

# If there is 1 Exception that is True, the whole rule is True, because it is an exception, so it is passed. 
# If every Exception is False, the rule needs to be further investigated.

def E_check(*args):
    for arg in args:
        if arg == True:
            return True
    return False

# If the rule applies and it is not an exception then every Requirement needs to be True!
# If there is 1 Requirement that is not True, the check did not pass. 

def R_check(*args):
    for arg in args:
        if arg == False:
            return False
    return True

# The 4 separate checks are set up in a way that if 1 is True the check is passed. 

def rase_check(A, S, E, R):
    return A or S or E or R

A = A_check(True, True, True, True)
S = S_check(False, False, True)
E = E_check(False, True)
R = R_check(True, True, True, False)

RASE = rase_check(A, S, E, R)

print('A check:', A)
print('S check:', S)
print('E check:', E)
print('R check:', R)
print('RASE check:', RASE)

