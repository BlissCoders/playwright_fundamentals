from code import interact

import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page

from src.pages.interactions_page import InteractionsPage


class Interaction:
    load_dotenv()


    @pytest.mark.interactions
    def test_sortable_interactions(self, playwright_page):
        interactions_page = InteractionsPage.open(page=playwright_page)
        interactions_page.drag_and_drop()


    @pytest.mark.interactions
    def test_resizeable_interactions(self, playwright_page):
        interactions_page = InteractionsPage.open(page=playwright_page)
        interactions_page.drag_and_drop()


    @pytest.mark.interactions
    def test_droppable_interactions(self, playwright_page : Page):
        interactions_page = InteractionsPage.open(page=playwright_page)

        interactions_page.navigate_to("Interactions")
        interactions_page.drag_and_drop()
