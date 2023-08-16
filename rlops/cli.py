import click
import os
from multiprocessing import Process
import subprocess


_CONTEXT_SETTINGS = {"help_option_names": ['-h', '--help']}


@click.group(context_settings=_CONTEXT_SETTINGS)
def cli():
    pass



@cli.command('serve')
@click.option(
    '-H', '--host', type=str, default='0.0.0.0', help='server host. Default: "0.0.0.0"',
)
@click.option(
    '-p', '--port', type=int, default=8501, help='server port. Default: 8501',
)
@click.option(
    '--reload',
    is_flag=True,
    help='whether to reload the server when the codes have been changed',
)
def serve(host, port, reload):
    """开启HTTP服务。"""

    path = os.path.realpath(os.path.dirname(__file__))
    api = Process(
        target=start_server,
        kwargs={'path': path, 'host': host, 'port': port, 'reload': reload},
    )
    api.start()
    api.join()


def start_server(path, port, reload):
    cmd = ['streamlit run', 'server/main.py', '--server.port', str(port)]
    if reload:
        cmd.append('--reload')
    subprocess.call(cmd, cwd=path)


if __name__ == "__main__":
    cli()