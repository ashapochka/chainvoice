from invoke import task


@task
def build_image(c):
    c.run('docker build -t chainvoice .')


@task
def run_container(c):
    c.run('docker run -d --name chainvoice1 -p 80:80 chainvoice')
