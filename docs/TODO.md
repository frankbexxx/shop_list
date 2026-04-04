# TODO

Plano vivo do projeto `shopping_list` para continuar a evolução até uma app madura, testada e pronta para Android e Play Store.

## Estado atual

### Já feito

- Refatoração total da base anterior para uma app web funcional.
- Nova entrada principal em `main.py`.
- Backend novo em `supermarket_app/`.
- Persistência local com SQLite.
- API HTTP para listas, itens, duplicação e ciclo de estados.
- Frontend web responsivo em `web/`.
- Fluxo principal funcional:
  - criar lista
  - adicionar produto
  - marcar produto como por comprar / no carrinho / comprado
  - remover produto
  - duplicar lista
  - arquivar lista
  - ver estimativa e orçamento restante
- Reaproveitamento de sementes base a partir de `assets/data/`.
- Testes automatizados novos em `tests/test_app.py`.
- Testes legacy de Kivy retirados de circulação para não bloquear a nova stack.
- `README.md` inicial criado.
- `Dockerfile` e `render.yaml` preparados, mas ainda não são prioridade de uso.
- Código commitado e pushed para GitHub.

### Decisão atual

- Foco imediato: codar e testar.
- Render e Docker ficam para a fase final ou quase final.
- Android / Play Store só depois de a app estar funcional e quase completa no uso real.

## Próximo ciclo: testes reais

### Testar manualmente agora

- Arrancar a app localmente com `python main.py`.
- Testar no browser desktop.
- Testar no browser mobile.
- Simular uma ida real ao supermercado.
- Verificar se o fluxo é rápido com uma mão e em ecrã pequeno.
- Confirmar se a organização por corredor ajuda mesmo durante as compras.
- Testar criação de listas recorrentes e duplicação semanal.
- Testar comportamento com muitos itens.
- Testar valores monetários e orçamento restante.
- Identificar fricções de UX antes de ampliar funcionalidades.

### Coisas para observar nos testes

- Quantos toques são necessários para adicionar um produto.
- Se o nome dos campos está natural.
- Se faz falta edição inline do item.
- Se a mudança de estado do produto é intuitiva.
- Se o layout continua claro no telemóvel.
- Se faz falta pesquisa, filtros ou agrupamento melhor.
- Se os corredores/categorias atuais são suficientes.

## Implementação antes de produção

### Produto e UX

- Melhorar edição de listas e itens sem fricção.
- Permitir reordenação manual de itens.
- Agrupar visualmente por corredor.
- Adicionar pesquisa de itens dentro da lista.
- Adicionar filtros por estado, prioridade e categoria.
- Adicionar modo "compras rápidas" com botões maiores.
- Melhorar acessibilidade:
  - contraste
  - foco
  - navegação por teclado
  - tamanhos de toque
- Melhorar feedback visual para ações importantes.
- Adicionar confirmações só onde fizer sentido, sem travar o fluxo.

### Domínio e funcionalidades

- Editar item existente.
- Editar lista existente com UI dedicada.
- Marcar lista como concluída.
- Reabrir listas arquivadas.
- Criar listas favoritas / templates de compras recorrentes.
- Guardar histórico de compras anteriores.
- Reaproveitar listas anteriores com um clique.
- Adicionar notas por item mais visíveis.
- Adicionar quantidades sugeridas por histórico.
- Melhorar sugestões frequentes com ranking real.
- Adicionar importação/exportação de listas.
- Suportar múltiplas lojas.
- Associar corredores por loja.
- Suportar preços por loja.
- Preparar base para partilha de listas entre utilizadores.

### Backend e arquitetura

- Criar camada de configuração de ambiente.
- Introduzir logging estruturado.
- Melhorar tratamento global de erros.
- Normalizar validações de input na API.
- Definir melhor versionamento da API.
- Preparar autenticação quando entrar multiutilizador.
- Separar melhor módulos de domínio, storage e apresentação.
- Criar migrações consistentes para a nova base de dados.
- Adicionar backups/export da base local.

### Testes

- Aumentar cobertura do backend.
- Adicionar testes de API para todos os endpoints.
- Adicionar testes de regressão para orçamento e totais.
- Adicionar testes para duplicação, arquivamento e sugestões.
- Adicionar testes end-to-end da interface.
- Testar responsividade mobile de forma repetível.
- Criar smoke test de arranque da aplicação.

## Preparação para quase produção

### Segurança e robustez

- Definir estratégia de autenticação.
- Adicionar gestão de sessão.
- Sanitizar melhor entradas de utilizador.
- Rever exposição pública dos endpoints.
- Definir limites de payload.
- Preparar observabilidade mínima:
  - logs
  - erros
  - métricas básicas

### Dados

- Estratégia de migração da SQLite local.
- Estratégia para base remota quando houver sincronização.
- Política de backup e recuperação.
- Exportação simples para ficheiro.

### Deploy

- Rever `Dockerfile` para produção.
- Rever `render.yaml` quando a app estiver quase pronta.
- Definir variáveis de ambiente.
- Definir processo de release.
- Definir branch/release strategy.

## Android / Play Store

### Só começar quando a app estiver quase pronta

- Decidir abordagem Android:
  - PWA instalada no telemóvel
  - wrapper Android com WebView
  - app nativa mais tarde, se necessário
- Avaliar se PWA resolve o caso de uso real antes de investir em nativo.
- Preparar manifest, ícones e instalação mobile.
- Garantir offline básico.
- Garantir cache local de dados.
- Garantir sincronização quando a rede voltar.
- Testar performance em Android real.
- Ajustar UI para toque e visibilidade em supermercado.
- Preparar splash, nome final e branding.
- Criar política de privacidade.
- Criar assets da Play Store.
- Preparar assinatura e pipeline de release.

## Ideias futuras

- Login e sincronização cloud.
- Partilha familiar em tempo real.
- Sugestões inteligentes por histórico.
- OCR de talões.
- Leitura de código de barras.
- Integração com receitas e meal planning.
- Comparação de preços por loja.
- Modo offline-first completo.
- Notificações de reposição.

## Regra de execução daqui para a frente

- Continuar a implementar por ciclos curtos.
- Testar cedo e frequentemente.
- Commit e push regulares.
- Não investir tempo sério em Render/Docker antes da app estar madura.
- Não avançar para Android/Play Store antes de validar o produto no uso real.
