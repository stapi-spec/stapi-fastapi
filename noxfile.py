import nox


@nox.session(python=["3.12"])
def tests(session):
    session.run("poetry", "install", external=True)
    session.run("poetry", "run", "pytest", external=True)
