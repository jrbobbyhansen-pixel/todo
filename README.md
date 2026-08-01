# todo

A zero-dependency command-line todo list manager. Add, list, complete, and delete tasks from your terminal. Tasks are stored in `~/.todo/tasks.json` as plain JSON. Works on macOS, Linux, and WSL.

## Install

```bash
pip install git+https://github.com/jrbobbyhansen-pixel/todo.git
```

Or just copy `todo.py` somewhere in your `$PATH` and run it directly:

```bash
curl -o /usr/local/bin/todo https://raw.githubusercontent.com/jrbobbyhansen-pixel/todo/master/todo.py
chmod +x /usr/local/bin/todo
```

## Usage

```bash
todo add "buy milk"              # Add a task
todo list                        # List pending tasks
todo list --all                  # List all tasks (including completed)
todo done 1                      # Mark task 1 as done
todo delete 1                    # Delete task 1
todo --version                   # Show version
todo --help                      # Show help
```

Aliases: `list` → `ls`, `delete` → `rm`.
