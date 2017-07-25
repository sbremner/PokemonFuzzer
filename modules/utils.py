import random

# Takes in a list of data and returns a list of weighted pairs
# A weighted pair is a tuple in the form:
#   (weight, item)
#       weight is an integer > 1
#       item can be anything
# The input list can contain two forms of data:
#   1. Individual items (default_weight is used to populate weight)
#   2. A weighted pair (weight, item)
def weighted_pairs(data, default_weight=1):
    if type(data) != list:
        raise TypeError("Parameter 'data' is not of type <list>")
        
    if type(default_weight) != int:
        raise TypeError("Parameter 'default_weight' is not of type <int>")
    
    if default_weight < 1:
        raise ValueError("Parameter 'default_weight' must be at least 1")
    
    pairs = []
    
    for d in data:
        # If it isn't a tuple, it must be an individual item
        if type(d) != tuple:
            pairs.append((default_weight, d))
        # Our item is a tuple (might be a valid weighted_pair)
        else:    
            # Extract the possible weight
            weight = d[0]
            
            # weight must be an int (otherwise this is not a valid weighted pair)
            if type(weight) != int:
                pairs.append((default_weight, d))
            # Type of weight was an int, fits the requirement for weighted_pair
            else:
                item = d[1:]
                
                # If our item is just one element, don't save value as a list
                if len(item) == 1:
                    item = item[0]
                    
                pairs.append((weight, item))
                
    return pairs

def weighted_random(pairs, default_weight=1):
    total = 0

    # Allow non-tuples as input using default_weight for the weight
    # total = sum(pairs[0] for pair in pairs)
    for pair in pairs:
        if type(pairs) == tuple:
            total += pairs[0]
        else:
            total += default_weight

    r = random.randint(1, total)
    
    for (weight, value) in pairs:
        r -= weight
        
        if r <= 0:
            return value