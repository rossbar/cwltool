from pathlib import Path
from stat import S_IWRITE, S_IWGRP, S_IWOTH
from typing import Any

from cwltool.factory import Factory
from cwltool.main import main

from .util import get_data, get_main_output, needs_docker, needs_singularity


def test_newline_in_entry() -> None:
    """Files in a InitialWorkingDirectory are created with a newline character."""
    factory = Factory()
    echo = factory.make(get_data("tests/wf/iwdr-entry.cwl"))
    assert echo(message="hello") == {"out": "CONFIGVAR=hello\n"}


@needs_docker
def test_empty_file_creation() -> None:
    """An empty file can be created in InitialWorkingDirectory."""
    err_code, _, _ = get_main_output([get_data("tests/wf/iwdr-empty.cwl")])
    assert err_code == 0


@needs_docker
def test_directory_literal_with_real_inputs_inside(tmp_path: Path) -> None:
    """Cope with unmoveable files in the output directory created by Docker+IWDR."""
    err_code, _, _ = get_main_output(
        [
            "--out",
            str(tmp_path),
            get_data("tests/iwdr_dir_literal_real_file.cwl"),
            "--example={}".format(get_data("tests/__init__.py")),
        ]
    )
    assert err_code == 0


@needs_docker
def test_iwdr_permutations(tmp_path_factory: Any) -> None:
    misc = tmp_path_factory.mktemp("misc")
    fifth = str(tmp_path_factory.mktemp("fifth"))
    sixth = str(tmp_path_factory.mktemp("sixth"))
    seventh = str(tmp_path_factory.mktemp("seventh"))
    eighth = str(tmp_path_factory.mktemp("eighth"))
    first = misc / "first"
    first.touch()
    second = misc / "second"
    second.touch()
    third = misc / "third"
    third.touch()
    fourth = misc / "fourth"
    fourth.touch()
    outdir = str(tmp_path_factory.mktemp("outdir"))
    assert (
        main(
            [
                "--outdir",
                outdir,
                "--enable-dev",
                get_data("tests/wf/iwdr_permutations.cwl"),
                "--first",
                str(first),
                "--second",
                str(second),
                "--third",
                str(third),
                "--fourth",
                str(fourth),
                "--fifth",
                fifth,
                "--sixth",
                sixth,
                "--seventh",
                seventh,
                "--eighth",
                eighth,
            ]
        )
        == 0
    )


def test_iwdr_permutations_readonly(tmp_path_factory: Any) -> None:
    """Confirm that readonly input files are properly made writable."""
    misc = tmp_path_factory.mktemp("misc")
    fifth = tmp_path_factory.mktemp("fifth")
    fifth_file = fifth / "bar"
    fifth_dir = fifth / "foo"
    fifth_file.touch()
    fifth_dir.mkdir()
    sixth = tmp_path_factory.mktemp("sixth")
    first = misc / "first"
    first.touch()
    second = misc / "second"
    second.touch()
    outdir = str(tmp_path_factory.mktemp("outdir"))
    for entry in [first, second, fifth, sixth, fifth_file, fifth_dir]:
        mode = entry.stat().st_mode
        ro_mask = 0o777 ^ (S_IWRITE | S_IWGRP | S_IWOTH)
        entry.chmod(mode & ro_mask)
    assert (
        main(
            [
                "--no-container",
                "--debug",
                "--leave-outputs",
                "--outdir",
                outdir,
                get_data("tests/wf/iwdr_permutations_nocontainer.cwl"),
                "--first",
                str(first),
                "--second",
                str(second),
                "--fifth",
                str(fifth),
                "--sixth",
                str(sixth),
            ]
        )
        == 0
    )
    for entry in [first, second, fifth, sixth, fifth_file, fifth_dir]:
        try:
            mode = entry.stat().st_mode
            entry.chmod(mode | S_IWRITE)
        except PermissionError:
            pass


@needs_docker
def test_iwdr_permutations_inplace(tmp_path_factory: Any) -> None:
    misc = tmp_path_factory.mktemp("misc")
    fifth = str(tmp_path_factory.mktemp("fifth"))
    sixth = str(tmp_path_factory.mktemp("sixth"))
    seventh = str(tmp_path_factory.mktemp("seventh"))
    eighth = str(tmp_path_factory.mktemp("eighth"))
    first = misc / "first"
    first.touch()
    second = misc / "second"
    second.touch()
    third = misc / "third"
    third.touch()
    fourth = misc / "fourth"
    fourth.touch()
    outdir = str(tmp_path_factory.mktemp("outdir"))
    assert (
        main(
            [
                "--outdir",
                outdir,
                "--enable-ext",
                "--enable-dev",
                "--overrides",
                get_data("tests/wf/iwdr_permutations_inplace.yml"),
                get_data("tests/wf/iwdr_permutations.cwl"),
                "--first",
                str(first),
                "--second",
                str(second),
                "--third",
                str(third),
                "--fourth",
                str(fourth),
                "--fifth",
                fifth,
                "--sixth",
                sixth,
                "--seventh",
                seventh,
                "--eighth",
                eighth,
            ]
        )
        == 0
    )


@needs_singularity
def test_iwdr_permutations_singularity(tmp_path_factory: Any) -> None:
    misc = tmp_path_factory.mktemp("misc")
    fifth = str(tmp_path_factory.mktemp("fifth"))
    sixth = str(tmp_path_factory.mktemp("sixth"))
    seventh = str(tmp_path_factory.mktemp("seventh"))
    eighth = str(tmp_path_factory.mktemp("eighth"))
    first = misc / "first"
    first.touch()
    second = misc / "second"
    second.touch()
    third = misc / "third"
    third.touch()
    fourth = misc / "fourth"
    fourth.touch()
    outdir = str(tmp_path_factory.mktemp("outdir"))
    assert (
        main(
            [
                "--outdir",
                outdir,
                "--enable-dev",
                "--singularity",
                get_data("tests/wf/iwdr_permutations.cwl"),
                "--first",
                str(first),
                "--second",
                str(second),
                "--third",
                str(third),
                "--fourth",
                str(fourth),
                "--fifth",
                fifth,
                "--sixth",
                sixth,
                "--seventh",
                seventh,
                "--eighth",
                eighth,
            ]
        )
        == 0
    )


@needs_singularity
def test_iwdr_permutations_singularity_inplace(tmp_path_factory: Any) -> None:
    misc = tmp_path_factory.mktemp("misc")
    fifth = str(tmp_path_factory.mktemp("fifth"))
    sixth = str(tmp_path_factory.mktemp("sixth"))
    seventh = str(tmp_path_factory.mktemp("seventh"))
    eighth = str(tmp_path_factory.mktemp("eighth"))
    first = misc / "first"
    first.touch()
    second = misc / "second"
    second.touch()
    third = misc / "third"
    third.touch()
    fourth = misc / "fourth"
    fourth.touch()
    outdir = str(tmp_path_factory.mktemp("outdir"))
    assert (
        main(
            [
                "--outdir",
                outdir,
                "--singularity",
                "--enable-ext",
                "--enable-dev",
                "--overrides",
                get_data("tests/wf/iwdr_permutations_inplace.yml"),
                get_data("tests/wf/iwdr_permutations.cwl"),
                "--first",
                str(first),
                "--second",
                str(second),
                "--third",
                str(third),
                "--fourth",
                str(fourth),
                "--fifth",
                fifth,
                "--sixth",
                sixth,
                "--seventh",
                seventh,
                "--eighth",
                eighth,
            ]
        )
        == 0
    )
