import click
import os
from multiprocessing import Process
import subprocess


_CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(context_settings=_CONTEXT_SETTINGS)
def cli():
    pass


@cli.command("serve")
@click.option(
    "-H",
    "--host",
    type=str,
    default="0.0.0.0",
    help='server host. Default: "0.0.0.0"',
)
@click.option(
    "-p",
    "--port",
    type=int,
    default=8501,
    help="server port. Default: 8501",
)
@click.option(
    "--reload",
    is_flag=True,
    help="whether to reload the server when the codes have been changed",
)
def serve(host, port, reload):
    """开启HTTP服务。"""

    path = os.path.realpath(os.path.dirname(__file__))
    api = start_server(path=path, port=port)


def start_server(path, port):
    try:
        # 执行shell命令并捕获日志
        process = subprocess.run(
            f"cd {path} && streamlit run server/main.py --server.port {port}",
            shell=True,
            capture_output=True,
            preexec_fn=os.setsid,
            text=True,
            timeout=1,  # 设定超时时间
            check=True,  # 检查命令执行结果，若返回非零状态码则抛出异常
        )

        if process.stdout or process.stderr:
            msg = process.stderr.strip()
        else:
            msg = "your script is processed success"

        return msg
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"
    except subprocess.TimeoutExpired:
        return "Command execution timed out"


if __name__ == "__main__":
    cli()
