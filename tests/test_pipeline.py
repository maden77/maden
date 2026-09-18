import os
import sys
import unittest

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from maden_lexer import Lexer, TokenType
from maden_parser import Parser
from maden_transpiler import Transpiler


class PipelineTest(unittest.TestCase):
    def test_lexer_parser_transpiler_pipeline(self):
        source = "fungsi tambah(a, b) {\n    kembali a + b\n}\n\ncetak(tambah(2, 3))\n"

        tokens = Lexer(source).tokenisasi()
        self.assertEqual(tokens[-1].tipe, TokenType.EOF)

        ast = Parser(tokens).parse()
        output = Transpiler().transpile(ast)

        self.assertIn("def tambah(a, b):", output)
        self.assertIn("return (a + b)", output)
        self.assertIn("print(tambah(2, 3))", output)

        compile(output, "<maden-output>", "exec")


if __name__ == "__main__":
    unittest.main()
