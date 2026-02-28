from playwright.sync_api import expect


class LoginPage:


    def __init__(self, page):
        self.page = page
        self.username = page.get_by_role("textbox", name="email")
        self.password = page.get_by_label("Password")
        self.login_button = page.get_by_role("button", name="Login")
        self.success_message = page.get_by_role("alert")

    @classmethod
    def open(cls, page, url:str = "https://blisscoders.pythonanywhere.com/login") -> 'LoginPage':
        page.goto(url)
        return cls(page)

    def login(self, _username:str, _password:str):
        self.username.fill(_username)
        self.password.fill(_password)
        self.login_button.click()
        expect(self.success_message).to_have_text('Successful login!')

