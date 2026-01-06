from random import randint

def dice():
    dice1 = randint(1,6)
    dice2 = randint(1,6)
    if dice1==dice2:
        return(dice1+dice2, True)
    return (dice1+dice2,False)
