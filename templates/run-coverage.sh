sources=(
{sourcepaths}
)

sources=$(printf ",%s" "${{sources[@]}}")
sources=${{sources:1}}

{venv}/bin/coverage run \\
    --source=$sources \\
    -m zope.testrunner --auto-color --auto-progress \\
{testpaths}

{venv}/bin/coverage report
{venv}/bin/coverage html
