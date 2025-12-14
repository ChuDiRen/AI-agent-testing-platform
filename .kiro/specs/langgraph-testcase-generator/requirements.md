# Requirements Document

## Introduction

本功能将基于LangGraph的多智能体协作架构集成到测试平台中，实现智能化的测试用例生成。系统通过需求分析专家、测试点设计专家、用例编写专家和用例评审专家四个智能体协作，自动将需求文档转换为高质量的测试用例。

## Glossary

- **LangGraph**: LangChain生态中的图状态机框架，用于构建多智能体协作系统
- **TestCaseGenerator**: 测试用例生成器，协调多个智能体完成用例生成
- **Supervisor**: 监督者智能体，负责协调各专家智能体的执行顺序
- **Analyzer**: 需求分析专家，负责深度解析需求文档
- **TestPointDesigner**: 测试点设计专家，负责设计测试覆盖点
- **Writer**: 用例编写专家，负责生成详细测试用例
- **Reviewer**: 用例评审专家，负责多维度质量评审
- **SSE**: Server-Sent Events，服务端推送事件，用于流式输出
- **TestCaseState**: 测试用例状态对象，在智能体间传递的上下文数据

## Requirements

### Requirement 1

**User Story:** As a test engineer, I want to generate test cases from requirement documents using AI multi-agent collaboration, so that I can quickly create comprehensive test coverage.

#### Acceptance Criteria

1. WHEN a user submits a requirement document THEN the TestCaseGenerator SHALL invoke the Analyzer agent to extract test elements within 30 seconds
2. WHEN the Analyzer completes analysis THEN the TestCaseGenerator SHALL invoke the TestPointDesigner to design test points covering normal, abnormal, and boundary scenarios
3. WHEN test points are designed THEN the Writer agent SHALL generate structured test cases in JSON format
4. WHEN test cases are generated THEN the Reviewer agent SHALL evaluate quality using a 0-100 scoring system
5. IF the quality score is below 80 THEN the TestCaseGenerator SHALL trigger re-generation up to 3 iterations

### Requirement 2

**User Story:** As a user, I want to see real-time progress of test case generation, so that I can understand the current processing stage.

#### Acceptance Criteria

1. WHEN generation starts THEN the system SHALL stream progress events via SSE to the frontend
2. WHILE the Analyzer is processing THEN the system SHALL emit "analyzing" status events with partial results
3. WHILE the Writer is generating THEN the system SHALL emit "writing" status events with incremental test case content
4. WHEN each agent completes THEN the system SHALL emit a completion event with the agent name and duration
5. WHEN generation completes THEN the system SHALL emit a "done" event with total test case count and quality score

### Requirement 3

**User Story:** As a user, I want to configure AI models for different agents, so that I can optimize cost and quality.

#### Acceptance Criteria

1. WHEN configuring the generator THEN the system SHALL allow separate model selection for Analyzer, Writer, and Reviewer agents
2. WHEN a model is selected THEN the system SHALL validate API connectivity before saving
3. WHILE generating THEN the system SHALL use the configured model for each respective agent
4. WHEN no model is configured THEN the system SHALL use the default enabled model

### Requirement 4

**User Story:** As a user, I want to view and manage generated test cases, so that I can review, edit, and export them.

#### Acceptance Criteria

1. WHEN test cases are generated THEN the system SHALL automatically save them to the database with conversation association
2. WHEN viewing generated cases THEN the system SHALL display them in a structured card format with priority, steps, and expected results
3. WHEN a user edits a test case THEN the system SHALL persist changes and update the modification timestamp
4. WHEN exporting test cases THEN the system SHALL support YAML and Excel formats

### Requirement 5

**User Story:** As a user, I want to generate test cases from Swagger/OpenAPI documents, so that I can quickly create API test coverage.

#### Acceptance Criteria

1. WHEN a user provides a Swagger URL THEN the system SHALL parse all API endpoints and their parameters
2. WHEN parsing completes THEN the system SHALL display a list of APIs for user selection
3. WHEN APIs are selected THEN the system SHALL batch generate test cases with configurable concurrency
4. WHEN batch generation completes THEN the system SHALL provide a summary report with success and failure counts

### Requirement 6

**User Story:** As a user, I want the frontend to display a ChatGPT-style conversation interface for test case generation, so that I can interact naturally with the AI.

#### Acceptance Criteria

1. WHEN the page loads THEN the system SHALL display a conversation list sidebar and main chat area
2. WHEN a user sends a message THEN the system SHALL display it as a user bubble and stream AI response in real-time
3. WHEN test cases are detected in the response THEN the system SHALL render them as interactive cards below the message
4. WHEN a user clicks a test case card THEN the system SHALL expand it to show full details with edit and save options
5. WHEN generation is in progress THEN the system SHALL display a progress indicator showing current agent and stage

### Requirement 7

**User Story:** As a system administrator, I want to monitor AI generation statistics, so that I can track usage and optimize costs.

#### Acceptance Criteria

1. WHEN a generation completes THEN the system SHALL record token usage, duration, and model used
2. WHEN viewing statistics THEN the system SHALL display daily/weekly/monthly generation counts and token consumption
3. WHEN a generation fails THEN the system SHALL log the error with full context for debugging

### Requirement 8

**User Story:** As a developer, I want the LangGraph integration to be modular, so that I can extend or replace agents independently.

#### Acceptance Criteria

1. WHEN adding a new agent THEN the system SHALL allow registration without modifying existing agent code
2. WHEN the Supervisor routes tasks THEN the system SHALL use a configurable graph definition
3. WHEN an agent fails THEN the system SHALL provide error recovery without affecting other agents

### Requirement 9

**User Story:** As a user, I want the generation process to be fast and efficient, so that I can get test cases without long waiting times.

#### Acceptance Criteria

1. WHEN generating test cases THEN the system SHALL complete single requirement analysis within 15 seconds
2. WHEN multiple agents can work independently THEN the system SHALL execute them in parallel to reduce total time
3. WHEN context is too long THEN the system SHALL apply intelligent compression to reduce token usage by 30-50%
4. WHEN generating batch test cases THEN the system SHALL support concurrent processing with configurable parallelism up to 10 requests
5. WHEN a generation step completes THEN the system SHALL cache intermediate results to avoid redundant LLM calls

### Requirement 10

**User Story:** As a user in China, I want to use domestic AI models, so that I can have faster response times and lower costs.

#### Acceptance Criteria

1. WHEN configuring AI models THEN the system SHALL support DeepSeek, Qwen (通义千问), Zhipu (智谱AI), Moonshot (Kimi), and SiliconFlow providers
2. WHEN adding a new model THEN the system SHALL allow custom API URL and model code configuration
3. WHEN selecting a provider THEN the system SHALL auto-fill the default API URL for that provider
4. WHEN testing model connectivity THEN the system SHALL validate the API key and endpoint within 5 seconds
5. WHEN a domestic model is selected THEN the system SHALL use the appropriate LangChain integration (ChatOpenAI with custom base_url)
