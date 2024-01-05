import nox

@nox.session()
def install(session):
    session.install("flit")
    session.run("flit", "install", "--deps", "production")