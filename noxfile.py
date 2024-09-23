import nox


@nox.session(python=["3.10", "3.11", "3.12", "pypy3.10"])
def tests(session):
    session.run("poetry", "install", external=True)
    session.run("poetry", "run", "pytest", external=True)
