import re
from connectors.core.connector import get_logger

logger = get_logger('fuzzy-search')


class Fuzzy_Search:

    def __init__(self):
        pass

    def set_ratio(self, str1, str2):
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


def filter_json_by_key_value(config, params):
    try:
        filter_data = []
        fuzzy_search = Fuzzy_Search()
        if isinstance(params['recordJSON'], list):
            for record in params['recordJSON']:
                record_value = record.get(str(params['targetKey']))
                if record_value is not None:
                    ratio = fuzzy_search.set_ratio(
                        str(params['targetKeyValue']), record_value)
                    if ratio >= params['similarityThreshold']:
                        filter_data.append(record)
            return filter_data
        elif isinstance(params['recordJSON'], dict):
            record_value = params['recordJSON'].get(str(params['targetKey']))
            if record_value is not None:
                ratio = fuzzy_search.set_ratio(
                    str(params['targetKeyValue']), record_value)
                if ratio >= params['similarityThreshold']:
                    filter_data.append(params['recordJSON'])
            return filter_data
    except Exception as err:
        logger.exception(str(err))
        raise Exception(err)


operations = {"filter_json_by_key_value": filter_json_by_key_value}
