============================= test session starts =============================
platform win32 -- Python 3.11.0, pytest-9.0.2, pluggy-1.6.0 -- C:\Users\Cheney\Documents\Github\ElevenDops\.venv\Scripts\python.exe
cachedir: .pytest_cache
hypothesis profile 'default' -> deadline=None, max_examples=50
rootdir: C:\Users\Cheney\Documents\Github\ElevenDops
configfile: pyproject.toml
plugins: anyio-4.12.0, hypothesis-6.148.8, langsmith-0.5.1, asyncio-1.3.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 6 items

tests/test_agent_service_logic.py::TestAgentUpdateLogic::test_update_agent_name_only PASSED [ 16%]
tests/test_agent_service_logic.py::TestAgentUpdateLogic::test_update_knowledge_base PASSED [ 33%]
tests/test_agent_service_logic.py::TestAgentUpdateLogic::test_update_languages_to_multilingual PASSED [ 50%]
tests/test_agent_api_update.py::test_update_agent_valid_request PASSED   [ 66%]
tests/test_agent_api_update.py::test_update_agent_not_found PASSED       [ 83%]
tests/test_agent_api_update.py::test_update_agent_validation_error PASSED [100%]

============================== 6 passed in 3.66s ==============================
