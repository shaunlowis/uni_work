""" Script for calculating Pi using coinflips
    Idea by Greg Bodeker, written up by Johnny (Shaun) Lowis
"""

import random as rand


def flip_coin():
    coinflip = rand.randint(1, 2)
    if coinflip == 1:
        coinflip = "heads"
    elif coinflip == 2:
        coinflip = "tails"

    return coinflip


def calc_pi():

    M = 10000000
    N = 0
    i = 1

    while i < M:

        done = False
        xmax = ymax = 1
        xmin = ymin = 0
        x = y = delta = 0.5

        while done is False:

            delta = delta / 2

            h_t1 = flip_coin()

            if h_t1 == "heads":
                xmax = x
                x -= delta
            elif h_t1 == "tails":
                xmin = x
                x += delta

            h_t2 = flip_coin()

            if h_t2 == "heads":
                ymax = y
                y -= delta
            elif h_t2 == "tails":
                ymin = y
                y += delta

            if (xmin ** 2) + (ymin ** 2) > 1:
                done = True
            elif(xmax ** 2) + (ymax ** 2) <= 1:
                done = True
                N += 1

        i += 1

    return 4 * (N/M)


def main():

    pi = calc_pi()
    print(f"Calculated value for pi is: {pi}")


main()
