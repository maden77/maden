class ASTNode {}

class Program extends ASTNode {
  constructor(statements) {
    this.type = 'Program';
    this.statements = statements;
  }
}

class FunctionDeclaration extends ASTNode {
  constructor(name, params, body) {
    this.type = 'FunctionDeclaration';
    this.name = name;
    this.params = params;
    this.body = body;
  }
}

class ReturnStatement extends ASTNode {
  constructor(value) {
    this.type = 'ReturnStatement';
    this.value = value;
  }
}

class PrintStatement extends ASTNode {
  constructor(expression) {
    this.type = 'PrintStatement';
    this.expression = expression;
  }
}

class AssignmentStatement extends ASTNode {
  constructor(name, value) {
    this.type = 'AssignmentStatement';
    this.name = name;
    this.value = value;
  }
}

class IfStatement extends ASTNode {
  constructor(condition, thenBranch, elseBranch) {
    this.type = 'IfStatement';
    this.condition = condition;
    this.thenBranch = thenBranch;
    this.elseBranch = elseBranch;
  }
}

class WhileStatement extends ASTNode {
  constructor(condition, body) {
    this.type = 'WhileStatement';
    this.condition = condition;
    this.body = body;
  }
}

class ForStatement extends ASTNode {
  constructor(variable, iterable, body) {
    this.type = 'ForStatement';
    this.variable = variable;
    this.iterable = iterable;
    this.body = body;
  }
}

class BlockStatement extends ASTNode {
  constructor(statements) {
    this.type = 'BlockStatement';
    this.statements = statements;
  }
}

class VariableExpression extends ASTNode {
  constructor(name) {
    this.type = 'VariableExpression';
    this.name = name;
  }
}

class LiteralExpression extends ASTNode {
  constructor(value) {
    this.type = 'LiteralExpression';
    this.value = value;
  }
}

class BinaryExpression extends ASTNode {
  constructor(operator, left, right) {
    this.type = 'BinaryExpression';
    this.operator = operator;
    this.left = left;
    this.right = right;
  }
}

class CallExpression extends ASTNode {
  constructor(callee, args) {
    this.type = 'CallExpression';
    this.callee = callee;
    this.args = args;
  }
}

class Parser {
  constructor(tokens) {
    this.tokens = tokens;
    this.index = 0;
  }

  current() {
    return this.tokens[this.index];
  }

  advance() {
    const token = this.current();
    this.index += 1;
    return token;
  }

  peek(offset = 0) {
    return this.tokens[this.index + offset] || this.tokens[this.tokens.length - 1];
  }

  match(...types) {
    const token = this.current();
    if (types.includes(token.type)) {
      this.index += 1;
      return token;
    }
    return null;
  }

  expect(type, message) {
    const token = this.current();
    if (token.type !== type) {
      throw new Error(`${message} (baris ${token.line}, kolom ${token.column})`);
    }
    this.index += 1;
    return token;
  }

  skipNewlines() {
    while (this.current().type === 'NEWLINE') this.advance();
  }

  parse() {
    const statements = [];
    this.skipNewlines();
    while (this.current().type !== 'EOF') {
      statements.push(this.parseStatement());
      this.skipNewlines();
    }
    return new Program(statements);
  }

  parseStatement() {
    this.skipNewlines();
    const token = this.current();

    if (token.type === 'FUNGSI') return this.parseFunctionDeclaration();
    if (token.type === 'KEMBALI') return this.parseReturnStatement();
    if (token.type === 'CETAK') return this.parsePrintStatement();
    if (token.type === 'JIKA') return this.parseIfStatement();
    if (token.type === 'ULANGI') return this.parseWhileStatement();
    if (token.type === 'UNTUK') return this.parseForStatement();
    if (token.type === 'IDENTIFIER') {
      const name = this.advance().value;
      if (this.current().type === 'SAMA') {
        this.advance();
        const value = this.parseExpression();
        return new AssignmentStatement(name, value);
      }
      if (this.current().type === 'KURUNG_BUKA') {
        return this.parseCallStatement(name);
      }
      throw new Error(`Pernyataan tidak dikenal: ${name}`);
    }

    throw new Error(`Pernyataan tidak dikenal: ${token.type} (${token.value})`);
  }

  parseFunctionDeclaration() {
    this.expect('FUNGSI', 'Diharapkan kata kunci fungsi');
    const name = this.expect('IDENTIFIER', 'Diharapkan nama fungsi').value;
    this.expect('KURUNG_BUKA', 'Diharapkan ( setelah nama fungsi');
    const params = [];
    if (this.current().type !== 'KURUNG_TUTUP') {
      while (true) {
        params.push(this.expect('IDENTIFIER', 'Diharapkan nama parameter').value);
        if (this.current().type !== 'KOMA') break;
        this.advance();
      }
    }
    this.expect('KURUNG_TUTUP', 'Diharapkan ) setelah parameter');
    const body = this.parseBlock();
    return new FunctionDeclaration(name, params, body);
  }

  parseReturnStatement() {
    this.expect('KEMBALI', 'Diharapkan kata kunci kembali');
    const value = this.current().type === 'NEWLINE' ? null : this.parseExpression();
    return new ReturnStatement(value);
  }

  parsePrintStatement() {
    this.expect('CETAK', 'Diharapkan kata kunci cetak');
    this.expect('KURUNG_BUKA', 'Diharapkan ( setelah cetak');
    const expr = this.parseExpression();
    this.expect('KURUNG_TUTUP', 'Diharapkan ) setelah ekspresi');
    return new PrintStatement(expr);
  }

  parseIfStatement() {
    this.expect('JIKA', 'Diharapkan kata kunci jika');
    const condition = this.parseExpression();
    const thenBranch = this.parseBlock();
    let elseBranch = null;
    if (this.current().type === 'SELAIN') {
      this.advance();
      elseBranch = this.parseBlock();
    }
    return new IfStatement(condition, thenBranch, elseBranch);
  }

  parseWhileStatement() {
    this.expect('ULANGI', 'Diharapkan kata kunci ulangi');
    this.expect('SELAMA', 'Diharapkan kata kunci selama setelah ulangi');
    const condition = this.parseExpression();
    const body = this.parseBlock();
    return new WhileStatement(condition, body);
  }

  parseForStatement() {
    this.expect('UNTUK', 'Diharapkan kata kunci untuk');
    this.expect('SETIAP', 'Diharapkan kata kunci setiap setelah untuk');
    const variable = this.expect('IDENTIFIER', 'Diharapkan nama variabel').value;
    this.expect('DALAM', 'Diharapkan kata kunci dalam');
    const iterable = this.parseExpression();
    const body = this.parseBlock();
    return new ForStatement(variable, iterable, body);
  }

  parseBlock() {
    this.expect('BLOK_BUKA', 'Diharapkan { untuk membuka blok');
    const statements = [];
    this.skipNewlines();
    while (this.current().type !== 'BLOK_TUTUP') {
      statements.push(this.parseStatement());
      this.skipNewlines();
    }
    this.expect('BLOK_TUTUP', 'Diharapkan } untuk menutup blok');
    return new BlockStatement(statements);
  }

  parseCallStatement(calleeName) {
    const args = [];
    this.expect('KURUNG_BUKA', 'Diharapkan ( setelah nama fungsi');
    if (this.current().type !== 'KURUNG_TUTUP') {
      while (true) {
        args.push(this.parseExpression());
        if (this.current().type !== 'KOMA') break;
        this.advance();
      }
    }
    this.expect('KURUNG_TUTUP', 'Diharapkan ) setelah argumen');
    return new CallExpression(calleeName, args);
  }

  parseExpression() {
    return this.parseLogicalOr();
  }

  parseLogicalOr() {
    let left = this.parseLogicalAnd();
    while (this.current().type === 'ATAU') {
      const operator = this.advance().value;
      const right = this.parseLogicalAnd();
      left = new BinaryExpression(operator, left, right);
    }
    return left;
  }

  parseLogicalAnd() {
    let left = this.parseEquality();
    while (this.current().type === 'DAN') {
      const operator = this.advance().value;
      const right = this.parseEquality();
      left = new BinaryExpression(operator, left, right);
    }
    return left;
  }

  parseEquality() {
    let left = this.parseComparison();
    while (this.current().type === 'SAMA_DENGAN' || this.current().type === 'TIDAK_SAMA') {
      const operator = this.advance().value;
      const right = this.parseComparison();
      left = new BinaryExpression(operator, left, right);
    }
    return left;
  }

  parseComparison() {
    let left = this.parseAdditive();
    while (
      this.current().type === 'LEBIH_BESAR' ||
      this.current().type === 'LEBIH_KECIL' ||
      this.current().type === 'LEBIH_BESAR_SAMA' ||
      this.current().type === 'LEBIH_KECIL_SAMA'
    ) {
      const operator = this.advance().value;
      const right = this.parseAdditive();
      left = new BinaryExpression(operator, left, right);
    }
    return left;
  }

  parseAdditive() {
    let left = this.parseMultiplicative();
    while (this.current().type === 'TAMBAH' || this.current().type === 'KURANG') {
      const operator = this.advance().value;
      const right = this.parseMultiplicative();
      left = new BinaryExpression(operator, left, right);
    }
    return left;
  }

  parseMultiplicative() {
    let left = this.parseUnary();
    while (this.current().type === 'KALI' || this.current().type === 'BAGI' || this.current().type === 'MOD') {
      const operator = this.advance().value;
      const right = this.parseUnary();
      left = new BinaryExpression(operator, left, right);
    }
    return left;
  }

  parseUnary() {
    if (this.current().type === 'KURANG') {
      this.advance();
      return new BinaryExpression('-', new LiteralExpression(0), this.parseUnary());
    }
    if (this.current().type === 'TIDAK') {
      this.advance();
      return new BinaryExpression('not', new LiteralExpression(true), this.parseUnary());
    }
    return this.parsePrimary();
  }

  parsePrimary() {
    const token = this.current();

    if (token.type === 'ANGKA') {
      this.advance();
      return new LiteralExpression(token.value);
    }

    if (token.type === 'TEKS') {
      this.advance();
      return new LiteralExpression(token.value);
    }

    if (token.type === 'BENAR') {
      this.advance();
      return new LiteralExpression(true);
    }

    if (token.type === 'SALAH') {
      this.advance();
      return new LiteralExpression(false);
    }

    if (token.type === 'KOSONG') {
      this.advance();
      return new LiteralExpression(null);
    }

    if (token.type === 'IDENTIFIER') {
      const name = this.advance().value;
      if (this.current().type === 'KURUNG_BUKA') {
        this.advance();
        const args = [];
        if (this.current().type !== 'KURUNG_TUTUP') {
          while (true) {
            args.push(this.parseExpression());
            if (this.current().type !== 'KOMA') break;
            this.advance();
          }
        }
        this.expect('KURUNG_TUTUP', 'Diharapkan ) pada pemanggilan fungsi');
        return new CallExpression(name, args);
      }
      return new VariableExpression(name);
    }

    if (token.type === 'KURUNG_BUKA') {
      this.advance();
      const expr = this.parseExpression();
      this.expect('KURUNG_TUTUP', 'Diharapkan ) untuk menutup ekspresi');
      return expr;
    }

    throw new Error(`Ekspresi tidak dikenal: ${token.type} (${token.value})`);
  }
}

if (typeof module !== 'undefined') {
  module.exports = { ASTNode, Program, FunctionDeclaration, ReturnStatement, PrintStatement, AssignmentStatement, IfStatement, WhileStatement, ForStatement, BlockStatement, VariableExpression, LiteralExpression, BinaryExpression, CallExpression, Parser };
}
