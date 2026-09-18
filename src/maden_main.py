import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from maden_lexer import Lexer
from maden_parser import Parser
from maden_transpiler import Transpiler


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("Cara pakai: python src/maden_main.py contoh.maden")
        return 1

    source_path = args[0]
    try:
        with open(source_path, "r", encoding="utf-8") as source_file:
            kode = source_file.read()
        ast = Parser(Lexer(kode).tokenisasi()).parse()
        hasil = Transpiler().transpile(ast)
    except (OSError, SyntaxError, TypeError) as error:
        print(f"Gagal memproses {source_path}: {error}")
        return 1

    output_path = os.path.join(os.getcwd(), "output.py")
    try:
        with open(output_path, "w", encoding="utf-8") as output_file:
            output_file.write(hasil)
    except OSError as error:
        print(f"Gagal menulis {output_path}: {error}")
        return 1

    print(f"Berhasil transpile ke {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
