import tomllib

print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])
