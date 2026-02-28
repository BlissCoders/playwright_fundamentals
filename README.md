# Playwright Python Automation Framework 🎭

A scalable end-to-end testing suite built with **Python**, **Playwright**, and **Pytest**, following industry best practices like the **Page Object Model (POM)**.

## 🛠️ Key Topics Covered

### 1. Environment Setup & Configuration
*   **Installation:** Setting up the [Playwright Python library](https://playwright.dev) and browser binaries (Chromium, Firefox, WebKit).
*   **Browser Management:** Configuring headless/headed modes and cross-browser execution.

### 2. Automated Browser Testing
*   **Test Scripting:** Writing scripts to simulate real user interactions.
*   **Execution:** Running individual tests or entire suites across multiple browsers.

### 3. Structured Test Execution with Pytest
*   **Fixtures:** Utilizing `pytest-playwright` fixtures (e.g., `page`, `browser`) for clean test setup.
*   **Parallelism:** Running tests in parallel to optimize execution time.
*   **Reporting:** Generating visual artifacts like screenshots, videos, and [Playwright Traces](https://playwright.dev).

### 4. Page Object Model (POM)
*   **Architecture:** Decoupling test logic from UI locators for high maintainability.
*   **Reusability:** Creating page-specific classes to minimize code duplication.

### 5. Advanced Web Interactions
*   **Locators & Selectors:** Using robust strategies (CSS, XPath, Text) to find elements.
*   **Auto-Waiting:** Leveraging Playwright's [intelligent waiting mechanisms](https://playwright.dev).
*   **Forms & Assertions:** Automating complex form inputs and verifying outcomes with web-first assertions.

### 6. GitHub Integration & Version Control
*   **Collaboration:** Using Git for branch management and pull requests.
*   **CI/CD Foundation:** Structuring the project for integration with [GitHub Actions](https://github.com/features/actions).

---

### 7. Documentation Links
*   [pytest](https://docs.pytest.org/en/stable/getting-started.html)
*   [pytest-html](https://pytest-html.readthedocs.io/en/latest/)

---

## 🚀 Getting Started

### Prerequisites
*   Python 3.8+
*   pip

### Installation
1. Install the [Playwright Pytest plugin](https://playwright.dev):
   ```bash
   pip install -r requirements.txt
   
### Execution
1. Run all tests in /tests directory:
   ```bash
   pytest tests

2. Run specific test in /tests directory:
   ```bash
   pytest tests/test_first_session.py
   
3. Run specific tests using marks e.g.('login_only') in /tests directory:
   ```bash
   pytest tests -m "login_only"
   
---
#### Github Branching Strategy
**Step 1: Feature to Develop**
* When your work in the feature-branch is done:
  1. Open a PR on GitHub.
  2. Set the base to develop and the compare to feature-branch.
  3. Once the tests (CI) pass and your team approves, merge it into develop.

**Step 2: Develop to Master**
* To move those changes to production (master):
  1. Open a new Pull Request on GitHub.
  2. Set the base to master and the compare to develop.
  3. This PR will show every feature that was added to develop since the last release.
  4. Once approved and the CI passes, merge it. master is now updated.


