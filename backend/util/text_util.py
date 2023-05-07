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

    @staticmethod
    def justify(initial_pad, objs): # objs: list of lists
        maxes = {}
        for obj in objs:
            for i, attr in enumerate(obj):
                attr_len = len(str(attr))
                maxes[i] = attr_len if i not in maxes else max(attr_len, maxes[i])

        obj_texts = []
        for obj in objs:
            attr_texts = []
            for i, attr in enumerate(obj):
                attr_texts.append(str(attr).ljust(maxes[i], " "))
            obj_texts.append(" " * initial_pad + " ".join(attr_texts))
        return "\n".join(obj_texts)