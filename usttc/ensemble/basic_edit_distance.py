from usttc.ensemble.comparable_result import ComparableResult


def get_edit_distance(result_1: ComparableResult, result_2: ComparableResult):
    if len(result_1) > len(result_2):
        result_1, result_2 = result_2, result_1

    current_distances = range(len(result_1) + 1)
    for i2, c2 in enumerate(result_2):
        next_distances = [i2 + 1]
        for i1, c1 in enumerate(result_1):
            if c1 == c2:
                next_distances.append(current_distances[i1])
            else:
                next_distances.append(1 + min((current_distances[i1], current_distances[i1 + 1], next_distances[-1])))
        current_distances = next_distances
    return current_distances[-1]
