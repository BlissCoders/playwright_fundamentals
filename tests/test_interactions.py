from code import interact

import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page

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
    def test_sortable_interactions(self, playwright_page):

        self.inter_page.verify_text_visible("Sortable")

    @pytest.mark.interactions
    @pytest.mark.TC2
    def test_resizeable_interactions(self, playwright_page):
        self.inter_page.verify_text_visible("Sortable")

    @pytest.mark.interactions
    @pytest.mark.TC3
    def test_droppable_interactions(self, playwright_page: Page):
        self.inter_page.navigate_to("Interactions")
        self.inter_page.verify_text_visible("Sortable")
        self.inter_page.drag_and_drop()
