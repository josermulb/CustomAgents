import inspect
import importlib
import docstring_parser
from typing import Any


class ToolsManager:
    """
    Manages and registers functions as tools for Large Language Models (LLMs).

    This class loads functions from a specified module, parses their signatures
    and docstrings, and converts them into a schema compatible with LLM tool-calling
    mechanisms (e.g., OpenAI function calling format). It also provides a method
    to execute these registered functions.
    """

    def __init__(self, module_name: str):
        """
        Initializes the ToolsManager by loading functions from a specified module.

        Args:
            module_name (str): The full dotted name of the module from which to load functions
                                (e.g., 'my_module.tools').
        """
        self._functions = {}
        self.tools = []
        self._load_functions_from_module(module_name)

    def _load_functions_from_module(self, module_name: str):
        """
        Loads all public functions from the given module and registers them as tools.

        Private functions (those starting with '_') are ignored.

        Args:
            module_name (str): The name of the module to inspect for functions.
        """
        mod = importlib.import_module(module_name)

        for name, obj in inspect.getmembers(mod, inspect.isfunction):
            if name.startswith("_"):
                continue  # Ignore private functions
            self.register_function(obj)

    def register_function(self, func, description: str = None):
        """
        Registers a Python function and builds its LLM-compatible schema.

        This method inspects the function's signature and docstring to extract
        parameter names, types, descriptions, and whether they are required.
        The function is then stored internally and its schema is added to `self.tools`.

        Args:
            func (Callable): The Python function to register.
            description (str, optional): An explicit description for the tool. If not provided,
                                         the short description from the function's docstring is used.
                                         Defaults to None.
        """
        sig = inspect.signature(func)
        doc = docstring_parser.parse(func.__doc__ or "")
        param_docs = {p.arg_name: p.description for p in doc.params}

        properties = {}
        required = []

        for name, param in sig.parameters.items():
            param_type = self._map_type(param.annotation)
            param_description = param_docs.get(name, f'Argument {name}')
            properties[name] = {
                'type': param_type,
                'description': param_description
            }
            if param.default is param.empty:
                required.append(name)

        func_name = func.__name__
        self._functions[func_name] = func
        setattr(self, func_name, func) # Allows direct access like `tools_manager.my_function()`

        tool_dict = {
            'type': 'function',
            'function': {
                'name': func_name,
                'description': description or doc.short_description or "No description provided.",
                'parameters': {
                    'type': 'object',
                    'properties': properties,
                    'required': required,
                    'additionalProperties': False, # Ensures only defined properties are allowed
                },
                'strict': True # Indicates strict parameter validation
            }
        }
        self.tools.append(tool_dict)

    def _map_type(self, annotation: Any) -> str:
        """
        Maps Python type annotations to corresponding JSON Schema types.

        Args:
            annotation (Any): The Python type annotation (e.g., str, int, float, bool).

        Returns:
            str: The corresponding JSON Schema type string (e.g., 'string', 'integer', 'number', 'boolean').
                 Defaults to 'string' if no specific mapping is found.
        """
        if annotation == str:
            return 'string'
        elif annotation == int:
            return 'integer'
        elif annotation == float:
            return 'number'
        elif annotation == bool:
            return 'boolean'
        else:
            return 'string' # Default for unhandled types

    def call_function(self, func_name: str, args: dict) -> Any:
        """
        Executes a registered function with the given arguments.

        Includes a specific security check to disable the 'run_cmd' function.

        Args:
            func_name (str): The name of the function to call.
            args (dict): A dictionary of arguments to pass to the function.

        Returns:
            Any: The result of the function call.

        Raises:
            ValueError: If the function name is not registered (implicitly handled by the return string).
        """
        if func_name == 'run_cmd':
            return "run_cmd function is disabled for security reasons."
        if func_name not in self._functions:
            return f"Tool '{func_name}' is not an existing capability."
        return self._functions[func_name](**args)