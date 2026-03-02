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
        self.inter_page = InteractionsPage.open(page=playwright_page)
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
        pytest.param("Autocomplete", "Dheo Claveria Testing", id="1"),
        pytest.param("Autocomplete", "Bliss Coders Assignment", id="2")
    ])
    def test_auto_complete_elements_interactions(self, element_test, autocomplete_value):
        print("Testing Autocomplete elements interactions...")

        self.inter_page.verify_text_visible(element_test)

        self.inter_page.verify_element_visible(self.inter_page.lbl_text(element_test))

        self.inter_page.enter_text(self.inter_page.txt_autocomplete(), autocomplete_value)
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
            self.inter_page.get_locator_by(locator_type="role", value="progressbar"),
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
