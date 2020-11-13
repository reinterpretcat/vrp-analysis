import functools

def parse_from_log(source, destination):
    with open(source) as f:
        lines = filter(lambda line: line.startswith("\t("), [line.rstrip() for line in f])

    data = functools.reduce(lambda x ,y: F"{x},{y}", lines)

    with open(destination, "w") as f:
        f.write( F"animation_data=[{data}]")

parse_from_log("source.log", "data.py")