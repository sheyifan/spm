import argparse
import os.path
import traceback

import meta
from project import create_project, ProjectExistsError, ProjectNotFound


def create_domain_parser(argument_parser: argparse.ArgumentParser):
    """
    Init parser of resource name spaces (domain)
    """


def main():
    # Top command parser
    parser = argparse.ArgumentParser(prog="spm", description="A simple CLI for software project management.")

    # Subcommand parser for identifying resources
    resource_parser = parser.add_subparsers(dest="resource", help="Subcommands", required=True)
    # Domain commands parser
    project_parser = resource_parser.add_parser("proj", help="Manage software projects")
    release_parser = resource_parser.add_parser("sw", help="Manage software releases")

    project_op_parser = project_parser.add_subparsers(dest="operation", help="Project operation", required=True)
    project_op_parser.add_parser("ls", help="List projects")
    op_parser = project_op_parser.add_parser("rm", help="Remove project")
    op_parser.add_argument("--name", type=str, help="Project name", required=True)
    op_parser = project_op_parser.add_parser("mv", help="Move (relocate) project")
    op_parser.add_argument("--name", type=str, help="Project name", required=True)
    op_parser.add_argument("--des", type=str, help="Destination location", required=True)
    op_parser = project_op_parser.add_parser("rn", help="Rename project")
    op_parser.add_argument("--name", type=str, help="Project name", required=True)
    op_parser.add_argument("--new-name", type=str, help="New name", required=True)
    op_parser = project_op_parser.add_parser("add", help="Add project")
    op_parser.add_argument("--name", type=str, help="Project name", required=True)
    op_parser.add_argument("--url", type=str, help="Project Location")
    op_parser.add_argument("--parent", type=str, help="Parent project")

    # Parse command line options
    args = parser.parse_args()
    if args.resource == "proj":
        if args.operation == "add":
            project_name = args.name
            url = args.url
            parent = args.parent
            if url is None:
                url = os.path.join(meta.default_projects_url, project_name)
            try:
                create_project(project_name, url, parent)
            except ProjectExistsError:
                print(f"Project '{project_name}' has exists.")
            except ProjectNotFound:
                print(f"Parent project '{parent}' not found.")
            except:
                traceback.print_exc()


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
