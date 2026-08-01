"""Tests for todo CLI tool."""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

# Ensure we can import todo.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import todo


class TestTodo(unittest.TestCase):
    """Test suite for todo CLI tool."""

    def setUp(self):
        """Set up a temporary todo directory for each test."""
        self.tmpdir = tempfile.mkdtemp()
        self.orig_todo_dir = todo.TODO_DIR
        self.orig_todo_file = todo.TODO_FILE
        todo.TODO_DIR = self.tmpdir
        todo.TODO_FILE = os.path.join(self.tmpdir, "tasks.json")

    def tearDown(self):
        """Restore original paths."""
        todo.TODO_DIR = self.orig_todo_dir
        todo.TODO_FILE = self.orig_todo_file
        # Clean up temp dir
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    # --- Happy path tests ---

    def test_add_task(self):
        """Adding a task should create it and return 0."""
        rc = todo.main(["add", "buy", "milk"])
        self.assertEqual(rc, 0)
        tasks = todo._load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["description"], "buy milk")
        self.assertFalse(tasks[0]["done"])

    def test_add_multiple_words(self):
        """Adding a task with multiple words should preserve them."""
        todo.main(["add", "finish", "the", "report"])
        tasks = todo._load_tasks()
        self.assertEqual(tasks[0]["description"], "finish the report")

    def test_list_empty(self):
        """Listing with no tasks should print 'No tasks.' and return 0."""
        rc = todo.main(["list"])
        self.assertEqual(rc, 0)

    def test_list_with_tasks(self):
        """Listing should show pending tasks."""
        todo.main(["add", "task one"])
        todo.main(["add", "task two"])
        rc = todo.main(["list"])
        self.assertEqual(rc, 0)

    def test_list_all(self):
        """--all should show completed tasks too."""
        todo.main(["add", "task one"])
        todo.main(["add", "task two"])
        todo.main(["done", "1"])
        rc = todo.main(["list", "--all"])
        self.assertEqual(rc, 0)

    def test_done_task(self):
        """Marking a task done should set done=True."""
        todo.main(["add", "something"])
        rc = todo.main(["done", "1"])
        self.assertEqual(rc, 0)
        tasks = todo._load_tasks()
        self.assertTrue(tasks[0]["done"])

    def test_delete_task(self):
        """Deleting a task should remove it."""
        todo.main(["add", "something"])
        rc = todo.main(["delete", "1"])
        self.assertEqual(rc, 0)
        tasks = todo._load_tasks()
        self.assertEqual(len(tasks), 0)

    def test_delete_alias_rm(self):
        """'rm' alias should work like 'delete'."""
        todo.main(["add", "something"])
        rc = todo.main(["rm", "1"])
        self.assertEqual(rc, 0)
        tasks = todo._load_tasks()
        self.assertEqual(len(tasks), 0)

    def test_list_alias_ls(self):
        """'ls' alias should work like 'list'."""
        todo.main(["add", "something"])
        rc = todo.main(["ls"])
        self.assertEqual(rc, 0)

    def test_version(self):
        """--version should print version string and exit 0."""
        with self.assertRaises(SystemExit) as cm:
            todo.main(["--version"])
        self.assertEqual(cm.exception.code, 0)

    def test_help(self):
        """--help should print help and exit 0."""
        with self.assertRaises(SystemExit) as cm:
            todo.main(["--help"])
        self.assertEqual(cm.exception.code, 0)

    # --- Error path tests ---

    def test_done_nonexistent(self):
        """Marking a nonexistent task done should print error and return 1."""
        rc = todo.main(["done", "999"])
        self.assertEqual(rc, 1)

    def test_delete_nonexistent(self):
        """Deleting a nonexistent task should print error and return 1."""
        rc = todo.main(["delete", "999"])
        self.assertEqual(rc, 1)

    def test_no_command(self):
        """Running with no subcommand should exit with code 2 (argparse default)."""
        with self.assertRaises(SystemExit) as cm:
            todo.main([])
        self.assertEqual(cm.exception.code, 2)

    def test_invalid_id_type(self):
        """Passing a non-integer id should fail."""
        with self.assertRaises(SystemExit):
            todo.main(["done", "abc"])

    def test_corrupted_json(self):
        """Corrupted tasks.json should be handled gracefully."""
        os.makedirs(self.tmpdir, exist_ok=True)
        with open(todo.TODO_FILE, "w") as f:
            f.write("not valid json")
        tasks = todo._load_tasks()
        self.assertEqual(tasks, [])

    def test_add_then_list_output(self):
        """Adding then listing should show the task."""
        todo.main(["add", "test", "output"])
        # Capture stdout
        from io import StringIO
        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        try:
            todo.main(["list"])
        finally:
            sys.stdout = old_stdout
        output = captured.getvalue()
        self.assertIn("test output", output)

    def test_done_then_list_hides(self):
        """Completed task should not appear in default list."""
        todo.main(["add", "hidden", "task"])
        todo.main(["done", "1"])
        from io import StringIO
        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        try:
            todo.main(["list"])
        finally:
            sys.stdout = old_stdout
        output = captured.getvalue()
        self.assertNotIn("hidden task", output)

    def test_multiple_tasks_ids_increment(self):
        """Task IDs should auto-increment."""
        todo.main(["add", "first"])
        todo.main(["add", "second"])
        tasks = todo._load_tasks()
        self.assertEqual(tasks[0]["id"], 1)
        self.assertEqual(tasks[1]["id"], 2)

    def test_delete_reuses_id(self):
        """Deleting a task should not reuse its id."""
        todo.main(["add", "first"])
        todo.main(["add", "second"])
        todo.main(["delete", "1"])
        todo.main(["add", "third"])
        tasks = todo._load_tasks()
        ids = [t["id"] for t in tasks]
        self.assertIn(2, ids)
        self.assertIn(3, ids)
        self.assertNotIn(1, ids)


if __name__ == "__main__":
    unittest.main()
