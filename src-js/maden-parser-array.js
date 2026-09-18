class Program { constructor(statements) { this.type='Program'; this.statements=statements; } }
class FunctionDeclaration { constructor(name,params,body) { this.type='FunctionDeclaration'; this.name=name; this.params=params; this.body=body; } }
class ReturnStatement { constructor(value) { this.type='ReturnStatement'; this.value=value; } }
class PrintStatement { constructor(expression) { this.type='PrintStatement'; this.expression=expression; } }
class AssignmentStatement { constructor(name,value) { this.type='AssignmentStatement'; this.name=name; this.value=value; } }
class IfStatement { constructor(condition,thenBranch,elseBranch) { this.type='IfStatement'; this.condition=condition; this.thenBranch=thenBranch; this.elseBranch=elseBranch; } }
class WhileStatement { constructor(condition,body) { this.type='WhileStatement'; this.condition=condition; this.body=body; } }
class ForStatement { constructor(variable,iterable,body) { this.type='ForStatement'; this.variable=variable; this.iterable=iterable; this.body=body; } }
class BlockStatement { constructor(statements) { this.type='BlockStatement'; this.statements=statements; } }
class VariableExpression { constructor(name) { this.type='VariableExpression'; this.name=name; } }
class LiteralExpression { constructor(value) { this.type='LiteralExpression'; this.value=value; } }
class ArrayExpression { constructor(elements) { this.type='ArrayExpression'; this.elements=elements; } }
class BinaryExpression { constructor(operator,left,right) { this.type='BinaryExpression'; this.operator=operator; this.left=left; this.right=right; } }
class CallExpression { constructor(callee,args) { this.type='CallExpression'; this.callee=callee; this.args=args; } }

class Parser {
  constructor(tokens) { this.tokens=tokens; this.index=0; }
  current() { return this.tokens[this.index]; }
  advance() { return this.tokens[this.index++]; }
  expect(type,message) { const t=this.current(); if(t.type!==type) throw new Error(`${message} (baris ${t.line}, kolom ${t.column})`); return this.advance(); }
  skipNewlines() { while(this.current().type==='NEWLINE') this.advance(); }
  parse() { const a=[]; this.skipNewlines(); while(this.current().type!=='EOF'){ a.push(this.statement()); this.skipNewlines(); } return new Program(a); }
  statement() {
    this.skipNewlines(); const t=this.current();
    if(t.type==='FUNGSI') return this.functionDeclaration();
    if(t.type==='KEMBALI') { this.advance(); const v=this.current().type==='NEWLINE'||this.current().type==='BLOK_TUTUP'?null:this.expression(); return new ReturnStatement(v); }
    if(t.type==='CETAK') { this.advance(); this.expect('KURUNG_BUKA','Diharapkan ( setelah cetak'); const e=this.expression(); this.expect('KURUNG_TUTUP','Diharapkan ) setelah cetak'); return new PrintStatement(e); }
    if(t.type==='JIKA') return this.ifStatement();
    if(t.type==='ULANGI') return this.whileStatement();
    if(t.type==='UNTUK') return this.forStatement();
    if(t.type==='IDENTIFIER') { const n=this.advance().value; if(this.current().type==='SAMA'){this.advance();return new AssignmentStatement(n,this.expression());} if(this.current().type==='KURUNG_BUKA') return this.call(n); throw new Error(`Pernyataan tidak dikenal: ${n}`); }
    throw new Error(`Pernyataan tidak dikenal: ${t.type} (${t.value})`);
  }
  block() { this.expect('BLOK_BUKA','Diharapkan { untuk membuka blok'); const a=[]; this.skipNewlines(); while(this.current().type!=='BLOK_TUTUP'&&this.current().type!=='EOF'){a.push(this.statement());this.skipNewlines();} this.expect('BLOK_TUTUP','Blok belum ditutup dengan }'); return new BlockStatement(a); }
  functionDeclaration() { this.advance(); const n=this.expect('IDENTIFIER','Diharapkan nama fungsi').value; this.expect('KURUNG_BUKA','Diharapkan ('); const p=[]; if(this.current().type!=='KURUNG_TUTUP'){do{p.push(this.expect('IDENTIFIER','Diharapkan nama parameter').value);if(this.current().type!=='KOMA')break;this.advance();}while(true);} this.expect('KURUNG_TUTUP','Diharapkan )'); return new FunctionDeclaration(n,p,this.block()); }
  ifStatement() { this.advance(); const c=this.expression(); const yes=this.block(); let no=null; this.skipNewlines(); if(this.current().type==='SELAIN'){this.advance(); this.skipNewlines(); no=this.current().type==='JIKA'?this.ifStatement():this.block();} return new IfStatement(c,yes,no); }
  whileStatement() { this.advance(); this.expect('SELAMA','Diharapkan selama setelah ulangi'); return new WhileStatement(this.expression(),this.block()); }
  forStatement() { this.advance(); this.expect('SETIAP','Diharapkan setiap'); const v=this.expect('IDENTIFIER','Diharapkan variabel').value; this.expect('DALAM','Diharapkan dalam'); return new ForStatement(v,this.expression(),this.block()); }
  call(n) { this.expect('KURUNG_BUKA','Diharapkan ('); const a=[]; if(this.current().type!=='KURUNG_TUTUP'){do{a.push(this.expression());if(this.current().type!=='KOMA')break;this.advance();}while(true);} this.expect('KURUNG_TUTUP','Diharapkan )'); return new CallExpression(n,a); }
  expression(){return this.or();}
  or(){let x=this.and();while(this.current().type==='ATAU'){const o=this.advance().value;x=new BinaryExpression(o,x,this.and());}return x;}
  and(){let x=this.eq();while(this.current().type==='DAN'){const o=this.advance().value;x=new BinaryExpression(o,x,this.eq());}return x;}
  eq(){let x=this.compare();while(['SAMA_DENGAN','TIDAK_SAMA'].includes(this.current().type)){const o=this.advance().value;x=new BinaryExpression(o,x,this.compare());}return x;}
  compare(){let x=this.add();while(['LEBIH_BESAR','LEBIH_KECIL','LEBIH_BESAR_SAMA','LEBIH_KECIL_SAMA'].includes(this.current().type)){const o=this.advance().value;x=new BinaryExpression(o,x,this.add());}return x;}
  add(){let x=this.mul();while(['TAMBAH','KURANG'].includes(this.current().type)){const o=this.advance().value;x=new BinaryExpression(o,x,this.mul());}return x;}
  mul(){let x=this.unary();while(['KALI','BAGI','MOD'].includes(this.current().type)){const o=this.advance().value;x=new BinaryExpression(o,x,this.unary());}return x;}
  unary(){if(this.current().type==='KURANG'){this.advance();return new BinaryExpression('-',new LiteralExpression(0),this.unary());}if(this.current().type==='TIDAK'){this.advance();return new BinaryExpression('not',new LiteralExpression(true),this.unary());}return this.primary();}
  primary(){const t=this.current();if(t.type==='ANGKA'||t.type==='TEKS'){this.advance();return new LiteralExpression(t.value);}if(t.type==='BENAR'||t.type==='SALAH'||t.type==='KOSONG'){this.advance();return new LiteralExpression(t.type==='BENAR'?true:t.type==='SALAH'?false:null);}if(t.type==='IDENTIFIER'){const n=this.advance().value;return this.current().type==='KURUNG_BUKA'?this.call(n):new VariableExpression(n);}if(t.type==='KURUNG_BUKA'&&t.value==='['){this.advance();const e=[];if(!(this.current().type==='KURUNG_TUTUP'&&this.current().value===']')){do{e.push(this.expression());if(this.current().type!=='KOMA')break;this.advance();}while(true);}this.expect('KURUNG_TUTUP','Diharapkan ]');return new ArrayExpression(e);}if(t.type==='KURUNG_BUKA'){this.advance();const e=this.expression();this.expect('KURUNG_TUTUP','Diharapkan )');return e;}throw new Error(`Ekspresi tidak dikenal: ${t.type} (${t.value})`);}
}
if(typeof module!=='undefined') module.exports={Parser,Program,FunctionDeclaration,ReturnStatement,PrintStatement,AssignmentStatement,IfStatement,WhileStatement,ForStatement,BlockStatement,VariableExpression,LiteralExpression,ArrayExpression,BinaryExpression,CallExpression};
