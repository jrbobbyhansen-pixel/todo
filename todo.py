#!/usr/bin/env python3
"""todo — command-line todo list manager.

Add, list, complete, and delete tasks. Tasks are stored in ~/.todo/tasks.json.
Zero external dependencies (stdlib only: json, argparse, os, sys).
"""

import argparse
import json
import os
import sys

__version__ = "1.0.0"

TODO_DIR = os.path.expanduser("~/.todo")
TODO_FILE = os.path.join(TODO_DIR, "tasks.json")


def _ensure_dir():
    os.makedirs(TODO_DIR, exist_ok=True)


def _load_tasks():
    _ensure_dir()
    if not os.path.exists(TODO_FILE):
        return []
    try:
        with open(TODO_FILE, "r") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return []
        return data
    except (json.JSONDecodeError, OSError):
        return []


def _save_tasks(tasks):
    _ensure_dir()
    with open(TODO_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


def _next_id(tasks):
    if not tasks:
        return 1
    return max(t["id"] for t in tasks) + 1


def cmd_add(args):
    tasks = _load_tasks()
    task = {
        "id": _next_id(tasks),
        "description": " ".join(args.description),
        "done": False,
    }
    tasks.append(task)
    _save_tasks(tasks)
    print(f"Added task {task['id']}: {task['description']}")
    return 0


def cmd_list(args):
    tasks = _load_tasks()
    if not tasks:
        print("No tasks.")
        return 0

    if args.all:
        filtered = tasks
    else:
        filtered = [t for t in tasks if not t["done"]]

    if not filtered:
        print("No tasks.")
        return 0

    for t in filtered:
        status = "✓" if t["done"] else " "
        print(f"[{status}] {t['id']}. {t['description']}")
    return 0


def cmd_done(args):
    tasks = _load_tasks()
    found = False
    for t in tasks:
        if t["id"] == args.id:
            t["done"] = True
            found = True
            break
    if not found:
        print(f"Error: no task with id {args.id}", file=sys.stderr)
        return 1
    _save_tasks(tasks)
    print(f"Completed task {args.id}.")
    return 0


def cmd_delete(args):
    tasks = _load_tasks()
    before = len(tasks)
    tasks = [t for t in tasks if t["id"] != args.id]
    if len(tasks) == before:
        print(f"Error: no task with id {args.id}", file=sys.stderr)
        return 1
    _save_tasks(tasks)
    print(f"Deleted task {args.id}.")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="todo",
        description="Command-line todo list manager.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Add a new task")
    p_add.add_argument("description", nargs="+", help="Task description")

    p_list = sub.add_parser("list", aliases=["ls"], help="List tasks")
    p_list.add_argument(
        "--all", "-a",
        action="store_true",
        help="Show completed tasks too",
    )

    p_done = sub.add_parser("done", help="Mark a task as done")
    p_done.add_argument("id", type=int, help="Task id to mark done")

    p_delete = sub.add_parser("delete", aliases=["rm"], help="Delete a task")
    p_delete.add_argument("id", type=int, help="Task id to delete")

    args = parser.parse_args(argv)

    dispatch = {
        "add": cmd_add,
        "list": cmd_list,
        "ls": cmd_list,
        "done": cmd_done,
        "delete": cmd_delete,
        "rm": cmd_delete,
    }

    fn = dispatch.get(args.command)
    if fn is None:
        parser.print_help()
        return 1

    return fn(args)


if __name__ == "__main__":
    sys.exit(main())
