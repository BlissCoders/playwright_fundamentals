from typing import List

from playwright.sync_api import expect, Locator


class HomePage:


    def __init__(self, page):
        self.page = page

        # Expected element values
        self.title = "Playwright"
        self.header_text = "QA Playwright Demo App"
        self.expected_instruction_text = "This application is designed to demonstrate:"
        self.expected_bullet_items =  [
            "Proper locator strategies",
            "Form validation testing",
            "Async loading behavior",
            "Dynamic filtering",
            "UI testing best practices"
        ]

        # Xpath/CSS locators
        self.header = "h1[data-testid='home-title']"
        self.bullet_items = "//div[@class='container']/ul/li"



    @classmethod
    def open(cls,page,url:str="https://blisscoders.pythonanywhere.com/")->'HomePage':
        page.goto(url)
        return cls(page)

    def get_title(self)-> str:
        return self.page.title()

    def get_header(self)-> Locator:
        return self.page.locator(self.header)

    def get_instruction(self)-> Locator:
        return self.page.get_by_text(self.expected_instruction_text)

    def get_bullet_items(self)-> List[Locator]:
        return self.page.locator(self.bullet_items).all()

    def verify_title(self, title:str=None):
        # if not title:
        #     expect(self.page.locator(self.header)).to_contain_text(title)
        # else:
        #     expect(self.page.locator(self.header)).to_contain_text(self.header_text)

        # Use provided title or fall back to the default header_text
        expected_text = title if title is not None else self.title

        # expect() automatically waits for the text to appear
        assert expected_text in self.get_title()


    def verify_header_text(self, header_text:str=None):
        # Should have a header text of "QA Playwright Demo App"
        # Validate the header text with CSS locator
        expected_header = header_text if header_text is not None else self.header_text
        header_element_text = self.get_header().inner_text()
        print(f"\nHeader:{header_element_text}")
        assert expected_header == header_element_text


    def verify_instruction_text(self, instruction_text:str=None):
        # Should have instruction text of "This application is designed to demonstrate:"
        # Validate the instruction text with playwright built-in get_by_text
        expected_instruction = instruction_text if instruction_text is not None else self.expected_instruction_text
        instruction_element_text = self.get_instruction().inner_text()
        print(f"\nInstruction Text:{instruction_element_text}")
        print(f"Expected instruction:{expected_instruction}")
        assert expected_instruction == instruction_element_text

    def verify_bullet_items(self, bullet_items:List[str]=None):
        """
        Should see five bullet points under instructions as follows:
            - Proper locator strategies
            - Form validation testing
            - Async loading behavior
            - Dynamic filtering
            - UI testing best practices
        """
        _expected_bullet_items = bullet_items if bullet_items is not None else self.expected_bullet_items

        # Get all bullet items
        bullets = self.get_bullet_items()

        # Validate all bullet points with XPath and loop elements
        for i, bullet in enumerate(bullets):
            print(f"Bullet text {i + 1}: {bullet.inner_text()}")
            assert bullet.inner_text() in _expected_bullet_items