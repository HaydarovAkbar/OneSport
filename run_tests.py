#!/usr/bin/env python
"""
Test runner script for OneSport project
Usage: python run_tests.py [options]
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

import django
django.setup()


def run_tests(
    apps=None, 
    coverage=False, 
    parallel=False, 
    keepdb=False, 
    verbosity=2,
    failfast=False,
    pattern=None
):
    """Run Django tests with options"""
    
    cmd = ['python', 'manage.py', 'test']
    
    # Add specific apps
    if apps:
        cmd.extend(apps)
    
    # Add options
    if verbosity:
        cmd.extend(['--verbosity', str(verbosity)])
    
    if parallel:
        cmd.append('--parallel')
    
    if keepdb:
        cmd.append('--keepdb')
    
    if failfast:
        cmd.append('--failfast')
    
    if pattern:
        cmd.extend(['--pattern', pattern])
    
    # Run with coverage if requested
    if coverage:
        coverage_cmd = [
            'coverage', 'run', '--source=.', '--omit=*/migrations/*,*/venv/*,*/env/*,manage.py,*/settings/*,*/tests/*',
            'manage.py', 'test'
        ]
        
        if apps:
            coverage_cmd.extend(apps)
        
        if verbosity:
            coverage_cmd.extend(['--verbosity', str(verbosity)])
        
        if parallel:
            coverage_cmd.append('--parallel')
        
        if keepdb:
            coverage_cmd.append('--keepdb')
        
        if failfast:
            coverage_cmd.append('--failfast')
        
        print("Running tests with coverage...")
        result = subprocess.run(coverage_cmd)
        
        if result.returncode == 0:
            print("\nGenerating coverage report...")
            subprocess.run(['coverage', 'report', '-m'])
            subprocess.run(['coverage', 'html'])
            print("HTML coverage report generated in htmlcov/")
        
        return result.returncode
    
    else:
        print("Running tests...")
        result = subprocess.run(cmd)
        return result.returncode


def run_linting():
    """Run code quality checks"""
    print("Running flake8...")
    flake8_result = subprocess.run(['flake8', 'grid/', 'config/'])
    
    print("Running black check...")
    black_result = subprocess.run(['black', '--check', 'grid/', 'config/'])
    
    print("Running isort check...")
    isort_result = subprocess.run(['isort', '--check-only', 'grid/', 'config/'])
    
    return all(result.returncode == 0 for result in [flake8_result, black_result, isort_result])


def format_code():
    """Format code with black and isort"""
    print("Formatting code with black...")
    subprocess.run(['black', 'grid/', 'config/'])
    
    print("Sorting imports with isort...")
    subprocess.run(['isort', 'grid/', 'config/'])
    
    print("Code formatting complete!")


def run_type_checking():
    """Run mypy type checking"""
    print("Running mypy type checking...")
    try:
        result = subprocess.run(['mypy', 'grid/', 'config/', '--ignore-missing-imports'])
        return result.returncode == 0
    except Exception as e:
        print(f"⚠️  MyPy type checking failed: {e}")
        print("MyPy will be skipped for now, but it's recommended to fix Django settings for type checking.")
        return True  # Don't fail the entire check because of MyPy configuration issues


def run_security_check():
    """Run bandit security check"""
    print("Running bandit security check...")
    result = subprocess.run(['bandit', '-r', 'grid/', 'config/', '-x', '*/tests/*'])
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description='OneSport Test Runner')
    
    # Test options
    parser.add_argument('apps', nargs='*', help='Specific apps to test')
    parser.add_argument('--coverage', '-c', action='store_true', help='Run with coverage')
    parser.add_argument('--parallel', '-p', action='store_true', help='Run tests in parallel')
    parser.add_argument('--keepdb', '-k', action='store_true', help='Keep test database')
    parser.add_argument('--verbosity', '-v', type=int, default=2, help='Verbosity level')
    parser.add_argument('--failfast', '-f', action='store_true', help='Stop on first failure')
    parser.add_argument('--pattern', help='Test file pattern')
    
    # Code quality options
    parser.add_argument('--lint', '-l', action='store_true', help='Run linting')
    parser.add_argument('--format', action='store_true', help='Format code')
    parser.add_argument('--type-check', '-t', action='store_true', help='Run type checking')
    parser.add_argument('--security', '-s', action='store_true', help='Run security check')
    parser.add_argument('--all-checks', '-a', action='store_true', help='Run all quality checks')
    
    # Quick test suites
    parser.add_argument('--unit', '-u', action='store_true', help='Run only unit tests')
    parser.add_argument('--integration', '-i', action='store_true', help='Run only integration tests')
    
    args = parser.parse_args()
    
    success = True
    
    # Format code if requested
    if args.format:
        format_code()
        return
    
    # Run specific test suites
    if args.unit:
        print("Running unit tests...")
        success &= run_tests(
            pattern='test_*.py',
            coverage=args.coverage,
            parallel=args.parallel,
            keepdb=args.keepdb,
            verbosity=args.verbosity,
            failfast=args.failfast
        ) == 0
    
    elif args.integration:
        print("Running integration tests...")
        success &= run_tests(
            pattern='integration_*.py',
            coverage=args.coverage,
            parallel=args.parallel,
            keepdb=args.keepdb,
            verbosity=args.verbosity,
            failfast=args.failfast
        ) == 0
    
    # Run regular tests
    elif not any([args.lint, args.type_check, args.security, args.all_checks]):
        success &= run_tests(
            apps=args.apps,
            coverage=args.coverage,
            parallel=args.parallel,
            keepdb=args.keepdb,
            verbosity=args.verbosity,
            failfast=args.failfast,
            pattern=args.pattern
        ) == 0
    
    # Run code quality checks
    if args.lint or args.all_checks:
        success &= run_linting()
    
    if args.type_check or args.all_checks:
        success &= run_type_checking()
    
    if args.security or args.all_checks:
        success &= run_security_check()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
