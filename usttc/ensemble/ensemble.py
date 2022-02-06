from usttc.ensemble.comparable_result import ComparableResult
from usttc.ensemble.comparable_word import ComparableWord
from usttc.ensemble.comparable_diff_word import ComparableDiffWord


class Ensemble:
    def __init__(self):
        pass

    def ensemble(self, result_1: ComparableResult, result_2: ComparableResult):
        new_comparable_result = self._ensemble_two_comparable_result(result_1, result_2)
        return new_comparable_result

    @staticmethod
    def _ensemble_two_comparable_result(result_1: ComparableResult, result_2: ComparableResult):
        if len(result_1) > len(result_2):
            result_1, result_2 = result_2, result_1

        dir_matrix = []  # left+up: 0, left: 1, up: 2
        match_matrix = []
        current_distances = range(len(result_1) + 1)
        dir_matrix.append([1] * (len(result_1) + 1))
        match_matrix.append([True] + [False] * len(result_1))
        for i2, c2 in enumerate(result_2):
            next_distances = [i2 + 1]
            next_dir = [2]
            next_match = [False]
            for i1, c1 in enumerate(result_1):
                if c1 == c2:
                    next_distances.append(current_distances[i1])
                    next_dir.append(0)
                    next_match.append(True)
                else:
                    next_match.append(False)
                    if (current_distances[i1] <= current_distances[i1 + 1]) and \
                            (current_distances[i1] <= next_distances[-1]):
                        new_d = current_distances[i1]
                        next_dir.append(0)
                    elif next_distances[-1] <= current_distances[i1 + 1]:
                        new_d = next_distances[-1]
                        next_dir.append(1)
                    else:
                        new_d = current_distances[i1 + 1]
                        next_dir.append(2)
                    next_distances.append(1 + new_d)
            current_distances = next_distances
            dir_matrix.append(next_dir)
            match_matrix.append(next_match)

        row_i = len(dir_matrix) - 1
        col_i = len(dir_matrix[0]) - 1
        phrases = []
        diff_provider_list_map = dict()

        def add_words_to_diff_provider_list_map(words):
            for word in words:
                p_map = word.provider_word_map
                for p, w in p_map.items():
                    if p in diff_provider_list_map:
                        diff_provider_list_map[p].insert(0, w)
                    else:
                        diff_provider_list_map[p] = [w]

        while row_i or col_i:
            if dir_matrix[row_i][col_i] == 0:

                word_1 = result_1[col_i - 1]
                word_2 = result_2[row_i - 1]

                if match_matrix[row_i][col_i]:
                    if diff_provider_list_map:
                        phrases.insert(0, ComparableDiffWord(diff_provider_list_map))
                        diff_provider_list_map = dict()

                    provider_map = word_1.provider_word_map.copy()
                    provider_map.update(word_2.provider_word_map)
                    phrases.insert(0, ComparableWord(provider_map))

                else:
                    add_words_to_diff_provider_list_map([word_1, word_2])
                row_i -= 1
                col_i -= 1

            elif dir_matrix[row_i][col_i] == 1:
                add_words_to_diff_provider_list_map([result_1[col_i - 1]])
                col_i -= 1
            else:
                add_words_to_diff_provider_list_map([result_2[row_i - 1]])
                row_i -= 1

        if diff_provider_list_map:
            phrases.insert(0, ComparableDiffWord(diff_provider_list_map))

        new_comparable_result = ComparableResult()
        new_comparable_result.phrases = phrases
        return new_comparable_result
