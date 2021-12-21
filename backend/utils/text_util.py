class TextUtil:
    @staticmethod
    def camel_case(text: str):
        text2 = "".join([i for i in text if i.isalpha() or i == " "]).title().replace(" ", "")
        return text2[0].lower() + text2[1:]

    @staticmethod
    def title_case(text: str):
        return text.replace("_", " ").title()
