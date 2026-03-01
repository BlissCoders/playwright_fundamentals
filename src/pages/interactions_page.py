from playwright.sync_api import Locator, Page


class InteractionsPage:

    def __init__(self, page : Page):
        self.page = page

# Locators
    def btn_drag_me(self) -> Locator:
        return self.page.locator(id="draggable")

    def sec_drop_here(self) -> Locator:
        return self.page.locator(id="droppable")

    def nav_menu(self, text) -> Locator:
        return self.page.locator(f'//a[@href and text()="{text}"]')

    def nav_menu_items(self) -> Locator:
        return self.page.locator(f'//nav[@class="navbar"]/a[@href]')


# Commands
    @classmethod
    def open(cls,page,url:str="https://blisscoders.pythonanywhere.com/")->'HomePage':
        page.goto(url)
        return cls(page)

    def navigate_to(self, nav_text):
        print(f"Navigating to {nav_text} ")

        self.nav_menu_items().filter(has_text=nav_text).click()



    def drag_and_drop(self):
        print(f"Dragging element with selector 'btn_drag_me' to element with selector 'sec_drop_here'")
        self.btn_drag_me().drag_to(self.sec_drop_here())


# Assertions