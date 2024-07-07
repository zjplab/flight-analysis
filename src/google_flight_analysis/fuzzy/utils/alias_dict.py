class AliasKeyDict:
    """
    A dictionary that allows setting values with multiple keys(alias keys) using slash-separated syntax.
    """
    def __init__(self):
        self._data = {}
        self._aliases = {}

    def _process_keys(self, keys):
        """
        Process a slash-separated string of keys into a list of individual keys.
        
        Args:
            keys (str): A string of keys separated by slashes.
        
        Returns:
            list: A list of processed keys.
        """
        return [key.strip().lower() for key in keys.split('/')]

    def __setitem__(self, keys, value):
        """
        Set a value with multiple keys using slash-separated syntax.
        
        Args:
            keys (str): A string of keys separated by slashes.
            value (any): The value to be associated with the keys.
        """
        keys_list = self._process_keys(keys)
        main_key = keys_list[0]
        if isinstance(value, list):
            self._data[main_key] = self._parse_list(value)[0]
        else:
            self._data[main_key] = value
        for key in keys_list:
            self._aliases[key] = main_key
    
    def _parse_list(self, value_list:list[str]):
        parsed_list = []
        comments = []
        for elem in value_list:
            if "//" in elem:
                value, comment = elem.split("//", 1)
                parsed_list.append(value.strip())
                comments.append(comment.strip())
            else:
                parsed_list.append(elem.strip())
                comments.append('')
        return parsed_list, comments
                
        

    def __getitem__(self, key):
        """
        Get the value associated with a key.
        
        Args:
            key (str): The key to search for.
        
        Returns:
            any: The value associated with the key.
        
        Raises:
            KeyError: If the key is not found.
        """
        key = key.strip().lower()
        if key in self._aliases:
            main_key = self._aliases[key]
            return self._data[main_key]
        else:
            raise KeyError(f"Key '{key}' not found in the dictionary.")

    def __delitem__(self, key):
        """
        Remove a key and all its aliases from the dictionary.
        
        Args:
            key (str): The key to remove.
        
        Raises:
            KeyError: If the key is not found.
        """
        key = key.strip().lower()
        if key in self._aliases:
            main_key = self._aliases[key]
            keys_to_delete = [alias for alias, mapped_key in self._aliases.items() if mapped_key == main_key]
            for alias in keys_to_delete:
                del self._aliases[alias]
            del self._data[main_key]
        else:
            raise KeyError(f"Key '{key}' not found in the dictionary.")

    def __contains__(self, key):
        """
        Check if the dictionary contains a key.
        
        Args:
            key (str): The key to check for.
        
        Returns:
            bool: True if the key is found, False otherwise.
        """
        return key.strip().lower() in self._aliases

    def __str__(self):
        """
        Provide a string representation of the dictionary.
        
        Returns:
            str: The string representation of the dictionary, showing main keys and their aliases.
        """
        result = []
        processed_keys = set()
        for alias, main_key in self._aliases.items():
            if main_key not in processed_keys:
                aliases = [key for key, value in self._aliases.items() if value == main_key]
                result.append(f"Main Key: {main_key} -> Aliases: {aliases} -> Value: {self._data[main_key]}")
                processed_keys.add(main_key)
        return "\n".join(result)


# Example usage:
if __name__ == "__main__":
    mk_dict = AliasKeyDict()
    mk_dict['SFO/San Francisco/旧金山/三番'] = 'San Francisco International Airport'
    mk_dict['LAX/Los Angeles'] = 'Los Angeles International Airport'
    mk_dict['JFK/New York'] = 'John F. Kennedy International Airport'
    
    print(mk_dict['SFO'])  # Should print: San Francisco International Airport
    print(mk_dict['San Francisco'])  # Should print: San Francisco International Airport
    print(mk_dict['LAX'])  # Should print: Los Angeles International Airport
    print(mk_dict['New York'])  # Should print: John F. Kennedy International Airport

    # Check if keys are in the dictionary
    print('LAX' in mk_dict)  # Should print: True
    print('XYZ' in mk_dict)  # Should print: False

    # Remove a key and its aliases
    del mk_dict['LAX']
    print('LAX' in mk_dict)  # Should print: False
    print('Los Angeles' in mk_dict)  # Should print: False

    print('旧金山' in mk_dict)  # Should print: True
    print(mk_dict['旧金山'])  # Should print: San Francisco International Airport
    # Print the dictionary
    print(mk_dict)  # Should print the remaining dictionary contents
    
    print("Testing list parsing")
    mk_dict['ORD/Chicago'] = ['O\'Hare International Airport//shit airport', 'The busiest airport in the world // Comment Hello here']
    print(mk_dict['ORD'])