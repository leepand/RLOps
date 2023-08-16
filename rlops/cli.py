import click
import os
from multiprocessing import Process
import subprocess
from .utils.killport import kill9_byport

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
    default=8910,
    help="server port. Default: 8910",
)
@click.option(
    "--reload",
    is_flag=True,
    help="whether to reload the server when the codes have been changed",
)
def serve(host, port, reload):
    """开启HTTP服务。"""

    path = os.path.realpath(os.path.dirname(__file__))
    msg = start_server(path=path, port=port)
    print(msg)


def start_server(path, port):
    try:
        # 执行shell命令并捕获日志
        process = subprocess.run(
            f"cd {path} && streamlit run server/1_📈_Main.py --server.port {port}",
            shell=True,
            capture_output=True,
            preexec_fn=os.setsid,
            text=True,
            timeout=3000,  # 设定超时时间
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


@cli.command("killport", no_args_is_help=True)
@click.option("--port", help="model port", required=True)
@click.option(
    "--confirm", help="confirm", is_flag=True, default=True, show_default=True
)
def killport(port, confirm):
    """
    Kill port process.
    """
    try:
        if confirm:
            c = input("Confirm port {} to {} (y/n)".format(port, "kill"))
            if c == "n":
                return None
        else:
            c = "y"
        if c == "y":
            kill9_byport(port)
    except Exception as e:
        click.echo(e)


if __name__ == "__main__":
    cli()
