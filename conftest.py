import os.path
import shutil
from datetime import datetime

import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture
def playwright_page(request):
    test_name = request.node.name
    root_dir = request.config.rootpath

    video_path = os.path.join(root_dir, "tests-results", "videos",str(test_name))
    screenshot_path = os.path.join(root_dir,"tests-results","screenshots", str(test_name))

    #Create directories
    os.makedirs(video_path, exist_ok=True)
    os.makedirs(screenshot_path, exist_ok=True)

    # Boolean flag for easier reading
    save_recorded_video = os.environ.get("RECORD_VIDEO", "false").lower() == "true"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Always enable recording if the ENV is true so Playwright captures the session
        context = browser.new_context(
            record_video_dir=video_path if save_recorded_video else None

        )
        # Setting default wait timeout overriding default 30 seconds
        context.set_default_timeout(5000)
        page = context.new_page()

        try:
            yield page
        finally:
            # Check if the test actually failed (requires the hook pytest_run_makereport)
            # We check 'rep_call' specifically for test body failures
            result_outcome = getattr(request.node, "rep_call", None)
            test_failed = result_outcome and result_outcome.failed

            # If test passed, no screenshot and delete folder not required (empty)
            if not test_failed:
                shutil.rmtree(screenshot_path)

            # If test failed, take screenshot
            if test_failed:
                now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                page.screenshot(path=f"{screenshot_path}/{test_name}_{now}.png")

            # VERY IMPORTANT: close context to finalize video
            context.close()

            # If test passed OR recording was disabled, delete the video folder
            if not test_failed or not save_recorded_video:
                if os.path.exists(video_path):
                    shutil.rmtree(video_path)

            # Now it's safe to close browser
            browser.close()

def pytest_configure(config):
    # This overrides the .ini setting with a timestamped filename
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Create report directory
    root_dir = config.rootpath
    report_path = os.path.join(root_dir, "tests-results","reports")
    os.makedirs(report_path, exist_ok=True)

    config.option.htmlpath = f"{report_path}/report_{now}.html"
    config.option.self_contained_html = True

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # Execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # Set a report attribute for each phase of a call (setup, call, teardown)
    # This allows the fixture to check if the test failed
    setattr(item, "rep_" + rep.when, rep)