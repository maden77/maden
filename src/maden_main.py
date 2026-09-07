import sys
from maden_lexer import Lexer
from maden_parser import Parser
from maden_transpiler import Transpiler

def main():
    if len(sys.argv) < 2:
        print("Cara pakai: python maden_main.py contoh.maden")
        return
    
    # Baca file
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        kode = f.read()
    
    # Lexer
    lexer = Lexer(kode)
    token = lexer.tokenisasi()
    print("\n=== TOKEN ===")
    for t in token:
        print(t)
    
    # Parser
    parser = Parser(token)
    ast = parser.parse()
    print("\n=== AST ===")
    print(ast)
    
    # Transpiler
    transpiler = Transpiler()
    hasil = transpiler.transpile(ast)
    print("\n=== KODE PYTHON ===")
    print(hasil)
    
    # Simpan ke file
    with open("output.py", 'w', encoding='utf-8') as f:
        f.write(hasil)
    print("\n✅ Berhasil transpile ke output.py")

if __name__ == "__main__":
    main()
