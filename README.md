# Example Custom NETMIKO CLI test

This repository demonstrates how to create a custom test for NUTS (Network Unit Testing System). After installing this Python package, you can run the following example test:

```yaml
- test_class: TestNetmikoCLI
  test_module: example_custom_netmiko_cli_test.netmiko_cli
  test_execution:
    command_string: show call-home
    use_timing: False  # Determines whether to use send_command_timing (True) or send_command (False) for command execution
    # test_execution parameters are passed to the send_command or send_command_timing function
    # See Netmiko documentation for details: https://ktbyers.github.io/netmiko/docs/netmiko/index.html#netmiko.BaseConnection.send_command
  test_data:
    - host: switch01
      contains: "call home feature : disable"
      not_contains: "enable"
```

## Setup Project

This project uses [UV](https://docs.astral.sh/uv/), a fast Python package manager, though you may also use (Poetry)[https://python-poetry.org/] or any other package manager.

To set up with `uv`, run:
```bash
uv init example-custom-netmiko-cli-test --lib --package -p python3.10
uv add --dev ruff
uv add --dev mypy
uv add nuts
```

## Test Implementation

The NUTS test class is implemented in `src/example_custom_netmiko_cli_test/netmiko_cli.py`. For detailed instructions on writing custom tests, see the [How To Write Your Own Test](https://nuts.readthedocs.io/en/latest/dev/writetests.html) documentation.

A NUTS test requires three classes:

1. **Context Class**: The `CLIContext` class provides all necessary information for test execution. `CLIContext` inherits from `NornirNutsContext`, which handles the Nornir task execution.

2. **Extractor Class:** The `CLIExtractor` class is responsible for extracting and transforming the task results. When using Nornir, all task results are returned as a `AggregatedResult` object. The extractor processes these results for each host, generating a `NutsResult` object for each, which is then passed to the test class.

3. **Test Class**: `TestNetmikoCLI` is the actual test class, where multiple test functions can be defined for different assertions.


### CLIContext

The CLIContext class overrides two methods:

- **nuts_task**: Defines the Nornir task to execute (in this case, `netmiko_send_command`). By default, all `test_execution` parameters are passed as arguments to the task. This behavior can be customized by overriding the `nuts_arguments` method.

    ```python
        def nuts_task(self) -> Callable[..., Result]:
            return netmiko_send_command
    ```

- **nuts_extractor**: Specifies the CLIExtractor object to use for processing results.

    ```python
        def nuts_extractor(self) -> CLIExtractor:
            return CLIExtractor(self)
    ```

To ensure the correct context class is used, set the variable CONTEXT in your file:

```python
CONTEXT = CLIContext
```

NUTS will automatically discover and use this context.


### CLIExtractor

The `CLIExtractor` prepares the data before passing it to the test class as a `NutsResult` object. By inheriting from `AbstractHostResultExtractor`, it maps the Nornir `AggregatedResult` to each host. The `single_transform` method, called for each host, transforms the `MultiResult` into a `NutsResult`. The `_simple_extract(single_result)` method extracts the first result from the `MultiResult` — standard behavior when there are no Nornir subtasks.

```python
class CLIExtractor(AbstractHostResultExtractor):
    def single_transform(self, single_result: MultiResult) -> Dict[str, Dict[str, Any]]:
        cli_result = self._simple_extract(single_result)
        return cli_result
```

### TestNetmikoCLI

The [custom pytest marker](https://docs.pytest.org/en/stable/example/markers.html) is used to pass specific data from the `test_data` section in the YAML test definition as a pytest fixture. In this example, the `contains` value is passed to the test function, allowing it to validate whether this value appears in the command output. For instance, based on the example YAML, the string `"call home feature : disable"` is passed for `switch01`, and the test checks if it is part of the result.

The test context is accessible via the `nuts_ctx` fixture, which allows additional functionality, such as enhancing error messages if assertions fail. In this example, the code retrieves the command string (`command_string`) for better error reporting. If a value specified in pytest nuts marker is not defined in the test_data section, the test is automatically skipped.

```python
class TestNetmikoCLI:
    @pytest.mark.nuts("contains")
    def test_contains_in_result(
        self, nuts_ctx, single_result: NutsResult, contains: Any
    ) -> None:
        cmd = nuts_ctx.nuts_parameters.get("test_execution", {}).get(
            "command_string", None
        )
        result = single_result.result
        assert contains in result, f"'{contains}' NOT found in '{cmd}' output"
```

You can also pass multiple values to a test function, as shown in this example from the [documentation](https://nuts.readthedocs.io/en/latest/dev/writetests.html#writing-the-test-itself):

```python
@pytest.mark.nuts("name, role")
def test_role(self, single_result: NutsResult, name: str, role: str) -> None:
    assert single_result.result[name]["role"] == role
```
