function setenv() {
{setenv}
}

function unsetenv() {
{unsetenv}
}

trap unsetenv ERR INT

setenv
{content}
unsetenv
