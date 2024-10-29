"""Query CLI output of a device."""

from typing import Callable, Dict, Any

import pytest
from nornir.core.task import MultiResult, Result
from nornir_netmiko import netmiko_send_command

from nuts.helpers.result import (
    AbstractHostResultExtractor,
    NutsResult,
)
from nuts.context import NornirNutsContext

EXAMPLE = """
- test_class: TestNetmikoCLI
  test_module: example_custom_netmiko_cli_test.netmiko_cli
  test_execution:
    command_string: show call-home
    use_timing: False
  test_data:
    - host: switch01
      contains: "call home feature : disable"
      not_contains: "enable"
"""


class CLIExtractor(AbstractHostResultExtractor):
    def single_transform(self, single_result: MultiResult) -> Dict[str, Dict[str, Any]]:
        cli_result = self._simple_extract(single_result)
        return cli_result


class CLIContext(NornirNutsContext):
    def nuts_task(self) -> Callable[..., Result]:
        return netmiko_send_command

    def nuts_extractor(self) -> CLIExtractor:
        return CLIExtractor(self)


CONTEXT = CLIContext


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

    @pytest.mark.nuts("not_contains")
    def test_not_contains_in_result(
        self, nuts_ctx, single_result: NutsResult, not_contains: Any
    ) -> None:
        cmd = nuts_ctx.nuts_parameters.get("test_execution", {}).get(
            "command_string", None
        )
        result = single_result.result
        assert not_contains not in result, f"'{not_contains}' FOUND in '{cmd}' output"
