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
        with open(source_path, 'r', encoding='utf-8') as f:
            kode = f.read()
    except FileNotFoundError:
        print(f"File tidak ditemukan: {source_path}")
        return 1
    except OSError as e:
        print(f"Gagal membaca file: {e}")
        return 1

    try:
        lexer = Lexer(kode)
        token = lexer.tokenisasi()
        parser = Parser(token)
        ast = parser.parse()
    except Exception as e:
        print(f"Error parsing: {e}")
        return 1

    try:
        transpiler = Transpiler()
        hasil = transpiler.transpile(ast)
    except Exception as e:
        print(f"Error transpile: {e}")
        return 1

    output_path = os.path.join(os.getcwd(), "output.py")
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(hasil)
    except OSError as e:
        print(f"Gagal menulis output.py: {e}")
        return 1

    print(f"✅ Berhasil transpile ke {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
