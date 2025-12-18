## ADDED Requirements

### Requirement: Mobile engine executes keyword-driven test cases
The system SHALL provide a `mobile-engine` executor that can run keyword-driven test cases against real mobile apps.

#### Scenario: Execute a YAML case successfully
- **WHEN** a user provides a cases directory containing YAML case files and a `context.yaml`
- **AND WHEN** the engine is invoked with required Appium connection/capability parameters
- **THEN** the engine executes `pre_script`, `steps`, and `post_script` in order
- **AND THEN** the run is reported as successful when all steps complete without errors

### Requirement: Mobile engine uses Appium/WebDriver sessions
The system SHALL connect to an Appium server and manage a WebDriver session for the duration of a test case run.

#### Scenario: Create and tear down session
- **WHEN** execution starts and no session exists
- **THEN** the engine creates an Appium session using the provided capabilities
- **AND THEN** the session is stored in runtime context for keyword execution
- **WHEN** execution completes
- **THEN** the engine closes the session and releases resources

### Requirement: Variable rendering and scripting lifecycle
The system SHALL support Jinja2 variable rendering and optional `pre_script`/`post_script` execution compatible with `web-engine`.

#### Scenario: Render variables into steps
- **WHEN** a step contains templated values referencing global context and case-local context
- **THEN** the engine renders templates before executing the keyword

#### Scenario: Execute pre_script and post_script
- **WHEN** a case defines `pre_script` and/or `post_script`
- **THEN** the engine executes them with access to context variables and `g_context`

### Requirement: Core mobile interaction keywords
The system SHALL provide a minimal set of built-in mobile keywords required to interact with Android/iOS UIs.

#### Scenario: Tap and input text
- **WHEN** a case step requests to tap an element and input text
- **THEN** the engine locates the element using the specified strategy and performs the interaction

### Requirement: Failure artifacts
The system SHALL capture artifacts on failure to aid debugging.

#### Scenario: Screenshot on step failure
- **WHEN** a keyword execution raises an exception
- **THEN** the engine captures a screenshot and attaches it to the test report
