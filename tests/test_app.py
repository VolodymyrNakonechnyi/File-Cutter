from file_configurator.app import main


def test_app_entry_point_imports_without_starting_event_loop() -> None:
    assert callable(main)
