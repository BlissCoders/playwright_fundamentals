from time import sleep

from playwright.sync_api import Locator, expect


class InfiniteScrollPage:

    def __init__(self, page):
        self.page = page
        self.header_text = "Infinite Scroll Demo"

        self.header = "//div[@class='container']//h2"
        self.infinite_list = page.get_by_test_id("infinite-container")

    @classmethod
    def open(cls, page, url: str = "https://blisscoders.pythonanywhere.com/infinite-scroll") -> 'InfiniteScrollPage':
        page.goto(url)
        return cls(page)

    def get_header(self) -> Locator:
        return self.page.locator(self.header)

    def get_current_items_locator(self) -> Locator:
        return self.page.locator("//div[starts-with(text(), 'Item ')]")

    def get_all_current_items(self):
        return self.get_current_items_locator().all_text_contents()

    def verify_header_text(self, header_text:str=None):
        expected_header = header_text if header_text is not None else self.header_text
        print(f"\nHeader:{expected_header}")
        expect(self.get_header()).to_have_text(expected_header)

    def scroll_list(self, scroll_times: int = 50):
        for _ in range(scroll_times):
            self.infinite_list.hover()
            self.page.mouse.wheel(0,400)
            sleep(0.2)
            # self.infinite_list.evaluate("el => el.scrollBy(0, 100)")
            # sleep(0.2)

        all_items = self.get_all_current_items()
        print(f"\nTotal items loaded: {all_items[-1]}")





