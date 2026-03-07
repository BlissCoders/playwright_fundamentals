import re
from pathlib import Path
from time import sleep

from playwright.sync_api import Locator, Page, expect


class InteractionsPage:

    def __init__(self, page: Page):
        self.page = page

    # Locators
    def nav_menu(self, text) -> Locator:
        return self.page.locator(f'//a[@href and text()="{text}"]')

    def nav_menu_items(self) -> Locator:
        return self.page.locator(f'//nav[@class="navbar"]/a[@href]')

    def lbl_text(self, text, is_exact_value: bool = None) -> Locator:
        return self.page.get_by_text(text, exact=is_exact_value)

    def txt_autocomplete(self):
        return self.page.locator("//input[@id='autocomplete']")

    def txt_date_picker(self):
        return self.page.locator("//input[@id='datepicker' and @class='hasDatepicker']")

    def tab_selected(self, tab_num: str) -> Locator:
        return self.page.locator(f'//li[@role="tab" and @aria-controls="tabs-{tab_num}"]')

    def menu_menu(self) -> Locator:
        return self.page.locator("ul#menu")

    def cmb_select_menu(self, ) -> Locator:
        return self.page.locator("#selectmenu-button")

    def cmb_item_select_menu(self, ) -> Locator:
        return self.page.locator("#selectmenu-menu .ui-menu-item-wrapper")

    def cmb_item_select_menu_value(self, ) -> Locator:
        return self.page.locator(".ui-selectmenu-text")

    def txt_upload(self) -> Locator:
        return self.page.get_by_test_id("file-input")

    def btn_upload(self) -> Locator:
        return self.page.locator("//button[@data-testid='btn-upload']")

    def get_locator_by(self, locator_type: str, locator_value: str, parent_selector: str = None) -> Locator:
        scope = self.page.locator(parent_selector) if parent_selector else self.page

        locators = {
            "alt_text": scope.get_by_alt_text,
            "label": scope.get_by_label,
            "placeholder": scope.get_by_placeholder,
            "role": scope.get_by_role,
            "test_id": scope.get_by_test_id,
            "text": scope.get_by_text,
            "title": scope.get_by_title,
            "xpath": scope.locator,
            "css": scope.locator,
        }

        locator_func = locators.get(locator_type, scope.locator)
        return locator_func(locator_value)

    def sortable_heading(self):
        return self.page.get_by_role("heading", name="Sortable")

    def sortable_items(self):
        return self.page.locator("#sortable > li.ui-sortable-handle")

    def resizable_box(self) -> Locator:
        return self.page.locator("#resizable")

    def resizable_handle_se(self) -> Locator:
        return self.page.locator("#resizable .ui-resizable-se")

    def selectable_items(self):
        return self.page.locator("#selectable > li.ui-selectee")

    def btn_drag_me(self) -> Locator:
        return self.page.locator("#draggable")

    def sec_drop_here(self) -> Locator:
        return self.page.locator("#droppable")

    # Commands

    @classmethod
    def open(cls, page, url: str = "https://blisscoders.pythonanywhere.com/") -> 'InteractionsPage':
        page.goto(url)
        return cls(page)

    def navigate_to(self, nav_text):
        print(f"Navigating to {nav_text} ")
        self.nav_menu_items().filter(has_text=nav_text).click()

    def drag_and_drop_sortable(self, source_index: int, target_index: int):
        items = self.sortable_items()
        source = items.nth(source_index)
        target = items.nth(target_index)
        source_box = source.bounding_box()
        target_box = target.bounding_box()
        self.page.mouse.move(source_box["x"] + source_box["width"] / 2,
                             source_box["y"] + source_box["height"] / 2)
        self.page.mouse.down()
        self.page.mouse.move(target_box["x"] + target_box["width"] / 2,
                             target_box["y"] + target_box["height"] / 2,
                             steps=10)
        self.page.mouse.up()

    def drag_and_drop(self):
        print("Dragging 'Drag me' into 'Drop here'")
        self.btn_drag_me().drag_to(self.sec_drop_here())

    def select_all_items(self):
        items = self.selectable_items()
        count = items.count()
        for i in range(count):
            item = items.nth(i)
            item.scroll_into_view_if_needed()
            item.click()
            print(f"Selected item: {item.text_content()}")

    def resize_box(self, x_offset: int = 100, y_offset: int = 100):
        handle = self.resizable_handle_se()
        handle.scroll_into_view_if_needed()

        box_before = self.resizable_box().bounding_box()

        # drag diagonally
        handle.hover()
        self.page.mouse.down()
        self.page.mouse.move(
            box_before["x"] + box_before["width"] + x_offset,
            box_before["y"] + box_before["height"] + y_offset,
            steps=15
        )
        self.page.mouse.up()

        box_after = self.resizable_box().bounding_box()
        print(f"Resized box: before={box_before}, after={box_after}")
        return box_after["width"], box_after["height"]

    def focus_element(self, locator: Locator):
        print(f"Focus Element {locator}")
        self.verify_element_visible(locator)
        locator.focus()
        expect(locator).to_be_focused()
        return locator

    def click_element(self, locator: Locator):
        print(f"Click Element {locator}")
        self.verify_element_visible(locator)
        locator.scroll_into_view_if_needed()
        locator.click()
        return locator

    def click_element_by_text(self, text_to_click: str, parent_selector: str = None):
        print(f"Click Element {text_to_click} with selector '{parent_selector}'")
        locator = self.get_locator_by("text", text_to_click, parent_selector)
        self.verify_element_visible(locator)
        locator.click()

    def enter_text(self, locator: Locator, value: str):
        print(f"Enter Text {locator}")
        self.focus_element(locator)
        locator.fill("")
        locator.fill(value)
        self.verify_element_value(locator, value)
        self.page.keyboard.press("Enter", delay=1500)
        return locator

    def press_key_element(self, locator: Locator, key_press: str):
        print(f"Press Key {key_press} in {locator} ")
        self.focus_element(locator)
        locator.press(key_press, delay=1500)
        return locator

    # Assertions

    def verify_text_visible(self, text, is_exact_text: bool = None):
        print(f"Verifying text visible: '{text}'")
        locator = self.lbl_text(text, is_exact_text)
        locator.scroll_into_view_if_needed()
        expect(locator).to_be_visible()
        assert locator.is_visible()

    def verify_element_visible(self, locator: Locator):
        print(f"Verifying element visible: '{locator}'")
        locator.scroll_into_view_if_needed()
        expect(locator).to_be_visible()
        assert locator.is_visible()

    def verify_element_not_visible(self, locator: Locator):
        print(f"Verifying element not visible: '{locator}'")
        expect(locator).not_to_be_visible()
        assert locator.is_hidden()

    def verify_element_attribute(self, locator: Locator, attr_name: str, expected_attr_value: str):
        print(f"Verifying element attribute: '{attr_name}' ({expected_attr_value})")
        get_value = locator.get_attribute(attr_name)
        print(f"Getting attribute: Attribute Name :'{attr_name}' | Attribute Value :' {expected_attr_value}'")
        assert expected_attr_value in get_value

    def verify_element_value(self, locator: Locator, expected_value: str):
        ex_value = re.compile(rf".*{re.escape(expected_value)}.*", re.IGNORECASE)
        el_value = locator.input_value()

        print(f"Verifying element : Expected Value: '{ex_value}' | Actual Value : '{el_value}'")

        expect(locator).to_have_value(ex_value)

    def upload_file(self, locator: Locator, file_name: str, file_type: str):
        print(f"Uploading file '{locator}' to file '{file_name}'")
        current_dir = Path(__file__).parent

        file_path = current_dir.parent.parent / "test_data" / f"{file_name}.{file_type}"

        locator.set_input_files(file_path)
        self.verify_element_value(locator, file_name)
        sleep(1.5)
