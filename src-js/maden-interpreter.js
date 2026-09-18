class Environment {
  constructor(parent = null) {
    this.parent = parent;
    this.values = new Map();
  }

  define(name, value) {
    this.values.set(name, value);
    return value;
  }

  assign(name, value) {
    if (this.values.has(name)) {
      this.values.set(name, value);
      return value;
    }
    if (this.parent) {
      return this.parent.assign(name, value);
    }
    throw new Error(`Variabel '${name}' tidak ditemukan`);
  }

  lookup(name) {
    if (this.values.has(name)) {
      return this.values.get(name);
    }
    if (this.parent) {
      return this.parent.lookup(name);
    }
    throw new Error(`Variabel '${name}' tidak ditemukan`);
  }
}

class MadenInterpreter {
  constructor(outputHandler = console.log) {
    this.outputHandler = outputHandler;
    this.globalEnv = new Environment();
    this.globalEnv.define('cetak', (...args) => {
      const text = args.map(a => String(a)).join(' ');
      this.outputHandler(text);
      return null;
    });
  }

  evaluate(node, env = this.globalEnv) {
    if (!node) return null;

    switch (node.type) {
      case 'Program':
        let result = null;
        for (const stmt of node.statements) {
          result = this.evaluate(stmt, env);
        }
        return result;

      case 'FunctionDeclaration': {
        const fn = (...args) => {
          const localEnv = new Environment(env);
          node.params.forEach((param, i) => localEnv.define(param, args[i]));
          let value = null;
          for (const stmt of node.body.statements) {
            try {
              value = this.evaluate(stmt, localEnv);
            } catch (err) {
              if (err && err.name === 'ReturnSignal') {
                return err.value;
              }
              throw err;
            }
          }
          return value;
        };
        env.define(node.name, fn);
        return fn;
      }

      case 'ReturnStatement': {
        if (node.value === null || node.value === undefined) {
          throw { name: 'ReturnSignal', value: null };
        }
        throw { name: 'ReturnSignal', value: this.evaluate(node.value, env) };
      }

      case 'PrintStatement': {
        const value = this.evaluate(node.expression, env);
        this.outputHandler(String(value));
        return value;
      }

      case 'AssignmentStatement':
        return env.assign(node.name, this.evaluate(node.value, env));

      case 'BlockStatement': {
        let result = null;
        for (const stmt of node.statements) {
          result = this.evaluate(stmt, env);
        }
        return result;
      }

      case 'IfStatement': {
        const cond = this.evaluate(node.condition, env);
        if (cond) {
          return this.evaluate(node.thenBranch, env);
        }
        if (node.elseBranch) {
          return this.evaluate(node.elseBranch, env);
        }
        return null;
      }

      case 'WhileStatement': {
        let result = null;
        while (this.evaluate(node.condition, env)) {
          result = this.evaluate(node.body, env);
        }
        return result;
      }

      case 'ForStatement': {
        const iterable = this.evaluate(node.iterable, env);
        let result = null;
        for (const item of iterable) {
          const localEnv = new Environment(env);
          localEnv.define(node.variable, item);
          result = this.evaluate(node.body, localEnv);
        }
        return result;
      }

      case 'VariableExpression':
        return env.lookup(node.name);

      case 'LiteralExpression':
        return node.value;

      case 'BinaryExpression': {
        const left = this.evaluate(node.left, env);
        const right = this.evaluate(node.right, env);

        switch (node.operator) {
          case '+': return left + right;
          case '-': return left - right;
          case '*': return left * right;
          case '/': return left / right;
          case '%': return left % right;
          case '>': return left > right;
          case '<': return left < right;
          case '>=': return left >= right;
          case '<=': return left <= right;
          case '==': return left === right;
          case '!=': return left !== right;
          case '&&': return left && right;
          case '||': return left || right;
          case 'not': return !right;
          default:
            throw new Error(`Operator tidak didukung: ${node.operator}`);
        }
      }

      case 'CallExpression': {
        const callee = env.lookup(node.callee);
        if (typeof callee !== 'function') {
          throw new Error(`'${node.callee}' bukan fungsi`);
        }
        const args = node.args.map(arg => this.evaluate(arg, env));
        return callee(...args);
      }

      default:
        throw new Error(`Node tidak didukung: ${node.type}`);
    }
  }

  run(program) {
    return this.evaluate(program, this.globalEnv);
  }
}

if (typeof module !== 'undefined') {
  module.exports = { Environment, MadenInterpreter };
}
