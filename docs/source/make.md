# A short primer on make

"make" is a build automation tool that is commonly used in software development projects to automate repetitive tasks.
This is historically such as compiling source code, linking object files, and building executables - and more recently managing complex (development) environments with different tools and languages mixed.

Using "make" in Python projects makes sense because it provides a way to manage dependencies and build processes in a consistent and repeatable way.
This can be particularly useful in large projects with multiple contributors, as it ensures that everyone is building and testing the project in the same way.
Additionally, "make" provides a simple and concise way to describe build processes, which makes it easier for developers to understand and maintain the build system over time.

## Dependency management

In "make", dependency management is achieved through the use of rules and dependencies.
A rule defines a target, its dependencies, and the commands necessary to create the target.
The dependencies for a target specify the other files that it relies on and must be built before the target can be built.

When "make" is run, it checks the timestamps of the target and its dependencies.
If the target is older than its dependencies, "make" will run the commands in the rule to rebuild the target.
If the dependencies are up-to-date, "make" will skip the build process for the target, saving time and resources.

This way, "make" can handle the complex and interdependent steps to form processes of a project, automatically handling the correct order of steps and avoiding unnecessary execution of steps.

## The "phony" target

In "make", a "phony" target is a special type of target that is used to define a target that is not a file or directory. Phony targets are used to describe actions that need to be performed but do not result in a file that can be used as a target in another rule.

For example, a common use case for a phony target is to define a "clean" target that removes all generated files.
A makefile could have a rule like the following:

```makefile
.PHONY: clean

clean:
    rm -rf build
```

The ".PHONY" line indicates that the "clean" target is a phony target. When "make clean" is run, the command in the rule will be executed to remove the "build" directory.

Phony targets are useful because they provide a way to define targets that don't correspond to files and can be used to perform arbitrary actions such as cleaning the build directory or running tests.
Additionally, "make" considers phony targets to always be out-of-date, so the commands for a phony target will always be executed, even if its dependencies are up-to-date.
This can be useful when you want to guarantee that an action is performed, such as cleaning the build directory before a build.

(make-sentinel-files)=

## Sentinel files

Tracking the state of a target in "make" is typically done by checking the timestamp of a file that is the output of a particular step.
However, there are instances where the steps in the build process do not create files, or the files they do create are not easily trackable.
In such cases, it becomes difficult to determine if a target needs to be rebuilt.
To overcome this challenge, other methods, such as using sentinel files, can be employed to keep track of the state of the build process.

```{info}
Sentinel files are used to indicate whether a target has been built, or if a process has been completed.
```

For example, a makefile could use a sentinel file to track the state of a build process.
The makefile could contain a rule like the following:

```makefile

build: sentinel
    # build commands go here

sentinel:
    # build commands go here
    touch sentinel
```

In this example, the "sentinel" file is used to track the state of the build. If the "sentinel" file exists, it means that the build has been completed and the build commands will be skipped.
If the "sentinel" file does not exist, the build commands will be executed and the "sentinel" file will be created to indicate that the build has been completed.

Sentinel files are useful in "make" because they provide a way to track the state of a build or process, allowing "make" to determine if a target needs to be rebuilt.
This helps to avoid unnecessary rebuilds, which can save time and resources.

## Variables

In "make", variables are used to store values that can be referenced in multiple places throughout the makefile. Variables are defined by assigning a value to a name and can be used in rules, dependencies, and commands.

For example, the following makefile uses a variable to store the name of the compiler:

```makefile

CC = gcc

main: main.c
    $(CC) -o main main.c
```

In this example, the "CC" variable is defined with the value "gcc", which is then used in the command to compile the "main.c" file.
This allows for easy modification of the compiler if needed, as the change only needs to be made in one place, instead of throughout the entire makefile.

Variables can also be used to store values that are generated dynamically, such as the result of a shell command. For example:

```makefile

OBJECTS = $(shell ls *.c | sed s/.c/.o/g)

main: $(OBJECTS)
    gcc -o main $(OBJECTS)
```

In this example, the "OBJECTS" variable is defined as the result of a shell command that lists all "*.c" files and replaces the ".c" extension with ".o".
The "OBJECTS" variable can then be used in the dependencies and command of the "main" target.

Variables in "make" can also be overridden on the command line, allowing for easy customization of the build process.
For example, the following command would use a different compiler than the one defined in the makefile:

```shell
make CC=clang
```

This way, "make" variables provide a flexible and convenient way to manage build configurations and reuse values throughout the makefile.

There are many more details about variables in the GNU Make Manual.

## Further Reading

For more information, read the [GNU Make Manual](https://www.gnu.org/software/make/manual/make.html).
