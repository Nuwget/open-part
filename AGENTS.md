# AGENTS.md

Instruções para agentes (e humanos) trabalhando neste repositório.

## Autonomia e aprovação

- **NUNCA** fazer merge de PR, force push ou apagar repositório/branch
  sem aprovação explícita e clara do usuário na mesma conversa.
- Pedir antes de destruir estado (revert, reset --hard, delete).

## Commits

- Use **Conventional Commits**: `feat:`, `fix:`, `docs:`, `refactor:`,
  `chore:`, `test:`, `perf:`, `style:`.
- Um commit por mudança lógica, em ordem.
- Mensagens em inglês, imperativo, sem ponto final.

## Arquitetura

- Separe **lógica pura** de **interface**: `src/core.py` não importa Tkinter
  e não lê/escreve arquivos sem necessidade; `src/gui.py` apenas apresenta.
- Funções pequenas, nomes claros, sem efeitos colaterais escondidos.
- Novas features entram primeiro no core (com teste lógico em mente),
  depois ganham UI.

## Código limpo

- Python 3.10+, type hints em funções públicas.
- Sem código comentado morto; remova o que não usa.
- Tratamento de erro explícito nas bordas (abrir arquivo, salvar, etc.).
