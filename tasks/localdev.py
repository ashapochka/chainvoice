from invoke import task


@task
def runapp(c):
    c.run('uvicorn app.main:app --reload')
