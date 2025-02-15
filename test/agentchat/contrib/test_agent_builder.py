# Copyright (c) 2023 - 2024, Owners of https://github.com/ag2ai
#
# SPDX-License-Identifier: Apache-2.0
#
# Portions derived from  https://github.com/microsoft/autogen are under the MIT License.
# SPDX-License-Identifier: MIT
#!/usr/bin/env python3 -m pytest

import json
import os

import pytest

from autogen.agentchat.contrib.agent_builder import AgentBuilder

from ...conftest import reason, skip_openai  # noqa: E402
from ..test_assistant_agent import KEY_LOC, OAI_CONFIG_LIST  # noqa: E402

try:
    import chromadb
    import huggingface_hub
except ImportError:
    skip = True
else:
    skip = False

here = os.path.abspath(os.path.dirname(__file__))


def _config_check(config):
    # check config loading
    assert config.get("coding", None) is not None
    assert config.get("default_llm_config", None) is not None
    assert config.get("code_execution_config", None) is not None

    for agent_config in config["agent_configs"]:
        assert agent_config.get("name", None) is not None
        assert agent_config.get("model", None) is not None
        assert agent_config.get("description", None) is not None
        assert agent_config.get("system_message", None) is not None


@pytest.mark.skipif(
    skip_openai,
    reason=reason,
)
def test_build():
    builder = AgentBuilder(
        config_file_or_env=OAI_CONFIG_LIST,
        config_file_location=KEY_LOC,
        builder_model_tags=["gpt-4o"],
        agent_model_tags=["gpt-4o"],
    )
    building_task = (
        "Find a paper on arxiv by programming, and analyze its application in some domain. "
        "For example, find a recent paper about gpt-4 on arxiv "
        "and find its potential applications in software."
    )
    agent_list, agent_config = builder.build(
        building_task=building_task,
        default_llm_config={"temperature": 0},
        code_execution_config={
            "last_n_messages": 2,
            "work_dir": f"{here}/test_agent_scripts",
            "timeout": 60,
            "use_docker": "python:3",
        },
    )
    _config_check(agent_config)

    # check number of agents
    assert len(agent_config["agent_configs"]) <= builder.max_agents


@pytest.mark.skipif(
    skip_openai or skip,
    reason=reason + "OR dependency not installed",
)
def test_build_from_library():
    builder = AgentBuilder(
        config_file_or_env=OAI_CONFIG_LIST,
        config_file_location=KEY_LOC,
        builder_model_tags=["gpt-4o"],
        agent_model_tags=["gpt-4o"],
    )
    building_task = (
        "Find a paper on arxiv by programming, and analyze its application in some domain. "
        "For example, find a recent paper about gpt-4 on arxiv "
        "and find its potential applications in software."
    )
    agent_list, agent_config = builder.build_from_library(
        building_task=building_task,
        library_path_or_json=f"{here}/example_agent_builder_library.json",
        default_llm_config={"temperature": 0},
        code_execution_config={
            "last_n_messages": 2,
            "work_dir": f"{here}/test_agent_scripts",
            "timeout": 60,
            "use_docker": "python:3",
        },
    )
    _config_check(agent_config)

    # check number of agents
    assert len(agent_config["agent_configs"]) <= builder.max_agents

    builder.clear_all_agents()

    # test embedding similarity selection
    agent_list, agent_config = builder.build_from_library(
        building_task=building_task,
        library_path_or_json=f"{here}/example_agent_builder_library.json",
        default_llm_config={"temperature": 0},
        embedding_model="all-mpnet-base-v2",
        code_execution_config={
            "last_n_messages": 2,
            "work_dir": f"{here}/test_agent_scripts",
            "timeout": 60,
            "use_docker": "python:3",
        },
    )
    _config_check(agent_config)

    # check number of agents
    assert len(agent_config["agent_configs"]) <= builder.max_agents


@pytest.mark.skipif(
    skip_openai,
    reason=reason,
)
def test_save():
    builder = AgentBuilder(
        config_file_or_env=OAI_CONFIG_LIST,
        config_file_location=KEY_LOC,
        builder_model_tags=["gpt-4o"],
        agent_model_tags=["gpt-4o"],
    )
    building_task = (
        "Find a paper on arxiv by programming, and analyze its application in some domain. "
        "For example, find a recent paper about gpt-4 on arxiv "
        "and find its potential applications in software."
    )

    builder.build(
        building_task=building_task,
        default_llm_config={"temperature": 0},
        code_execution_config={
            "last_n_messages": 2,
            "work_dir": f"{here}/test_agent_scripts",
            "timeout": 60,
            "use_docker": "python:3",
        },
    )
    saved_files = builder.save(f"{here}/example_save_agent_builder_config.json")

    # check config file path
    assert os.path.isfile(saved_files)

    saved_configs = json.load(open(saved_files))

    _config_check(saved_configs)


@pytest.mark.skipif(
    skip_openai,
    reason=reason,
)
def test_load():
    builder = AgentBuilder(
        config_file_or_env=OAI_CONFIG_LIST,
        config_file_location=KEY_LOC,
        # builder_model=["gpt-4", "gpt-4-1106-preview"],
        # agent_model=["gpt-4", "gpt-4-1106-preview"],
        builder_model_tags=["gpt-4o"],
        agent_model_tags=["gpt-4o"],
    )

    config_save_path = f"{here}/example_test_agent_builder_config.json"
    json.load(open(config_save_path))

    agent_list, loaded_agent_configs = builder.load(
        config_save_path,
        code_execution_config={
            "last_n_messages": 2,
            "work_dir": f"{here}/test_agent_scripts",
            "timeout": 60,
            "use_docker": "python:3",
        },
    )
    print(loaded_agent_configs)

    _config_check(loaded_agent_configs)


@pytest.mark.skipif(
    skip_openai,
    reason=reason,
)
def test_clear_agent():
    builder = AgentBuilder(
        config_file_or_env=OAI_CONFIG_LIST,
        config_file_location=KEY_LOC,
        builder_model_tags=["gpt-4o"],
        agent_model_tags=["gpt-4o"],
    )

    config_save_path = f"{here}/example_test_agent_builder_config.json"
    builder.load(
        config_save_path,
        code_execution_config={
            "last_n_messages": 2,
            "work_dir": f"{here}/test_agent_scripts",
            "timeout": 60,
            "use_docker": "python:3",
        },
    )
    builder.clear_all_agents()

    # check if the agent cleared
    assert len(builder.agent_procs_assign) == 0


if __name__ == "__main__":
    test_build()
    test_build_from_library()
    test_save()
    test_load()
    test_clear_agent()
