import pytest
from src.pages.infinite_scroll_page import InfiniteScrollPage

class TestInfiniteScroll:

    @pytest.mark.scroll
    def test_scroll_scenarios(self, playwright_page):
        """
        Test Case : Validate Infinite Scroll and get the Last Scrolled Item

        Steps:
        1. Navigate to https://blisscoders.pythonanywhere.com/infinite-scroll
        2. Should have header text "Infinite Scroll Demo"
        3. Should be able to scroll depending on how many times needed scroll_list() default is 50
        4. Should output the last item in the list
        """

        infinite_scroll_page = InfiniteScrollPage.open(playwright_page)
        infinite_scroll_page.verify_header_text()
        infinite_scroll_page.verify_scroll_list_expected_value()
