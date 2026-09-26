from rabtech_diag import system_info


def test_get_python_version_format():
    version = system_info.get_python_version()
    parts = version.split(".")
    assert len(parts) >= 2
    assert all(p.isdigit() for p in parts[:2])


def test_get_disk_space_positive():
    info = system_info.get_disk_space(".")
    assert info["total_gb"] > 0
    assert info["free_gb"] >= 0
    assert 0 <= info["percent_used"] <= 100


def test_check_dev_tools_missing_tool_reported():
    statuses = system_info.check_dev_tools(["definitely_not_a_real_tool_xyz"])
    assert len(statuses) == 1
    assert statuses[0].found is False
    assert statuses[0].version is None


def test_check_dev_tools_python3_or_pip_found():
    statuses = system_info.check_dev_tools(["python3", "pip"])
    assert any(s.found for s in statuses)


def test_gather_system_info_has_all_sections():
    info = system_info.gather_system_info()
    assert set(info.keys()) == {"python_version", "platform", "disk_space", "env_vars", "dev_tools"}
