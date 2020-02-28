from collections import namedtuple
import itertools
import os.path
from tempfile import TemporaryDirectory

from click.testing import CliRunner

from .main import entry_point


# todo- does click result include a copy of the command?
TestStatus = namedtuple('TestStatus',
    ['status',
     'outfile',
     'pytest_exit_code'])


counter = itertools.count()
"""
Iterator that counts up from zero. Used for making a filename.

It is used to make a unique basename (or PurePatn.name) when 
the invoked phmdoctest writes an OUTFILE into the tempdir.
This avoids a pytest error when:
1. simulate_and_pytest() is called a from a 
   pytest test case function.
2. simulate_and_pytest() is called a second time from the
   same pytest test case function.
3. both simulate_and_pytest() calls also call pytest.main()

  import file mismatch:
  imported module 'test_1' has this __file__ attribute:
    <temp dir absolute path>test_1.py
  which is not the same as the test file we want to collect:
   <different temp dir absolute path>test_1.py
  HINT: remove __pycache__ / .pyc files and/or use a 
  unique basename for your test file modules
  
  To see this happen set up 1-3 above and patch counter
  here to: counter = itertools.cycle([1]) 
"""


def run_and_pytest(
        well_formed_command,
        pytest_options=None):
    """
    Simulate a phmdoctest command, optionally run pytest.

    If a filename is provide by the --outfile option, the
    command is rewritten replacing the OUTFILE with a
    path to a temporary directory and a synthesized filename.

    To run pytest on an --outfile, pass a list of zero or
    more pytest_options.
    To run pytest the PYPI package pytest must be installed
    since pytest is not required top install phmdoctest.
    Use this command:
        pip install pytest

    Returns TestStatus object.

    TestStatus.status is the CliRunner.invoke return value.

    If an outfile is written or streamed to stdout a copy of it
    is returned in TestStatus.outfile.

    well_formed_command
    - starts with phmdoctest
    - followed by MARKDOWN_FILE
    - ends with --outfile OUTFILE (if needed)
    - all other options are between MARKDOWN_FILE and --outfile
    for example:
    phmdoctest MARKDOWN_FILE --skip FIRST --outfile OUTFILE

    pytest_options
    List of strings like this: ['--strict', '-vv'].
    Set to empty list to run pytest with no options.
    Set to None to skip pytest.
    """
    # todo- use a sphinx or other arg format for parameters

    # chop off phmdoctest since invoking by a python function call
    assert well_formed_command.startswith('phmdoctest ')
    command1 = well_formed_command.replace('phmdoctest ', '', 1)
    # simulate commands that don't write OUTFILE.
    wants_help = '--help' in command1
    wants_version = '--version' in command1
    stream_outfile = command1.endswith('--outfile -')
    no_outfile = '--outfile' not in command1
    runner = CliRunner()
    if wants_help or wants_version or stream_outfile or no_outfile:
        return TestStatus(
            status=runner.invoke(cli=entry_point, args=command1),
            outfile=None,
            pytest_exit_code=None
        )

    # Simulate commands that write an OUTFILE.
    # Split up the command into pieces.
    # Chop out the path to the markdown file.
    # Drop the rest of the command starting at --outfile and the
    # outfile path since we rename the outfile in the invoked command.
    with TemporaryDirectory() as tmpdirname:
        # Create a new unique filename in the temporary directly to
        # receive the OUTFILE.
        # Rewrite the command to use the new OUTFILE path and
        # split up the command to a list of strings.
        # Calling invoke with the single string form of the
        # rewritten command fails to find the outfile.
        # This might be because it is now an absolute path
        # to the tmpdir.
        # counter's docstring explains its use.
        test_file_name = 'test_' + str(next(counter)) + '.py'
        outfile_path = os.path.join(tmpdirname, test_file_name)
        markdown_path, command2 = command1.split(maxsplit=1)
        command3 = command2[:command2.find('--outfile')].strip()
        pfm_args = [markdown_path]
        pfm_args.extend(command3.split())
        pfm_args.extend(['--outfile', outfile_path])
        status = runner.invoke(cli=entry_point, args=pfm_args)

        # return now if the command failed
        if status.exit_code:
            return TestStatus(
                status=status,
                outfile=None,
                pytest_exit_code=None
            )

        # Copy the generated pytest file from the isolated filesystem.
        with open(outfile_path, 'r') as fp:
            outfile_text = fp.read()

        pytest_exit_code = None
        if pytest_options is not None:
            import pytest
            print()    # desirable if terminal shows captured stdout
            pytest_exit_code = pytest.main(pytest_options + [tmpdirname])
        return TestStatus(
            status=status,
            outfile=outfile_text,
            pytest_exit_code=pytest_exit_code
        )
