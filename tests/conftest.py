import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic._internal._config")
warnings.filterwarnings("ignore", message="open_text is deprecated", category=DeprecationWarning)
