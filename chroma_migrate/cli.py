from bullet import Bullet, SlidePrompt, Check, Input, YesNo, Numbers
from bullet import styles
from bullet import colors

import chromadb
from chromadb.config import Settings

from chroma_migrate.import_clickhouse import migrate_from_clickhouse
from chroma_migrate.import_duckdb import migrate_from_duckdb
from chroma_migrate.import_chromadb import migrate_from_remote_chroma

_logo = """
                \033[38;5;069m(((((((((    \033[38;5;203m(((((\033[38;5;220m####         
             \033[38;5;069m(((((((((((((\033[38;5;203m(((((((((\033[38;5;220m#########    
           \033[38;5;069m(((((((((((((\033[38;5;203m(((((((((((\033[38;5;220m###########  
         \033[38;5;069m((((((((((((((\033[38;5;203m((((((((((((\033[38;5;220m############ 
        \033[38;5;069m(((((((((((((\033[38;5;203m((((((((((((((\033[38;5;220m#############
        \033[38;5;069m(((((((((((((\033[38;5;203m((((((((((((((\033[38;5;220m#############
         \033[38;5;069m((((((((((((\033[38;5;203m(((((((((((((\033[38;5;220m##############
         \033[38;5;069m((((((((((((\033[38;5;203m((((((((((((\033[38;5;220m############## 
           \033[38;5;069m((((((((((\033[38;5;203m(((((((((((\033[38;5;220m#############   
             \033[38;5;069m((((((((\033[38;5;203m((((((((\033[38;5;220m##############     
                \033[38;5;069m(((((\033[38;5;203m((((    \033[38;5;220m#########\033[0m            

    """


def run_cli():
    print(_logo)
    print("Welcome to the Chroma Migration Tool")
    print("This tool will help you migrate your data from versions less than v0.4.0 to the latest version of Chroma")

    cli = SlidePrompt(
        [
            Bullet("Where would you like to migrate your data from? ",
                choices = ["Clickhouse (You run chroma with a clickhouse instance)", "DuckDB (You run chroma and save files to a persist_directory)", "Chroma server (You run a chroma server running you access via the HTTP client)"],
                bullet = " >",
                margin = 2,
                bullet_color = colors.bright(colors.foreground["cyan"]),
                background_color = colors.background["black"],
                background_on_switch = colors.background["black"],
                word_color = colors.foreground["white"],
                word_on_switch = colors.foreground["white"]
            ),
            Bullet("Where is the Chroma instance you want to migrate to?",
                choices = ["Running locally", "Running on a remote server"],
                bullet = " >",
                margin = 2,
                bullet_color = colors.bright(colors.foreground["cyan"]),
                background_color = colors.background["black"],
                background_on_switch = colors.background["black"],
                word_color = colors.foreground["white"],
                word_on_switch = colors.foreground["white"]
            ),
        ]
    )

    print('\n')
    result = cli.launch()
    current_config = result[0][1]
    target_config = result[1][1]

    prompts = []
    if "Clickhouse" in current_config:
        clickhouse_host = Input("What is the ip/hostname of your clickhouse server", default = "localhost", word_color = colors.foreground["yellow"])
        clickhouse_port = Input("What is the port of your clickhouse server", default = "8123", word_color = colors.foreground["yellow"])
        prompts.append(clickhouse_host)
        prompts.append(clickhouse_port)

    if "DuckDB" in current_config:
        duckdb_path = Input("What is the path to the persist directory your data is currently stored in?", default = "./chroma", word_color = colors.foreground["yellow"])
        prompts.append(duckdb_path)
    
    if "Chroma server" in current_config:
        chroma_host = Input("What is the ip/hostname of your chroma server", default = "localhost", word_color = colors.foreground["yellow"])
        chroma_port = Input("What is the port of your chroma server", default = "8000", word_color = colors.foreground["yellow"])
        prompts.append(chroma_host)
        prompts.append(chroma_port)

    if target_config == "Running on a remote server":
        chroma_host = Input("What is the ip/hostname of your chroma server", default = "localhost", word_color = colors.foreground["yellow"])
        chroma_port = Input("What is the port of your chroma server", default = "8000", word_color = colors.foreground["yellow"])
        prompts.append(chroma_host)
        prompts.append(chroma_port)

    if target_config == "Running locally":
        chroma_persist_directory = Input("What is the path you would like your data to be stored in?", default = "./chroma_migrated", word_color = colors.foreground["yellow"])
        prompts.append(chroma_persist_directory)

    cli = SlidePrompt(prompts)
    print('\n')
    result = cli.launch()

    api = None
    if target_config == "Running locally":
        for prompt, answer in result:
            if prompt == "What is the path you would like your data to be stored in?":
                persist_directory = answer
        api = chromadb.PersistentClient(path=persist_directory)

    if target_config == "Running on a remote server":
        for prompt, answer in result:
            if prompt == "What is the ip/hostname of your chroma server":
                chroma_host = answer
            if prompt == "What is the port of your chroma server":
                chroma_port = answer
        api = chromadb.HttpClient(host=chroma_host, port=chroma_port)

    if "DuckDB" in current_config:
        for prompt, answer in result:
            if prompt == "What is the path to the persist directory your data is currently stored in?":
                persist_directory = answer
        migrate_from_duckdb(api, persist_directory)

    if "Clickhouse" in current_config:
        for prompt, answer in result:
            if prompt == "What is the ip/hostname of your clickhouse server":
                clickhouse_host = answer
            if prompt == "What is the port of your clickhouse server":
                clickhouse_port = answer
        migrate_from_clickhouse(api, clickhouse_host, clickhouse_port)
    
    if "Chroma server" in current_config:
        for prompt, answer in result:
            if prompt == "What is the ip/hostname of your chroma server":
                chroma_host = answer
            if prompt == "What is the port of your chroma server":
                chroma_port = answer
        from_chroma = chromadb.HttpClient(host=chroma_host, port=chroma_port)
        migrate_from_remote_chroma(from_chroma, api)
