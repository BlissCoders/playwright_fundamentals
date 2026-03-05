from datetime import datetime
from time import sleep

import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page, expect

from src.pages.interactions_page import InteractionsPage


class TestInteraction:
    load_dotenv()

    inter_page = None

    @pytest.fixture(autouse=True)
    def before_each_test(self, playwright_page: Page):
        self.page = playwright_page
        self.inter_page = InteractionsPage.open(self.page)
        self.inter_page.navigate_to("Interactions")
        yield

        print("Test complete, performing cleanup...")

    @pytest.mark.interactions
    @pytest.mark.TC1
    def test_sortable_interactions(self):
        self.inter_page.verify_text_visible("Sortable")

    @pytest.mark.interactions
    @pytest.mark.TC2
    def test_resizeable_interactions(self):
        self.inter_page.verify_text_visible("Sortable")

    @pytest.mark.interactions
    @pytest.mark.TC3
    def test_droppable_interactions(self):
        self.inter_page.verify_text_visible("Sortable")
        self.inter_page.drag_and_drop()

    @pytest.mark.interactions
    @pytest.mark.TC8
    def test_accordion_elements_interactions(self):
        print("Testing Accordion elements interactions...")

        self.inter_page.verify_text_visible("Accordion")

        self.inter_page.verify_element_visible(self.inter_page.lbl_text("Accordion"))

        print(f"Verify Default Element visible for Accordion")

        for txt in ["Section 1", "Section 2", "Content 1"]:
            self.inter_page.verify_element_visible(self.inter_page.lbl_text(txt))

        self.inter_page.verify_element_not_visible(self.inter_page.lbl_text("Content 2"))

        self.inter_page.click_element(self.inter_page.lbl_text("Section 2"))

        self.inter_page.verify_element_attribute(
            self.inter_page.lbl_text("Section 1"),
            attr_name="aria-expanded",
            expected_attr_value="false"
        )
        self.inter_page.verify_element_not_visible(self.inter_page.lbl_text("Content 1"))

    @pytest.mark.interactions
    @pytest.mark.TC9
    @pytest.mark.parametrize("element_test, autocomplete_value", [
        pytest.param("Autocomplete", "Playwright", id="1"),
        pytest.param("Autocomplete", "Cypress", id="2"),
        pytest.param("Autocomplete", "Python", id="3")
    ])
    def test_auto_complete_elements_interactions(self, element_test, autocomplete_value):
        print("Testing Autocomplete elements interactions...")

        self.inter_page.verify_text_visible(element_test)

        self.inter_page.verify_element_visible(self.inter_page.lbl_text(element_test))

        # since the element is not "select" we cannot use the selection_option, so simuilate ko nalang
        self.inter_page.enter_text(self.inter_page.txt_autocomplete(), "P")
        self.inter_page.click_element_by_text(autocomplete_value, ".ui-autocomplete li")
        self.inter_page.verify_element_value(self.inter_page.txt_autocomplete(), autocomplete_value)

        sleep(3)

        self.inter_page.verify_element_attribute(
            self.inter_page.txt_autocomplete(),
            attr_name="autocomplete",
            expected_attr_value="off"
        )

    @pytest.mark.interactions
    @pytest.mark.TC10
    def test_date_picker_elements_interactions(self):
        print("Testing Date picker elements interactions...")

        self.inter_page.verify_text_visible("Datepicker")

        self.inter_page.verify_element_visible(self.inter_page.lbl_text("Datepicker"))

        date_today = datetime.now().strftime("%m/%d/%Y")
        self.inter_page.enter_text(self.inter_page.txt_date_picker(), date_today)
        sleep(3)

    @pytest.mark.interactions
    @pytest.mark.TC11
    @pytest.mark.parametrize("element_test, progress_bar_value", [
        pytest.param("Progressbar", "60", id="1")])
    def test_progress_bar_elements_interactions(self, element_test, progress_bar_value):
        print("Testing Progress bar elements interactions...")

        self.inter_page.verify_text_visible(element_test)

        self.inter_page.verify_element_visible(self.inter_page.lbl_text(element_test))

        self.inter_page.verify_element_attribute(
            self.inter_page.get_locator_by(locator_type="role", locator_value="progressbar"),
            attr_name="aria-valuenow",
            expected_attr_value=progress_bar_value)

    @pytest.mark.interactions
    @pytest.mark.TC12
    def test_tabs_elements_interactions(self):
        print("Testing Tabs elements interactions...")

        self.inter_page.verify_text_visible("Tabs")

        self.inter_page.verify_element_visible(self.inter_page.lbl_text("Tabs"))
        self.inter_page.verify_element_visible(self.inter_page.tab_selected("1"))
        self.inter_page.verify_element_visible(self.inter_page.lbl_text("Tab 1 content"))
        self.inter_page.verify_element_not_visible(self.inter_page.lbl_text("Tab 2 content"))

        self.inter_page.click_element(self.inter_page.tab_selected("2"))

        self.inter_page.verify_element_attribute(
            self.inter_page.tab_selected("1"),
            attr_name="aria-expanded",
            expected_attr_value="false"
        )
        self.inter_page.verify_element_not_visible(self.inter_page.lbl_text("Tab 1 content"))
        sleep(1.5)
        self.inter_page.verify_element_visible(self.inter_page.tab_selected("1"))

    @pytest.mark.interactions
    @pytest.mark.TC13
    def test_tooltips_elements_interactions(self):
        print("Testing Tooltips elements interactions...")

        self.inter_page.verify_text_visible("Tooltips")
        self.inter_page.get_locator_by(locator_type="text", locator_value="Hover over me").hover(force=True)
        sleep(1.5)
        tooltip = self.inter_page.get_locator_by(
            locator_type="text",
            locator_value="Tooltip text here",
            parent_selector=".ui-tooltip-content"
        )
        self.inter_page.verify_element_visible(tooltip)

    @pytest.mark.interactions
    @pytest.mark.TC14
    def test_menu_elements_interactions(self):
        print("Testing Menu elements interactions...")

        self.inter_page.verify_text_visible("Menu", is_exact_text=True)

        for index, menu_item in enumerate(["Dashboard", "Users", "Settings", ], start=1):
            attr_value = f"ui-id-{index}"

            self.inter_page.click_element_by_text(menu_item, parent_selector=f"#{attr_value}")

            self.inter_page.verify_element_attribute(
                self.inter_page.menu_menu(),
                attr_name="aria-activedescendant",
                expected_attr_value=attr_value
            )

    @pytest.mark.interactions
    @pytest.mark.TC15
    def test_select_menu_elements_interactions(self):
        print("Testing Select Menu elements interactions...")

        self.inter_page.verify_text_visible("Select Menu", is_exact_text=True)

        for select_menu_item in ["Playwright", "QA", "Automation"]:
            print(f" Select Menu Item to be selected : {select_menu_item}")
            # since the element is not "select" we cannot use the selection_option, so simuilate ko nalang
            self.inter_page.cmb_select_menu().click()
            self.inter_page.cmb_item_select_menu().filter(has_text=select_menu_item).click()
            expect(self.inter_page.cmb_item_select_menu_value()).to_have_text(select_menu_item)
            sleep(1.2)

    @pytest.mark.interactions
    @pytest.mark.TC16
    def test_shadow_dom_demo_elements_interactions(self):
        print("Testing Shadow DOM Demo elements interactions...")
        self.inter_page.verify_text_visible("Shadow DOM Demo")

        self.inter_page.click_element_by_text("Click Me", parent_selector="#shadow-host")

        result_text = self.inter_page.get_locator_by(
            "text",
            "Button clicked inside Shadow DOM!",
            "#shadow-host")

        self.inter_page.verify_element_visible(result_text)

    @pytest.mark.interactions
    @pytest.mark.TC17
    def test_upload_file_elements_interactions(self):
        print("Testing Upload File elements interactions...")

        self.inter_page.verify_text_visible("File Upload Demo")

        self.inter_page.upload_file(self.inter_page.txt_upload(), "test_upload_file", "jpg")
        self.inter_page.click_element(self.inter_page.btn_upload())
        self.page.wait_for_load_state()
        self.inter_page.verify_text_visible("Method Not Allowed")
