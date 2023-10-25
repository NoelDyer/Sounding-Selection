def depth_tolerance(catzoc, depth):
    if catzoc.upper() == 'A1':  # Encoded value = 1
        depth_accuracy = 0.5 + (depth * 0.01)
    elif catzoc.upper() == 'A2':  # Encoded value = 2
        depth_accuracy = 1 + (depth * 0.02)
    elif catzoc.upper() == 'B':  # Encoded value = 3
        depth_accuracy = 1 + (depth * 0.02)
    elif catzoc.upper() == 'C':  # Encoded value = 4
        depth_accuracy = 2 + (depth * 0.05)
    elif catzoc.upper() == 'D' or catzoc.upper() == 'U':  # Encoded value > 4
        depth_accuracy = None

    return depth_accuracy
