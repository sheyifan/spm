import argparse
import os
import shutil
import traceback
from typing import Optional, List, Tuple
from pathlib import Path

import sqlite3
import sys

from meta import mete_file


def init():
    with sqlite3.connect(mete_file) as conn:
        try:
            conn.execute("PRAGMA foreign_keys = 1")
            conn.isolation_level = 'EXCLUSIVE'
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS PROJECTS (
                NAME TEXT PRIMARY KEY,
                URL TEXT UNIQUE NOT NULL,
                PARENT TEXT,
                CONSTRAINT REVISON_LINK FOREIGN KEY (PARENT) REFERENCES PROJECTS(NAME) ON DELETE SET NULL ON UPDATE CASCADE
            )
            """)

            cursor.execute("CREATE INDEX IF NOT EXISTS PARENT_IDX ON PROJECTS (PARENT)")
        except Exception as sys_error:
            conn.rollback()
            raise sys_error


class ProjectExistsError(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code


class InvalidProjectURL(Exception):
    """
    Occur when the given url can not be recognized or be occupied.
    """
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code


class ProjectNotFound(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code


def create_project(name: str, url: str, parent: Optional[str] = None):
    """
    Create this project and store it.
    :raises InvalidProjectURL: when the given url can not be recognized or be occupied.
    :raises ProjectExistsError: when the given project name is been used by another project.
    :raises ProjectNotFound: when specified parent project name is missing.
    :raises Exception: software internal error to be addressed by the developers.
    """
    with sqlite3.connect(mete_file) as conn:
        try:
            conn.execute("PRAGMA foreign_keys = 1")
            conn.isolation_level = 'EXCLUSIVE'
            cursor = conn.cursor()
            cursor.execute(r"SELECT * FROM PROJECTS WHERE NAME = ?", (name,))
            if cursor.fetchone() is not None:
                raise ProjectExistsError(f"Duplicated project name: {name}")

            cursor.execute(r"INSERT INTO PROJECTS (NAME, URL, PARENT) VALUES (?, ?, ?)",
                           (name, url, parent))

            if Path(url).exists():
                raise InvalidProjectURL(f"Can not create project located at {url}")
            try:
                os.makedirs(url)
            except OSError:
                raise InvalidProjectURL(f"Can not create project located at {url}")

            conn.commit()
        except (ProjectExistsError, ProjectNotFound) as user_error:
            conn.rollback()
            raise user_error
        except (InvalidProjectURL, OSError) as file_error:
            conn.rollback()
            raise file_error
        except Exception as sys_error:
            conn.rollback()
            raise sys_error


def get_projects() -> List[Tuple[str, str]]:
    """
    :return: name and url for each project
    """
    with sqlite3.connect(mete_file) as conn:
        cursor = conn.cursor()
        cursor.execute(r"SELECT NAME, URL FROM PROJECTS")
        return cursor.fetchall()


def delete_project(name: str):
    with sqlite3.connect(mete_file) as conn:
        try:
            conn.execute("PRAGMA foreign_keys = 1")
            conn.isolation_level = 'EXCLUSIVE'
            cursor = conn.cursor()
            cursor.execute("SELECT URL FROM PROJECTS WHERE NAME = ?", (name,))
            url = cursor.fetchone()[0]
            cursor.execute("DELETE FROM PROJECTS WHERE NAME = ?", (name,))
            shutil.rmtree(url)
            conn.commit()
        except FileNotFoundError:
            conn.rollback()
            raise ProjectNotFound(f"Project located at {url} is not found.")
        except Exception as sys_error:
            conn.rollback()
            raise sys_error


def rename_project(name: str, new_name: str):
    with sqlite3.connect(mete_file) as conn:
        try:
            conn.execute("PRAGMA foreign_keys = 1")
            conn.isolation_level = 'EXCLUSIVE'
            cursor = conn.cursor()
            cursor.execute("SELECT URL FROM PROJECTS WHERE NAME = ?", (name,))
            url = cursor.fetchone()[0]
            cursor.execute("UPDATE PROJECTS SET NAME = ? WHERE NAME = ?", (new_name, name))
            url = Path(url)
            new_url = url.parent / new_name
            url.rename(new_url)
            conn.commit()
        except FileNotFoundError:
            conn.rollback()
            raise ProjectNotFound(f"Project located at {url} is not found.")
        except Exception as sys_error:
            conn.rollback()
            raise sys_error


def relocate_project(name: str, new_url: str):
    with sqlite3.connect(mete_file) as conn:
        try:
            conn.execute("PRAGMA foreign_keys = 1")
            conn.isolation_level = 'EXCLUSIVE'
            cursor = conn.cursor()
            cursor.execute("SELECT URL FROM PROJECTS WHERE NAME = ?", (name,))
            url = cursor.fetchone()[0]
            cursor.execute("UPDATE PROJECTS SET URL = ? WHERE NAME = ?", (new_url, name))
            if Path(new_url).exists():
                raise InvalidProjectURL(f"Can not relocate project to {new_url}")
            shutil.move(url, new_url)
            conn.commit()
        except FileNotFoundError:
            conn.rollback()
            raise ProjectNotFound(f"Project located at {url} is not found.")
        except Exception as sys_error:
            conn.rollback()
            raise sys_error


init()


def main():
    # Top command parser
    parser = argparse.ArgumentParser(prog="spm", description="A simple CLI for software project management.")

    # Subcommand parser for identifying resources
    target_parser = parser.add_subparsers(dest="target", help="Subcommands")

    # Sub command: volume
    volume_parser = target_parser.add_parser("project", help="Manage Docker volumes")
    project_op_parser = volume_parser.add_subparsers(dest="operation", help="Project operation")
    project_op_parser.add_parser("ls", help="List projects")
    project_op_parser.add_parser("rm", help="Remove project")
    project_op_parser.add_parser("mv", help="Move project")
    project_op_parser.add_parser("rename", help="Rename project")
    project_op_parser.add_parser("add", help="Add project")

    target_parser.add_parser("release", help="Manage software releases")

    # Parse command line options
    args = parser.parse_args()


if __name__ == '__main__':
    # try:
    #     create_project('test', r'C:\Users\yvanshe\Documents\workdir\tmp\python\testpro')
    #     create_project('test1', r'C:\Users\yvanshe\Documents\workdir\tmp\python\testpro1', 'test')
    #     relocate_project("test", r"C:\Users\yvanshe\Documents\workdir\tmp\cpt")
    # except ProjectExistsError as e:
    #     traceback.print_exc()
    # except InvalidProjectURL as e:
    #     traceback.print_exc()
    # except ProjectNotFound as e:
    #     traceback.print_exc()
    # except:
    #     print("Software internal error.", file=sys.stderr)
    #     traceback.print_exc()
    # get_projects()
    main()
