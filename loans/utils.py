def amortize_loan(P, r, n): #From wikipedia
    A = P * ((r*(1+r)**n)/ (((1+r)**n)-1))
    return A

def interest_payment(P, r, n):
    return P * r / n

