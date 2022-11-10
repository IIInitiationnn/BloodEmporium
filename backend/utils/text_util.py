class TextUtil:
    @staticmethod
    def camel_case(text: str):
        text2 = "".join([i for i in text if i.isalpha() or i == " "]).title().replace(" ", "")
        return text2[0].lower() + text2[1:]

    @staticmethod
    def title_case(text: str):
        return text.replace("_", " ").title()

    @staticmethod
    def pynput_to_key_string(listener, key):
        key_string = listener.canonical(key)
        try:
            key_string = key_string.char
        except AttributeError:
            key_string = str(key_string).replace("Key.", "")
        return key_string