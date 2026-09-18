import contextlib
import io
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
    def transpile(self, source):
        tokens = Lexer(source).tokenisasi()
        self.assertEqual(tokens[-1].tipe, TokenType.EOF)
        return Transpiler().transpile(Parser(tokens).parse())

    def test_function_call_pipeline(self):
        output = self.transpile(
            "fungsi tambah(a, b) {\n"
            "    kembali a + b\n"
            "}\n\n"
            "cetak(tambah(2, 3))\n"
        )
        self.assertIn("def tambah(a, b):", output)
        self.assertIn("return (a + b)", output)
        self.assertIn("print(tambah(2, 3))", output)
        compile(output, "<maden-output>", "exec")

    def test_generated_program_runs(self):
        output = self.transpile(
            "fungsi tambah(a, b) {\n"
            "    kembali a + b\n"
            "}\n\n"
            "cetak(tambah(2, 3))\n"
        )
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            exec(compile(output, "<maden-output>", "exec"), {})
        self.assertEqual(captured.getvalue(), "5\n")

    def test_relational_and_boolean_tokens(self):
        tokens = Lexer("2 >= 1 && 3 != 4 <= 5 || 6 == 6").tokenisasi()
        types = [token.tipe for token in tokens]
        self.assertIn(TokenType.LEBIH_BESAR_SAMA, types)
        self.assertIn(TokenType.TIDAK_SAMA, types)
        self.assertIn(TokenType.LEBIH_KECIL_SAMA, types)
        self.assertIn(TokenType.SAMA_DENGAN_DUA, types)
        self.assertIn(TokenType.DAN, types)
        self.assertIn(TokenType.ATAU, types)

    def test_relational_and_boolean_expression(self):
        output = self.transpile(
            "jika 2 >= 1 && 3 != 4 {\n"
            "    cetak(benar)\n"
            "}\n"
        )
        self.assertIn("if ((2 >= 1) and (3 != 4)):", output)
        compile(output, "<maden-output>", "exec")


if __name__ == "__main__":
    unittest.main()
