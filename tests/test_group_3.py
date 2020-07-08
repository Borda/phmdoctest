"""Third group of pytest test cases for phmdoctest."""
import click

import phmdoctest
import phmdoctest.cases
import phmdoctest.main
import phmdoctest.simulator
import verify


def test_missing_setup_for_setup_doctest():
    """Caller specifies --setup-doctest, but no --setup."""
    command = (
        'phmdoctest doc/setup_doctest.md --setup-doctest --report'
    )
    simulator_status = phmdoctest.simulator.run_and_pytest(
        well_formed_command=command,
        pytest_options=None
    )
    assert simulator_status.runner_status.exit_code == 0
    stdout = simulator_status.runner_status.stdout
    # no blocks set to role setup
    assert not ('  setup' in stdout)
    want2 = 'No setup block found, not honoring --setup-doctest.'
    assert want2 in stdout


def test_no_match_for_setup():
    """Caller specifies --setup TEXT, but no block matches TEXT."""
    command = (
        'phmdoctest doc/setup_doctest.md --setup NOTMATCHED --report'
    )
    simulator_status = phmdoctest.simulator.run_and_pytest(
        well_formed_command=command,
        pytest_options=None
    )
    assert simulator_status.runner_status.exit_code == 0
    stdout = simulator_status.runner_status.stdout
    # no blocks set to role setup
    assert not ('  setup' in stdout)
    assert 'No setup block found.' in stdout


def test_too_many_matches_for_setup():
    """Caller specifies --setup TEXT, but no block matches TEXT."""
    command = (
        'phmdoctest doc/setup_doctest.md --setup print --report'
    )
    simulator_status = phmdoctest.simulator.run_and_pytest(
        well_formed_command=command,
        pytest_options=None
    )
    assert simulator_status.runner_status.exit_code == 1
    stdout = simulator_status.runner_status.stdout
    assert 'Error: More than one block matched command line' in stdout
    assert '--setup print (or -uprint).' in stdout
    assert 'Only one match is allowed.' in stdout
    assert 'The matching blocks are at line numbers 18, 35, 45' in stdout


def test_setup_is_not_code_block():
    """Caller --setup matches, but it is not a code block."""
    command = (
        'phmdoctest doc/setup_doctest.md --setup="mylist.append(55)" --report'
    )
    simulator_status = phmdoctest.simulator.run_and_pytest(
        well_formed_command=command,
        pytest_options=None
    )
    assert simulator_status.runner_status.exit_code == 0
    stdout = simulator_status.runner_status.stdout
    assert not ('  setup' in stdout)
    assert 'No setup block found.' in stdout


def test_setup_is_not_skipped_block():
    """Caller --setup matches, but the block is skipped."""
    command = (
        'phmdoctest doc/setup_doctest.md --skip FIRST --setup FIRST` --report'
    )
    simulator_status = phmdoctest.simulator.run_and_pytest(
        well_formed_command=command,
        pytest_options=None
    )
    assert simulator_status.runner_status.exit_code == 0
    stdout = simulator_status.runner_status.stdout
    assert not ('  setup' in stdout)
    assert 'No setup block found.' in stdout


def test_no_match_for_teardown():
    """Caller specifies --teardown TEXT, but no block matches TEXT."""
    command = (
        'phmdoctest doc/setup_doctest.md --teardown NOTMATCHED --report'
    )
    simulator_status = phmdoctest.simulator.run_and_pytest(
        well_formed_command=command,
        pytest_options=None
    )
    assert simulator_status.runner_status.exit_code == 0
    stdout = simulator_status.runner_status.stdout
    # no blocks set to role setup
    assert not ('  teardown' in stdout)
    want2 = 'No teardown block found.'
    assert want2 in stdout


def test_too_many_matches_for_teardown():
    """Caller specifies --teardown TEXT, but no block matches TEXT."""
    command = (
        'phmdoctest doc/setup_doctest.md --teardown round --report'
    )
    simulator_status = phmdoctest.simulator.run_and_pytest(
        well_formed_command=command,
        pytest_options=None
    )
    assert simulator_status.runner_status.exit_code == 1
    stdout = simulator_status.runner_status.stdout
    assert 'Error: More than one block matched command line' in stdout
    assert '--teardown round (or -dround).' in stdout
    assert 'Only one match is allowed.' in stdout
    assert 'The matching blocks are at line numbers 18, 74' in stdout


def test_teardown_is_not_code_block():
    """Caller --teardown matches, but it is not a code block."""
    command = (
        'phmdoctest doc/setup_doctest.md --teardown True --report'
    )
    simulator_status = phmdoctest.simulator.run_and_pytest(
        well_formed_command=command,
        pytest_options=None
    )
    assert simulator_status.runner_status.exit_code == 0
    stdout = simulator_status.runner_status.stdout
    assert not ('  teardown' in stdout)
    assert 'No teardown block found.' in stdout


def test_run_setup_example():
    """Verify the setup example passes pytest."""
    command = (
        'phmdoctest doc/setup.md --setup FIRST --teardown LAST'
        ' --report --outfile discarded.py'
    )
    simulator_status = phmdoctest.simulator.run_and_pytest(
        well_formed_command=command,
        pytest_options=['--strict', '-v']
    )
    assert simulator_status.runner_status.exit_code == 0
    assert simulator_status.pytest_exit_code == 0
    stdout = simulator_status.runner_status.stdout
    assert 'py3         9  setup     "FIRST"' in stdout
    assert 'py3        56  teardown  "LAST"' in stdout


def test_run_setup_doctest_example():
    """Verify the --setup-doctest example passes pytest."""
    command = (
        'phmdoctest doc/setup_doctest.md --setup FIRST --teardown LAST'
        ' --setup-doctest --report --outfile discarded.py'
    )
    simulator_status = phmdoctest.simulator.run_and_pytest(
        well_formed_command=command,
        pytest_options=['--strict', '--doctest-modules', '-v']
    )
    assert simulator_status.runner_status.exit_code == 0
    assert simulator_status.pytest_exit_code == 0
    stdout = simulator_status.runner_status.stdout
    assert 'py3         9  setup     "FIRST"' in stdout
    assert 'py3        84  teardown  "LAST"' in stdout


def test_no_blocks_left_to_test_passing():
    """Generate a pytest file that passes when no blocks to test."""
    command = (
        'phmdoctest doc/example1.md -sFIRST'
        ' --skip SECOND --report --outfile discarded.py'
    )
    simulator_status = phmdoctest.simulator.run_and_pytest(
        well_formed_command=command,
        pytest_options=['--strict', '--doctest-modules', '-v']
    )
    assert simulator_status.runner_status.exit_code == 0
    assert simulator_status.pytest_exit_code == 0
    assert 'def test_nothing_passes()' in simulator_status.outfile


def test_no_blocks_left_to_test_fails():
    """Generate a pytest file that asserts when no blocks to test."""
    command = (
        'phmdoctest doc/example1.md -sFIRST --fail-nocode'
        ' --skip SECOND --report --outfile discarded.py'
    )
    simulator_status = phmdoctest.simulator.run_and_pytest(
        well_formed_command=command,
        pytest_options=['--strict', '--doctest-modules', '-v']
    )
    assert simulator_status.runner_status.exit_code == 0
    assert simulator_status.pytest_exit_code == 1    # pytest failed
    assert 'def test_nothing_fails()' in simulator_status.outfile


def test_no_code_blocks():
    """Process .md that has no code blocks."""
    command = (
        'phmdoctest tests/no_code_blocks.md'
        ' --report --outfile discarded.py'
    )
    simulator_status = phmdoctest.simulator.run_and_pytest(
        well_formed_command=command,
        pytest_options=['--strict', '--doctest-modules', '-v']
    )
    assert simulator_status.runner_status.exit_code == 0
    assert simulator_status.pytest_exit_code == 0
    assert 'def test_nothing_passes()' in simulator_status.outfile


def test_empty_code_blocks_report():
    """Report counts empty code and output blocks."""
    command = 'phmdoctest tests/empty_code_block.md --report'
    simulator_status = phmdoctest.simulator.run_and_pytest(
        well_formed_command=command,
        pytest_options=None
    )
    assert simulator_status.runner_status.exit_code == 0
    stdout = simulator_status.runner_status.stdout
    with open('tests/empty_code_report.txt', 'r', encoding='utf-8') as f:
        want = f.read()
    verify.a_and_b_are_the_same(want, stdout)


def test_missing_markdown_file():
    """Usage error for MARKDOWN_FILE that does not exist."""
    command = 'phmdoctest tests/bogus.md --outfile discarded.py'
    simulator_status = phmdoctest.simulator.run_and_pytest(
        well_formed_command=command,
        pytest_options=['--strict', '--doctest-modules', '-v']
    )
    assert (
            simulator_status.runner_status.exit_code ==
            click.UsageError.exit_code
    )
    assert simulator_status.outfile is None
    assert simulator_status.pytest_exit_code is None


def test_bad_usage_option():
    """Usage error for misspelled option."""
    command = 'phmdoctest doc/example1.md --misspelled --outfile discarded.py'
    simulator_status = phmdoctest.simulator.run_and_pytest(
        well_formed_command=command,
        pytest_options=['--strict', '--doctest-modules', '-v']
    )
    assert (
            simulator_status.runner_status.exit_code == click.UsageError.exit_code
    )
    assert simulator_status.outfile is None
    assert simulator_status.pytest_exit_code is None
