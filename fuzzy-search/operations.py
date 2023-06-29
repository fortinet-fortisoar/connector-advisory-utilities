import re
import difflib
from connectors.core.connector import get_logger

logger = get_logger('fuzzy-search')


class Fuzzy_Search:

    def __init__(self):
        pass

    def filter_data(self, json_record, params):
        for key, value in params['targetKeyValue'].items():
            record_value = json_record.get(key)
            if record_value is not None:
                ratio = self.set_ratio(
                    str(value), record_value, params)
                if ratio >= params['similarityThreshold']:
                    return True
                else:
                    return False

    def set_ratio(self, str1, str2, params):
        try:
            if str1 in str2 or str2 in str1:
                return 100

            count = 0
            # Unique within string
            modified_str1 = self.remove_special_characters(str1.lower())
            modified_str2 = list(
                set(self.remove_special_characters(str2.lower()).split(' ')))
            for data in ' '.join(modified_str2).split():
                if re.search(r'\b{0}\b'.format(data), modified_str1):
                    count += 1
                elif params['fuzzyMatch']:
                    params['limit'] = 5
                    if len(self.get_fuzzy_search_data(data, modified_str1, params)) > 0:
                        count += 1
            if len(modified_str2) <= len(modified_str1.split(' ')):
                return round(count / len(modified_str2) * 100)
            return round(count / len(modified_str1.split(' ')) * 100)
        except Exception as err:
            logger.exception(str(err))
            raise Exception(err)

    def remove_special_characters(self, text):
        try:
            return re.sub(r'[^\w\s]', ' ', text)
        except Exception as err:
            logger.exception(str(err))
            raise Exception(err)

    def get_fuzzy_search_data(self, keyword_to_search, targetText, params):
        return difflib.get_close_matches(keyword_to_search, targetText.split(
            ' '), n=params['limit'], cutoff=params['cutoff']/100)


def filter_json_by_key_value(config, params):
    try:
        filter_data = []
        fuzzy_search = Fuzzy_Search()
        if isinstance(params['recordJSON'], list):
            for record in params['recordJSON']:
                if fuzzy_search.filter_data(record, params):
                    filter_data.append(record)
            return filter_data
        elif isinstance(params['recordJSON'], dict):
            if fuzzy_search.filter_data(params['recordJSON'], params):
                filter_data.append(params['recordJSON'])
            return filter_data
    except Exception as err:
        logger.exception(str(err))
        raise Exception(err)


def search_keyword_in_text(config, params):
    searched_result = []
    fuzzy_search = Fuzzy_Search()
    if isinstance(params['keywordToSearch'], str):
        fuzzy_match = fuzzy_search.get_fuzzy_search_data(
            params['keywordToSearch'], params['targetText'], params)
        if len(fuzzy_match) > 0:
            for item in fuzzy_match:
                searched_result.append(item)
    elif isinstance(params['keywordToSearch'], list):
        for data in params['keywordToSearch']:
            fuzzy_match = fuzzy_search.get_fuzzy_search_data(
                data, params['targetText'], params)
            if len(fuzzy_match) > 0:
                for item in fuzzy_match:
                    searched_result.append(item)
    return searched_result


operations = {"filter_json_by_key_value": filter_json_by_key_value,
              "search_keyword_in_text": search_keyword_in_text}
