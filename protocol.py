import io
import struct

END = b"\n"  # end of line
DELIM = b"\x12"  # key/value delimiter

FIELDS = [
    "title",
    "mode",
    "host",
    "host_cuid",
    "host_lvl",
    "cap",
    "team",
    "hp",
    "turns",
    "theme",
    "map",
    "shot",
    "wind",
    "friends",
    "turntime",
    "tracers",
    "items",
    "lvldiff",
    "wager",
    "mod",
    "obs",
    "range",
    "playing",
    "avglvl",
    "chooseweplvl",
    "wepnum",
]

# Decoding helpers


def read_str(f: io.BytesIO):
    length = int.from_bytes(f.read(1), "big")
    return f.read(length)


def peek(f: io.BytesIO, length=1):
    pos = f.tell()
    data = f.read(length)
    f.seek(pos)
    return data


def read_until_end(f: io.BytesIO):
    data = b""
    while True:
        byte = f.read(1)
        if byte in (END, b""):
            break
        data += byte

    return data


def read_key_value(f: io.BytesIO):
    if peek(f) == END:
        f.seek(1, 1)  # Skip lone END byte

    key = read_str(f)
    assert f.read(1) == DELIM
    value = read_str(f)

    return key, value


# Encoding helpers


def to_bytes(any_type):
    if isinstance(any_type, str):
        return any_type.encode()
    elif isinstance(any_type, int) or isinstance(any_type, float) or isinstance(any_type, bool):
        return str(any_type).encode()
    elif isinstance(any_type, bytes):
        return any_type


def write_string(data, s):
    s = to_bytes(s)
    data.write(len(s).to_bytes(1, "big"))
    data.write(s)


def encode_key_value(key, value, end=b'"'):
    data = io.BytesIO()
    write_string(data, key)
    data.write(DELIM)
    write_string(data, value)
    data.write(end)
    return data.getvalue()


# Decoding & Encoding


def decode_all(f):
    if isinstance(f, bytes):
        f = io.BytesIO(f)

    response_type = struct.unpack(">H", f.read(2))[0]

    assert f.read(1) == END

    games = []
    while peek(f):
        game = Game.decode(f)
        games.append(game)

    return games


def encode_all(games):
    parts = []

    for game in games:
        parts.append(game.encode())

    data = io.BytesIO()
    data.write(struct.pack(">H", 1) + END)  # Response type

    # Write all games with lengths
    for part in parts:
        data.write((len(part) + 0x200).to_bytes(2, "little") + END)
        data.write(part)

    return data.getvalue()[:-1]  # Remove last newline


class Game:
    def __init__(self, **kwargs):
        self.unknown = kwargs.get("unknown", 0)
        self.id = kwargs.get("id", "SSLU Game STEAM v1.1")
        self.type = kwargs.get("type", 0)
        self.title = kwargs.get("title", "Proxy's Game")
        self.mode = kwargs.get("mode", "dm")
        self.host = kwargs.get("host", "Proxy")
        self.host_cuid = kwargs.get("host_cuid", "steam76561199084239433")
        self.host_lvl = kwargs.get("host_lvl", 42)
        self.cap = kwargs.get("cap", 2)
        self.team = kwargs.get("team", True)
        self.hp = kwargs.get("hp", 200)
        self.turns = kwargs.get("turns", 0)
        self.theme = kwargs.get("theme", 0)
        self.map = kwargs.get("map", 0)
        self.shot = kwargs.get("shot", 1)
        self.wind = kwargs.get("wind", 0)
        self.friends = kwargs.get("friends", False)
        self.turntime = kwargs.get("turntime", 40)
        self.tracers = kwargs.get("tracers", True)
        self.items = kwargs.get("items", True)
        self.lvldiff = kwargs.get("lvldiff", 100)  # Not default
        self.wager = kwargs.get("wager", 0)
        self.mod = kwargs.get("mod", "none")
        self.obs = kwargs.get("obs", 2)
        self.range = kwargs.get("range", False)
        self.playing = kwargs.get("playing", False)
        self.avglvl = kwargs.get("avglvl", 69)
        self.chooseweplvl = kwargs.get("chooseweplvl", False)
        self.wepnum = kwargs.get("wepnum", 2)

    def __repr__(self):
        return f"<Game {self.title!r}>"

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def decode(f: io.BytesIO):
        length = struct.unpack("H", f.read(2))[0] - 0x200

        tmp = f.read(1)
        assert tmp == END, (tmp, f.read())

        game_id, game_type = read_key_value(f)
        game_id, game_type = game_id.decode(), game_type.decode()

        assert f.read(1) == b"\x18"
        unknown = int.from_bytes(f.read(1), "big")
        read_until_end(f)

        game = Game()
        game.unknown = unknown
        game.id = game_id
        game.type = game_type

        for field in FIELDS:
            key, value = read_key_value(f)
            assert key.decode() == field
            key, value = key.decode(), value
            game[key] = value
            read_until_end(f)

        return game

    def encode(self):
        parts = []

        # Encode id and type (special format)
        unknown = self.unknown.to_bytes(1, "big")
        id_and_type = encode_key_value(self.id, self.type, end=b"\x18" + unknown + b'"')
        parts.append(id_and_type)

        # Encode all normal fields
        for field in FIELDS[:-1]:
            parts.append(encode_key_value(field, self[field]))

        # Last field has no trailing quote
        parts.append(encode_key_value(FIELDS[-1], self[FIELDS[-1]], end=b""))

        # Join with lengths
        data = io.BytesIO()
        for i, part in enumerate(parts[:-1]):
            data.write(part)
            if part != b"":
                length = len(parts[i + 1]) + (i == len(parts) - 2)
                data.write(length.to_bytes(1, "big"))

            data.write(END)

        data.write(parts[-1])
        data.write(END)

        return data.getvalue()


if __name__ == "__main__":
    with open("test/body.bin", "rb") as f:
        orig_data = f.read()
        parsed = decode_all(orig_data)

    with open("test/encoded.bin", "wb") as f:
        encoded = encode_all(parsed)
        f.write(encoded)

    assert orig_data == encoded  # Decoding and encoding should be the same
