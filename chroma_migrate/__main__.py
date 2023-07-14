from bullet import Bullet, SlidePrompt, Check, Input, YesNo, Numbers
from bullet import styles
from bullet import colors
import chromadb
from chromadb.config import Settings
from import_clickhouse import migrate_from_clickhouse
from import_duckdb import migrate_from_duckdb

cli = SlidePrompt(
    [
         Bullet("Which configuration of chroma is your data currently stored in? ",
            choices = ["Clickhouse", "DuckDB"],
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
if current_config == "Clickhouse":
    clickhouse_host = Input("What is the ip/hostname of your clickhouse server", default = "localhost", word_color = colors.foreground["yellow"])
    clickhouse_port = Input("What is the port of your clickhouse server", default = "8123", word_color = colors.foreground["yellow"])
    prompts.append(clickhouse_host)
    prompts.append(clickhouse_port)

if current_config == "DuckDB":
    duckdb_path = Input("What is the path to the persist directory your data is currently stored in?", default = "./chroma", word_color = colors.foreground["yellow"])
    prompts.append(duckdb_path)

if target_config == "Running on a remote server":
    chroma_host = Input("What is the ip/hostname of your chroma server", default = "localhost", word_color = colors.foreground["yellow"])
    chroma_port = Input("What is the port of your chroma server", default = "8000", word_color = colors.foreground["yellow"])
    prompts.append(chroma_host)
    prompts.append(chroma_port)

if target_config == "Running locally":
    chroma_persist_directory = Input("What is the path you would like your data to be stored in?", default = "./chroma_new", word_color = colors.foreground["yellow"])
    prompts.append(chroma_persist_directory)

cli = SlidePrompt(prompts)
print('\n')
result = cli.launch()

api = None
if target_config == "Running locally":
    # TODO: change to new api
    for prompt, answer in result:
        if prompt == "What is the path you would like your data to be stored in?":
            persist_directory = answer
    api = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=persist_directory))

if target_config == "Running on a remote server":
    for prompt, answer in result:
        if prompt == "What is the ip/hostname of your chroma server":
            chroma_host = answer
        if prompt == "What is the port of your chroma server":
            chroma_port = answer
    api = chromadb.Client(Settings(chroma_api_impl="rest", chroma_host=chroma_host, chroma_port=chroma_port))

if current_config == "DuckDB":
    for prompt, answer in result:
        if prompt == "What is the path to the persist directory your data is currently stored in?":
            persist_directory = answer
    migrate_from_duckdb(api, persist_directory)

if current_config == "Clickhouse":
    for prompt, answer in result:
        if prompt == "What is the ip/hostname of your clickhouse server":
            clickhouse_host = answer
        if prompt == "What is the port of your clickhouse server":
            clickhouse_port = answer
    migrate_from_clickhouse(api, clickhouse_host, clickhouse_port)


if current_config == "Clickhouse":
    clickhouse_host = result[0][1]
    clickhouse_port = result[1][1]