import re
from time import sleep

from playwright.sync_api import Locator, Page, expect


class InteractionsPage:

    def __init__(self, page: Page):
        self.page = page

    # Locators
    def btn_drag_me(self) -> Locator:
        return self.page.locator("#draggable")

    def sec_drop_here(self) -> Locator:
        return self.page.locator("#droppable")

    def nav_menu(self, text) -> Locator:
        return self.page.locator(f'//a[@href and text()="{text}"]')

    def nav_menu_items(self) -> Locator:
        return self.page.locator(f'//nav[@class="navbar"]/a[@href]')

    def lbl_text(self, text) -> Locator:
        return self.page.get_by_text(text)

    def txt_autocomplete(self):
        return self.page.locator("//input[@id='autocomplete']")

    def txt_date_picker(self):
        return self.page.locator("//input[@id='datepicker' and @class='hasDatepicker']")

    def tab_selected(self, tabNum: str) -> Locator:
        return self.page.locator(f'//li[@role="tab" and @aria-controls="tabs-{tabNum}"]')

    def get_locator_by(self: Page, locator_type: str, value: str) -> Locator:
        """
        Returns a locator based on the type specified.
        Types: 'alt_text', 'label', 'placeholder', 'role', 'test_id', 'text', 'title'
        """
        if locator_type == "alt_text":
            return self.page.get_by_alt_text(value)
        elif locator_type == "label":
            return self.page.get_by_label(value)
        elif locator_type == "placeholder":
            return self.page.get_by_placeholder(value)
        elif locator_type == "role":
            return self.page.get_by_role(value)
        elif locator_type == "test_id":
            return self.page.get_by_test_id(value)
        elif locator_type == "text":
            return self.page.get_by_text(value)
        elif locator_type == "title":
            return self.page.get_by_title(value)
        else:
            return self.locator(value)

    # Commands

    @classmethod
    def open(cls, page, url: str = "https://blisscoders.pythonanywhere.com/") -> 'InteractionsPage':
        page.goto(url)
        return cls(page)

    def navigate_to(self, nav_text):
        print(f"Navigating to {nav_text} ")
        self.nav_menu_items().filter(has_text=nav_text).click()

    def drag_and_drop(self):
        print(f"Dragging element with selector 'btn_drag_me' to element with selector 'sec_drop_here'")
        self.btn_drag_me().drag_to(self.sec_drop_here())

    def focus_element(self, locator: Locator):
        print(f"Focus Element {locator}")
        self.verify_element_visible(locator)
        locator.focus()
        expect(locator).to_be_focused()

    def click_element(self, locator: Locator):
        print(f"Click Element {locator}")
        self.verify_element_visible(locator)
        locator.scroll_into_view_if_needed()
        locator.click()

    def enter_text(self, locator: Locator, value: str):
        print(f"Enter Text {locator}")
        self.focus_element(locator)
        locator.fill(value)
        expect(locator).to_have_value(re.compile(r".+"))
        self.page.keyboard.press("Enter", delay=2500)

    # Assertions

    def verify_text_visible(self, text):
        print(f"Verifying text visible: '{text}'")
        locator = self.lbl_text(text)
        expect(locator).to_be_visible()
        assert locator.is_visible()

    def verify_element_visible(self, locator: Locator):
        print(f"Verifying element visible: '{locator}'")
        expect(locator).to_be_visible()
        assert locator.is_visible()

    def verify_element_not_visible(self, locator: Locator):
        print(f"Verifying element not visible: '{locator}'")
        expect(locator).not_to_be_visible()
        assert locator.is_hidden()

    def verify_element_attribute(self, locator: Locator, attr_name: str, expected_attr_value: str):
        print(f"Verifying element attribute: '{attr_name}' ({expected_attr_value})")
        get_value = locator.get_attribute(attr_name)
        print(f"Getting attribute: '{attr_name}' ({expected_attr_value})")
        assert expected_attr_value in get_value
