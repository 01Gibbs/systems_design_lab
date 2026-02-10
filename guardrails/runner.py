"""Guardrails Runner - Main entry point for all enforcement checks"""
import sys
from pathlib import Path

from guardrails.architecture_checker import ArchitectureChecker
from guardrails.contract_checker import ContractChecker


def run_all_checks() -> int:
    """
    Run all guardrail checks.
    Returns 0 if all pass, 1 if any fail.
    """
    repo_root = Path(__file__).parent.parent
    backend_path = repo_root / "backend"

    print("=" * 60)
    print("Running Guardrails Checks")
    print("=" * 60)

    all_passed = True

    # 1. Architecture Boundaries
    print("\n[1/2] Checking architecture boundaries...")
    arch_checker = ArchitectureChecker(backend_path)
    arch_passed = arch_checker.check()
    arch_checker.print_violations()
    all_passed = all_passed and arch_passed

    # 2. Contract Drift
    print("\n[2/2] Checking contract drift...")
    contract_checker = ContractChecker(repo_root)
    contract_passed = contract_checker.check_drift()
    contract_checker.print_violations()
    all_passed = all_passed and contract_passed

    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All guardrails checks passed")
    else:
        print("✗ Some guardrails checks failed")
    print("=" * 60)

    return 0 if all_passed else 1


def main() -> int:
    """Main entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        repo_root = Path(__file__).parent.parent

        if command == "arch-check":
            backend_path = repo_root / "backend"
            checker = ArchitectureChecker(backend_path)
            passed = checker.check()
            checker.print_violations()
            return 0 if passed else 1

        elif command == "contracts-check":
            checker = ContractChecker(repo_root)
            passed = checker.check_drift()
            checker.print_violations()
            return 0 if passed else 1

        elif command == "contracts-accept":
            checker = ContractChecker(repo_root)
            success = checker.accept_changes()
            return 0 if success else 1

        else:
            print(f"Unknown command: {command}")
            print("Available commands: arch-check, contracts-check, contracts-accept")
            return 1

    # No command provided, run all checks
    return run_all_checks()


if __name__ == "__main__":
    sys.exit(main())
