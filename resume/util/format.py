import shlex
import string


class FormatUtilies:
    """Methods for manipulating strings, lists, etc."""

    def split_keywords(self, input_str: str) -> list[str]:
        """Return list of keywords, with quoted phrases intact."""
        return shlex.split(input_str)

    # TODO: Merge with remove_punctuation_list
    def remove_punctuation(self, orig: str) -> str:
        """Remove punctuation from string (helper for remove_punctuation_list())."""
        return " ".join(word.strip(string.punctuation) for word in orig.split())

    def remove_punctuation_list(self, og_list: list[str]) -> list[str]:
        """Remove punctuation from all strings in list, for better matching."""
        return [self.remove_punctuation(i) for i in og_list]

    def remove_empty_str_from_list(self, og_list: list[str]) -> list[str]:
        """Remove any "" items from list.

        Run this after remove_punctuation. Useful if keyword query contained
        a sequence like `word - word2`, which would generate a blank element.
        """
        fixed_list: list[str] = [i for i in og_list if i]
        return fixed_list

    def remove_duplicates_from_list(self, og_list: list[str]) -> list[str]:
        """Remove duplicate items from list.

        Used to prevent display of duplicate headers, in DataFiltering class.
        """
        no_dups: list[str] = []
        [no_dups.append(x) for x in og_list if x not in no_dups]
        return no_dups

    def format_keywords(self, kw_str: str) -> list[str]:
        """Format keywords properly for database & CSV."""
        kw_list: list[str] = self.split_keywords(kw_str)
        kw_formatted = self.remove_punctuation_list(kw_list)
        kw_formatted = self.remove_empty_str_from_list(kw_formatted)
        kw_formatted: list[str] = self.remove_duplicates_from_list(kw_formatted)
        return kw_formatted
