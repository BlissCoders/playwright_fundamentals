import re
from datetime import datetime

import pytest
from playwright.sync_api import Page, expect

from src.pages.interactions_page import InteractionsPage


class TestInteraction:
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
        self.inter_page.sortable_heading().is_visible()
        before_items = self.inter_page.sortable_items().all_text_contents()
        print("Before sorting:", before_items)
        self.inter_page.drag_and_drop_sortable(0, 2)
        after_items = self.inter_page.sortable_items().all_text_contents()
        print("After sorting:", after_items)
        assert before_items != after_items

    @pytest.mark.interactions
    @pytest.mark.TC2
    def test_resizeable_interactions(self, playwright_page):
        before_size = self.inter_page.resizable_box().bounding_box()
        print("Before resize:", before_size)
        after_width, after_height = self.inter_page.resize_box(100, 100)
        print("After resize:", after_width, after_height)
        assert after_width > before_size["width"]
        assert after_height > before_size["height"]
        assert after_height > before_size["height"]

    @pytest.mark.interactions
    @pytest.mark.TC3
    def test_selectable_interactions(self, playwright_page: Page):
        expect(self.page.get_by_text("Selectable", exact=True)).to_be_visible()
        self.inter_page.select_all_items()
        last_item = self.inter_page.selectable_items().nth(3)
        expect(last_item).to_have_class(re.compile("ui-selected"))

    @pytest.mark.interactions
    @pytest.mark.TC4
    def test_droppable_interactions(self, playwright_page: Page):
        expect(self.page.get_by_text("Droppable")).to_be_visible()
        self.inter_page.drag_and_drop()
        drop_area = self.inter_page.sec_drop_here()
        expect(drop_area).to_have_text(re.compile("Dropped!"))

    @pytest.mark.interactions
    @pytest.mark.TC5
    def test_accordion_elements_interactions(self):
        print("Testing Accordion elements interactions...")

        expect(self.page.get_by_text("Accordion")).to_be_visible()

        print(f"Verify Default Element visible for Accordion")

        self.inter_page.lbl_text("Content 1").is_visible()
        self.inter_page.lbl_text("Content 2").is_hidden()
        self.inter_page.lbl_text("Section 2").click()

        get_attr = self.inter_page.lbl_text("Section 1").get_attribute("aria-expanded")
        assert get_attr == "false"
        self.inter_page.lbl_text("Content 2").is_hidden()

    @pytest.mark.interactions
    @pytest.mark.TC6
    @pytest.mark.parametrize("element_test, autocomplete_value", [
        pytest.param("Autocomplete", "Playwright", id="1"),
        pytest.param("Autocomplete", "Cypress", id="2"),
        pytest.param("Autocomplete", "Python", id="3")
    ])
    def test_auto_complete_elements_interactions(self, element_test, autocomplete_value):
        print("Testing Autocomplete elements interactions...")

        expect(self.page.get_by_text(element_test)).to_be_visible()

        # since the element is not "select" we cannot use the selection_option, so simuilate ko nalang
        self.inter_page.txt_autocomplete().fill("P")

        self.inter_page.lbl_auto_complete_list(autocomplete_value).click()

        expect(self.inter_page.txt_autocomplete()).to_have_value(autocomplete_value)

        get_attr = self.inter_page.txt_autocomplete().get_attribute("autocomplete")
        assert get_attr == "off"

    @pytest.mark.interactions
    @pytest.mark.TC7
    def test_date_picker_elements_interactions(self):
        print("Testing Date picker elements interactions...")

        expect(self.page.get_by_text("Datepicker")).to_be_visible()

        date_today = datetime.now().strftime("%m/%d/%Y")
        self.inter_page.txt_date_picker().fill(date_today)
        self.page.keyboard.press("Enter", delay=1500)

    @pytest.mark.interactions
    @pytest.mark.TC8
    @pytest.mark.parametrize("element_test, progress_bar_value", [
        pytest.param("Progressbar", "60", id="1")])
    def test_progress_bar_elements_interactions(self, element_test, progress_bar_value):
        print("Testing Progress bar elements interactions...")

        expect(self.page.get_by_text(element_test)).to_be_visible()

        get_attr = self.inter_page.div_progress_bar().get_attribute("aria-valuenow")

        assert get_attr == progress_bar_value, f"Failed  Actual Value{get_attr} | Expected Value : {progress_bar_value}"

    @pytest.mark.interactions
    @pytest.mark.TC9
    def test_tabs_elements_interactions(self):
        print("Testing Tabs elements interactions...")

        expect(self.page.get_by_text("Tabs")).to_be_visible()

        self.inter_page.tab_selected("1").is_visible()
        self.inter_page.lbl_text("Tab 1 content").is_visible()
        self.inter_page.lbl_text("Tab 2 content").is_hidden()
        self.inter_page.tab_selected("2").click()

        get_attr = self.inter_page.tab_selected("1").get_attribute("aria-expanded")
        assert get_attr == "false"
        self.inter_page.lbl_text("Tab 1 content").is_hidden()

    @pytest.mark.interactions
    @pytest.mark.TC10
    def test_tooltips_elements_interactions(self):
        print("Testing Tooltips elements interactions...")

        expect(self.page.get_by_text("Tooltips")).to_be_visible()
        self.inter_page.lbl_hover_me().hover(force=True)

        expect(self.inter_page.lbl_tooltip()).to_be_visible()

    @pytest.mark.interactions
    @pytest.mark.TC11
    def test_menu_elements_interactions(self):
        print("Testing Menu elements interactions...")

        self.inter_page.validate_menu_option(["Dashboard", "Users", "Settings"])

    @pytest.mark.interactions
    @pytest.mark.TC12
    def test_select_menu_elements_interactions(self):
        print("Testing Select Menu elements interactions...")

        self.inter_page.validate_select_menu(["Playwright", "QA", "Automation"])

    @pytest.mark.interactions
    @pytest.mark.TC13
    def test_shadow_dom_demo_elements_interactions(self):
        print("Testing Shadow DOM Demo elements interactions...")
        expect(self.page.get_by_text("Shadow DOM Demo")).to_be_visible()
        self.inter_page.btn_click_me().click()

        expect(self.inter_page.lbl_shadow_dom_demo()).to_be_visible()

    @pytest.mark.interactions
    @pytest.mark.TC14
    def test_upload_file_elements_interactions(self):
        print("Testing Upload File elements interactions...")

        expect(self.page.get_by_text("File Upload Demo")).to_be_visible()
        self.inter_page.upload_file(self.inter_page.txt_upload(), "test_upload_file", "jpg")
        self.inter_page.btn_upload().click()
        self.page.wait_for_load_state()
        expect(self.page.get_by_text("Method Not Allowed")).to_be_visible()
