def flatten(data, prefix="", result=None):

    if result is None:
        result = {}

    if isinstance(data, dict):

        for key, value in data.items():

            new_key = f"{prefix}_{key}" if prefix else key

            flatten(value, new_key, result)

    elif isinstance(data, list):

        if data:
            flatten(data[0], prefix, result)

    else:

        result[prefix] = data

    return result