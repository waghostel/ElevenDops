============================= test session starts =============================
platform win32 -- Python 3.11.0, pytest-7.4.3, pluggy-1.5.0
rootdir: C:\Users\Cheney\Documents\Github\ElevenDops
configfile: pyproject.toml
plugins: anyio-4.6.2.post1, hypothesis-6.148.8, asyncio-0.21.1, cov-4.1.0, docker-3.1.1, mock-3.12.0
asyncio: mode=Mode.AUTO
collected 0 items / 1 error

=================================== ERRORS ====================================
_______________ ERROR collecting tests/test_debug_api_props.py ________________
ImportError while importing test module 'C:\Users\Cheney\Documents\Github\ElevenDops\tests\test_debug_api_props.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
..\..\..\AppData\Local\Programs\Python\Python311\Lib\importlib\__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests\test_debug_api_props.py:21: in <module>
    from backend.main import app
backend\main.py:11: in <module>
    from backend.api.routes.audio import router as audio_router
backend\api\routes\audio.py:21: in <module>
    from backend.services.audio_service import AudioService, get_audio_service
backend\services\audio_service.py:13: in <module>
    from backend.services.script_generation_service import ScriptGenerationService
backend\services\script_generation_service.py:4: in <module>
    from backend.services.langgraph_workflow import create_script_generation_graph, generate_script_stream as workflow_generate_script_stream
backend\services\langgraph_workflow.py:2: in <module>
    from langgraph.graph import StateGraph, END
E   ModuleNotFoundError: No module named 'langgraph'
============================== warnings summary ===============================
..\..\..\AppData\Local\Programs\Python\Python311\Lib\site-packages\starlette\formparsers.py:12
  C:\Users\Cheney\AppData\Local\Programs\Python\Python311\Lib\site-packages\starlette\formparsers.py:12: PendingDeprecationWarning: Please use `import python_multipart` instead.
    import multipart

..\..\..\AppData\Local\Programs\Python\Python311\Lib\site-packages\pydantic\_internal\_fields.py:132
  C:\Users\Cheney\AppData\Local\Programs\Python\Python311\Lib\site-packages\pydantic\_internal\_fields.py:132: UserWarning: Field "model_name" in ScriptGenerateRequest has conflict with protected namespace "model_".
  
  You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
    warnings.warn(

..\..\..\AppData\Local\Programs\Python\Python311\Lib\site-packages\pydantic\_internal\_fields.py:132
  C:\Users\Cheney\AppData\Local\Programs\Python\Python311\Lib\site-packages\pydantic\_internal\_fields.py:132: UserWarning: Field "model_used" in ScriptGenerateResponse has conflict with protected namespace "model_".
  
  You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
ERROR tests/test_debug_api_props.py
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
======================== 3 warnings, 1 error in 5.76s =========================
