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

    def menu_list(self, menu_text: str) -> Locator:
        return self.page.locator(".ui-menu-item-wrapper").get_by_text(menu_text)

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

    def lbl_tooltip(self) -> Locator:
        return self.page.locator(".ui-tooltip-content").get_by_text("Tooltip text here")

    def btn_click_me(self) -> Locator:
        return self.page.locator("#shadow-host").get_by_text("Click Me")

    def lbl_shadow_dom_demo(self) -> Locator:
        return self.page.locator("#shadow-host").get_by_text("Button clicked inside Shadow DOM!")

    def lbl_auto_complete_list(self, text: str) -> Locator:
        return self.page.locator(".ui-autocomplete li").get_by_text(text)

    def lbl_hover_me(self) -> Locator:
        return self.page.get_by_text("Hover over me")

    def div_progress_bar(self) -> Locator:
        return self.page.get_by_role(role="progressbar")

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

    def validate_menu_option(self, list_text):
        for index, menu_item in enumerate(list_text, start=1):
            attr_value = f"ui-id-{index}"
            self.menu_list(menu_item).click()
            get_attr = self.menu_menu().get_attribute("aria-activedescendant")
            print(f"Actual Attribute Value for {menu_item} is {get_attr}")
            assert get_attr == attr_value

    def validate_select_menu(self, list_text):
        for select_menu_item in list_text:
            print(f" Select Menu Item to be selected : {select_menu_item}")
            # since the element is not "select" we cannot use the selection_option, so simuilate ko nalang
            self.cmb_select_menu().click()
            self.cmb_item_select_menu().filter(has_text=select_menu_item).click()
            expect(self.cmb_item_select_menu_value()).to_have_text(select_menu_item)
            sleep(1.2)

    def upload_file(self, locator: Locator, file_name: str, file_type: str):
        print(f"Uploading file '{locator}' to file '{file_name}'")
        current_dir = Path(__file__).parent

        file_path = current_dir.parent.parent / "test_data" / f"{file_name}.{file_type}"

        locator.set_input_files(file_path)
        expect(locator).to_have_value(re.compile(rf"{file_name}(\.[^.]+)?$"))
        sleep(1.5)
