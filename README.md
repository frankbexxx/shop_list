# Market Flow

Aplicação de lista de compras pensada para uso real no supermercado, com foco em rapidez no telemóvel, organização por corredor, orçamento e itens recorrentes.

## O que já faz

- Criar várias listas de compras.
- Adicionar produtos com quantidade, unidade, corredor, categoria, prioridade e preço estimado.
- Marcar o avanço da compra com um toque: `por comprar -> no carrinho -> comprado`.
- Calcular total estimado, orçamento restante e taxa de conclusão.
- Duplicar listas para compras recorrentes.
- Sugerir produtos frequentes para preenchimento rápido.
- Guardar tudo em SQLite local.

## Arranque local

```bash
python main.py
```

A app arranca por omissão em `http://127.0.0.1:8000`.

## Testes

```bash
python -m unittest discover -s tests -v
```
