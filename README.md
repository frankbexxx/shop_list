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

## License

This project is released under the OXS Non-Commercial Source License v1.0.

Source code is available for personal, educational, research, evaluation and other non-commercial use subject to the terms of the license.

Commercial use, commercial redistribution, SaaS use, incorporation into commercial products or substantial use in business operations requires prior written permission from the copyright holder.

Copyright © 2026 Francisco Bexiga
OXS — Oeiras Xtreme Software

See [LICENSE](LICENSE) for the full terms.
