import re
import difflib
from connectors.core.connector import get_logger

logger = get_logger('fuzzy-search')


class Fuzzy_Search:

    def __init__(self):
        pass

    # checks if json record contains value for provided key
    def is_record_found(self, key, value, json_record, params):
        record_value = json_record.get(key)
        if record_value is not None:
            calculated_threshold = self.calculate_threshold(
                str(value), record_value, params)
            if calculated_threshold >= params['similarityThreshold']:
                return True
            else:
                logger.debug(str("Threshold for value {0} in {1} is {2}".format(
                    value, json_record, calculated_threshold)))
                return False
        else:
            logger.debug(
                str("Value for key {0} in {1} is found none.".format(key, json_record)))
            return False

    # calculate threshold
    def calculate_threshold(self, text1, text2, params):
        try:
            if text1 in text2 or text2 in text1:
                return 100

            count = 0
            # Unique within string
            text1 = self.remove_special_characters(text1.lower())
            text2 = list(
                set(self.remove_special_characters(text2.lower()).split(' ')))

            for data in ' '.join(text2).split():
                # check boundary search
                if re.search(r'\b{0}\b'.format(data), text1):
                    count += 1
                # perform fuzzy search
                elif params['fuzzyMatch']:
                    params['limit'] = 5
                    if len(self.get_fuzzy_search_data(data, text1, params)) > 0:
                        count += 1
            if len(text2) <= len(text1.split(' ')):
                return round(count / len(text2) * 100)
            return round(count / len(text1.split(' ')) * 100)
        except Exception as err:
            logger.exception(str(err))
            raise Exception(err)

    def remove_special_characters(self, text):
        try:
            return re.sub(r'[^\w\s]', ' ', text)
        except Exception as err:
            logger.exception(str(err))
            raise Exception(err)

    def get_fuzzy_search_data(self, keyword_to_search, input_text, params):
        return difflib.get_close_matches(keyword_to_search, input_text.split(
            ' '), n=params['limit'], cutoff=params['cutoff']/100)

    def verify_threshold(self, threshold_value, key_name):
        if threshold_value in range(0, 101):
            return
        logger.exception(
            str("{0} value should be in range of 0 to 100".format(key_name)))
        raise Exception(
            str("{0} value should be in range of 0 to 100".format(key_name)))


def filter_json_by_key_value(config, params):
    try:
        filter_data = []
        fuzzy_search = Fuzzy_Search()
        fuzzy_search.verify_threshold(
            params['similarityThreshold'], "Similarity Threshold")
        if 'cutoff' in params.keys():
            fuzzy_search.verify_threshold(params['cutoff'], "Cut Off")
        if isinstance(params['inputJSON'], list):
            for json_record in params['inputJSON']:
                for key, value in params['targetKeyValue'].items():
                    if fuzzy_search.is_record_found(key, value, json_record, params) and json_record not in filter_data:
                        filter_data.append(json_record)
            return filter_data
        elif isinstance(params['inputJSON'], dict):
            for key, value in params['targetKeyValue'].items():
                if fuzzy_search.is_record_found(key, value, params['inputJSON'], params) and params['inputJSON'] not in filter_data:
                    filter_data.append(params['inputJSON'])
            return filter_data
    except Exception as err:
        logger.exception(str(err))
        raise Exception(err)


def search_keyword_in_text(config, params):
    searched_result = []
    fuzzy_search = Fuzzy_Search()
    fuzzy_search.verify_threshold(params['cutoff'], "Cut Off")
    if isinstance(params['keywordToSearch'], str):
        fuzzy_match = fuzzy_search.get_fuzzy_search_data(
            params['keywordToSearch'], params['inputText'], params)
        if len(fuzzy_match) > 0:
            for item in fuzzy_match:
                searched_result.append(item)
    elif isinstance(params['keywordToSearch'], list):
        for data in params['keywordToSearch']:
            fuzzy_match = fuzzy_search.get_fuzzy_search_data(
                data, params['inputText'], params)
            if len(fuzzy_match) > 0:
                for item in fuzzy_match:
                    searched_result.append(item)
    return searched_result


operations = {"filter_json_by_key_value": filter_json_by_key_value,
              "search_keyword_in_text": search_keyword_in_text}
