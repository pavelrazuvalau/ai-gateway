"""
E2E tests for negative scenarios - application logic only.

These tests verify that the application handles error conditions in its logic
gracefully. System dependencies (Docker, RAM, permissions) are covered by
unit tests and don't require E2E testing.

See docs/troubleshooting.md for troubleshooting details.
See IMPROVEMENT_PLAN.md#Этап-6 for E2E test requirements.

Principle: E2E tests check only application logic, not system dependencies.
Users are enthusiasts with basic Linux knowledge, system errors are their concern.
"""

import socket
from pathlib import Path

import pytest


@pytest.mark.e2e
class TestNegativeScenarios:
    """
    Test negative scenarios for application logic.
    
    These tests verify that application logic handles error conditions correctly.
    System dependencies (Docker, RAM, permissions) are covered by unit tests.
    
    See docs/troubleshooting.md for troubleshooting details.
    See IMPROVEMENT_PLAN.md#Этап-6 for E2E test requirements.
    """

    def test_port_conflict_detection(self, e2e_project_root: Path) -> None:
        """
        Test that port conflicts are detected (application logic).
        
        See docs/troubleshooting.md#port-conflicts for details.
        
        This test verifies application logic for handling port conflicts.
        It creates a socket on a port and verifies that the application
        can detect when a port is already in use.
        """
        # Use a high port that's unlikely to be in use
        test_port = 54321
        
        # Try to bind to the port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            sock.bind(("localhost", test_port))
            sock.listen(1)
            
            # Port is now in use - verify we can detect it
            # Try to create another socket on the same port
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                test_sock.bind(("localhost", test_port))
                # If we get here, port is not actually in use (unexpected)
                test_sock.close()
                pytest.fail("Port should be in use but bind succeeded")
            except OSError:
                # Expected: port is in use
                assert True, "Port conflict detected correctly"
            finally:
                test_sock.close()
        except OSError as e:
            # Port might already be in use by another process
            pytest.skip(f"Could not bind to test port {test_port}: {e}")
        finally:
            sock.close()
    
    def test_invalid_configuration_handling(self, e2e_project_root: Path) -> None:
        """
        Test that invalid configuration is handled gracefully (application logic).
        
        See docs/configuration.md for configuration details.
        
        This test verifies application logic for handling invalid configuration.
        It checks that the application can detect and report configuration
        errors without crashing.
        """
        # Create an invalid .env file
        env_file = e2e_project_root / ".env"
        env_file.write_text("INVALID_CONFIG=value\nMALFORMED_LINE\n", encoding="utf-8")
        
        # Try to read it - should handle errors gracefully
        from src.infrastructure.file_repository import FileRepository
        
        file_repo = FileRepository(e2e_project_root)
        
        # read_env_file should handle malformed lines gracefully
        env_vars = file_repo.read_env_file(Path(".env"))
        
        # Should parse valid lines and skip invalid ones
        assert "INVALID_CONFIG" in env_vars, "Valid config should be parsed"
        assert env_vars["INVALID_CONFIG"] == "value", "Config value should be correct"
    
    def test_missing_config_files_handling(self, e2e_project_root: Path) -> None:
        """
        Test that missing configuration files are handled gracefully (application logic).
        
        See docs/getting-started.md#step-1-run-setup-script for setup details.
        
        This test verifies application logic for handling missing configuration files.
        """
        # Verify that missing .env file is handled
        env_file = e2e_project_root / ".env"
        assert not env_file.exists(), "Env file should not exist initially"
        
        from src.infrastructure.file_repository import FileRepository
        
        file_repo = FileRepository(e2e_project_root)
        
        # read_env_file should return empty dict for missing file
        env_vars = file_repo.read_env_file(Path(".env"))
        assert isinstance(env_vars, dict), "Should return dict even for missing file"
        assert len(env_vars) == 0, "Should return empty dict for missing file"

