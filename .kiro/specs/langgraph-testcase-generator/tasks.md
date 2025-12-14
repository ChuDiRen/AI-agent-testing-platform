# Implementation Plan

## Backend Implementation

- [x] 1. Set up LangGraph module structure

  - [x] 1.1 Create langgraph directory structure under aiassistant

    - Create `aiassistant/langgraph/` with `__init__.py`, `agents/`, `services/`, `prompts/` subdirectories
    - _Requirements: 8.1, 8.2_

  - [x] 1.2 Create state and base agent definitions
    - Implement `state.py` with TestCaseState dataclass
    - Implement `agents/base.py` with BaseAgent abstract class
    - _Requirements: 1.1, 1.2, 1.3, 1.4_
  - [x]\* 1.3 Write property test for TestCaseState

    - **Property 1: Generation Pipeline Completeness**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4**

- [x] 2. Implement ModelService for domestic AI models

  - [x] 2.1 Create ModelService with provider configurations

    - Implement `services/model_service.py` with PROVIDER_CONFIGS for DeepSeek, SiliconFlow, Qwen, Zhipu, Moonshot
    - Implement `create_chat_model()` method using ChatOpenAI with custom base_url
    - _Requirements: 10.1, 10.2, 10.3, 10.5_

  - [x]\* 2.2 Write property test for provider URL auto-fill

    - **Property 13: Provider URL Auto-fill**

    - **Validates: Requirements 10.3, 10.5**

  - [x] 2.3 Implement model connectivity test with timeout

    - Implement `test_connection()` method with 5-second timeout
    - _Requirements: 3.2, 10.4_

  - [x]\* 2.4 Write property test for model validation timeout

    - **Property 5: Model Validation Timeout**
    - **Validates: Requirements 3.2, 10.4**

- [x] 3. Implement expert agents

  - [x] 3.1 Implement AnalyzerAgent

    - Create `agents/analyzer.py` with requirement analysis logic

    - Add prompt template in `prompts/analyzer.txt`
    - _Requirements: 1.1_

  - [x] 3.2 Implement TestPointDesignerAgent

    - Create `agents/designer.py` with test point design logic
    - Add prompt template in `prompts/designer.txt`
    - _Requirements: 1.2_

  - [x] 3.3 Implement WriterAgent

    - Create `agents/writer.py` with test case generation logic

    - Add prompt template in `prompts/writer.txt`
    - Ensure JSON output format
    - _Requirements: 1.3_

  - [x]\* 3.4 Write property test for test case JSON structure
    - **Property 7: Test Case JSON Structure**
    - **Validates: Requirements 1.3, 4.4**
  - [x] 3.5 Implement ReviewerAgent

    - Create `agents/reviewer.py` with quality scoring logic (0-100)
    - Add prompt template in `prompts/reviewer.txt`

    - _Requirements: 1.4_

  - [x]\* 3.6 Write property test for iteration control
    - **Property 2: Iteration Control**
    - **Validates: Requirements 1.5**

- [x] 4. Implement Supervisor and Generator

  - [x] 4.1 Implement TestCaseSupervisor

    - Create `supervisor.py` with LangGraph state machine
    - Define agent routing logic and iteration control
    - _Requirements: 1.5, 8.2_

  - [x] 4.2 Implement TestCaseGenerator
    - Create `generator.py` with generate() and batch_generate() methods
    - Integrate ModelService for model selection
    - _Requirements: 3.1, 3.3, 3.4_
  - [x]\* 4.3 Write property test for model configuration isolation

    - **Property 4: Model Configuration Isolation**
    - **Validates: Requirements 3.1, 3.3, 3.4**

- [x] 5. Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement performance optimization services

  - [x] 6.1 Implement ContextCompressor
    - Create `services/context_compressor.py` with compress() method
    - Implement token estimation and intelligent summarization
    - _Requirements: 9.3_
  - [x]\* 6.2 Write property test for context compression effectiveness
    - **Property 12: Context Compression Effectiveness**
    - **Validates: Requirements 9.3**
  - [x] 6.3 Implement CacheService
    - Create `services/cache_service.py` with in-memory caching
    - Support cache key generation from requirement hash
    - _Requirements: 9.5_

- [x] 7. Implement LangGraphController API

  - [x] 7.1 Create LangGraphController with stream endpoint
    - Implement `/LangGraph/generate/stream` with SSE response
    - Emit stage_start, stage_progress, stage_complete, text_chunk, testcase, done events
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  - [x]\* 7.2 Write property test for SSE event sequence
    - **Property 3: SSE Event Sequence**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
  - [x] 7.3 Implement batch generation endpoint
    - Implement `/LangGraph/generate/batch` with concurrent processing
    - Support configurable max_concurrent parameter
    - _Requirements: 5.3, 9.4_
  - [x]\* 7.4 Write property test for batch generation concurrency
    - **Property 10: Batch Generation Concurrency**
    - **Validates: Requirements 5.3, 9.4**
  - [x] 7.5 Implement Swagger parsing endpoint
    - Implement `/LangGraph/swagger/parse` to extract API endpoints
    - _Requirements: 5.1_
  - [x]\* 7.6 Write property test for Swagger parsing completeness
    - **Property 9: Swagger Parsing Completeness**
    - **Validates: Requirements 5.1**

- [x] 8. Implement data persistence

  - [x] 8.1 Create GenerationHistory model

    - Add `model/GenerationHistory.py` with all required fields
    - _Requirements: 4.1, 7.1_

  - [x] 8.2 Implement history recording in generator
    - Save generation results with token usage, duration, model info
    - _Requirements: 4.1, 7.1_
  - [x]\* 8.3 Write property test for persistence after generation
    - **Property 6: Persistence After Generation**
    - **Validates: Requirements 4.1, 7.1**
  - [x] 8.4 Implement statistics endpoint
    - Implement `/LangGraph/statistics` for usage tracking
    - _Requirements: 7.2_

- [x] 9. Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Implement error handling and recovery

  - [x] 10.1 Implement error handling in agents
    - Add try-catch with retry logic in each agent
    - Implement error event emission for SSE
    - _Requirements: 7.3, 8.3_
  - [x]\* 10.2 Write property test for error isolation
    - **Property 11: Error Isolation**
    - **Validates: Requirements 7.3, 8.3**

- [x] 11. Implement export functionality

  - [x] 11.1 Implement YAML export
    - Add export_yaml() method in TestCaseController
    - _Requirements: 4.4_
  - [x]\* 11.2 Write property test for export format validity
    - **Property 8: Export Format Validity**
    - **Validates: Requirements 4.4**

- [x] 12. Register routes in app.py
  - Add LangGraphController router to FastAPI application
  - _Requirements: All backend requirements_

## Frontend Implementation

- [x] 13. Create enhanced AgentChat components

  - [x] 13.1 Create ProgressIndicator component

    - Display current agent stage with progress bar
    - Show stage icons and labels
    - _Requirements: 6.5_

  - [x] 13.2 Create TestCaseCard component

    - Display test case in card format with priority, steps, expected results
    - Support expand/collapse and edit mode
    - _Requirements: 6.3, 6.4_

  - [x] 13.3 Create ModelSelector component

    - Dropdown for selecting AI models per agent
    - Show provider icons and model names
    - _Requirements: 3.1_

- [x] 14. Implement AgentChatEnhanced page

  - [-] 14.1 Create AgentChatEnhanced.vue

    - Integrate conversation sidebar, message list, progress indicator
    - Handle SSE events and update UI in real-time
    - _Requirements: 6.1, 6.2, 6.3_

  - [x] 14.2 Implement useLangGraph composable
    - Create `composables/useLangGraph.js` for SSE connection and state management
    - Handle event parsing and test case extraction
    - _Requirements: 2.1, 6.2_

- [x] 15. Update router and menu

  - Add route for AgentChatEnhanced page
  - Update menu configuration if needed
  - _Requirements: 6.1_

- [x] 16. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
