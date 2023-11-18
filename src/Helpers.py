from constants import *

def IsMateScore(score):
    if score == -INF:
        return False
    maxMateDepth = 1000
    return abs(score) > immediateMateScore - maxMateDepth


# Quicksort :)
def Partition(values, scores, low, high):
    pivotScore = scores[high]
    i = low - 1
    for j in range(low, high):
        if scores[j] > pivotScore:
            i += 1
            values[i], values[j] = values[j], values[i]
            scores[i], scores[j] = scores[j], scores[i]
    
    values[i + 1], values[high] = values[high], values[i + 1]
    scores[i + 1], scores[high] = scores[high], scores[i + 1]
    return i + 1

def Quicksort(values, scores, low, high):
    if low < high:
        pi = Partition(values, scores, low, high)
        Quicksort(values, scores, low, pi - 1)
        Quicksort(values, scores, pi + 1, high)
